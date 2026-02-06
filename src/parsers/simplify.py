from typing import Optional
import re
from .base import BaseParser, Job


class SimplifyParser(BaseParser):
    """Parser for SimplifyJobs repositories"""

    def __init__(self, readme_url: str):
        super().__init__(source_name="simplify", readme_url=readme_url)
        self._text_pattern = re.compile(r'\[([^\]]+)\]')

    def parse_row(self, parts: list[str]) -> Optional[Job]:
        # Simplify table format may differ - needs verification
        # TODO: Verify actual Simplify table format and update
        if len(parts) < 5:
            return None

        company = self._extract_text(parts[0])
        title = self._extract_text(parts[1])
        location = parts[2]
        apply_link = self.extract_url(parts[1]) or ""
        date_posted = parts[4]

        return Job(
            company=company,
            title=title,
            location=location,
            apply_link=apply_link,
            date_posted=date_posted,
            source=self.source_name
        )

    def _extract_text(self, markdown: str) -> str:
        """Extract text from markdown link: **[Text](url)** -> Text"""
        match = self._text_pattern.search(markdown)
        return match.group(1) if match else markdown.strip("* ")
