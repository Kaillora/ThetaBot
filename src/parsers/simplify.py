from typing import Optional
import re
from .base import BaseParser, Job

class SimplifyParser(BaseParser):
    def __init__(self, readme_url: str):
        super().__init__(source_name="simplify", readme_url=readme_url)
        self._td_pattern = re.compile(r'<td.*?>(.*?)</td>', re.DOTALL)
        self._href_pattern = re.compile(r'href="(https?://[^"]+)"')

    def extract_rows(self, content: str) -> list[list[str]]:
        # Extract rows from HTML tables
        rows = []
        tr_blocks = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL)
        for block in tr_blocks:
            cells = self._td_pattern.findall(block)
            rows.append(cells)
        return rows
        
    def parse_row(self, parts: list[str]) -> Optional[Job]:
        if len(parts) < 5:
            return None

        company = self.extract_text(parts[0])
        title = self.extract_text(parts[1])
        location = parts[2].strip()
        apply_link = self._href_pattern.search(parts[3])
        apply_link = apply_link.group(1) if apply_link else ""
        date_posted = parts[4].strip()

        return Job(
            company=company,
            title=title,
            location=location,
            apply_link=apply_link,
            date_posted=date_posted,
            source=self.source_name
        )
