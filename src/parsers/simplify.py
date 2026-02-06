from typing import Optional
import re
from .base import BaseParser, Job

class SimplifyParser(BaseParser):
    def __init__(self, readme_url: str):
        super().__init__(source_name="simplify", readme_url=readme_url)
    
    def parse_row(self, parts: list[str]) -> Optional[Job]:
        if len(parts) < 5:
            return None
        
        company = self.extract_text(parts[0])
        title = parts[1]
        location = parts[2]
        apply_link = self.extract_url(parts[1]) or ""
        date_posted = parts[4]
        source = parts[5]
        
        return Job(
            company=company,
            title=title,
            location=location,
            apply_link=apply_link,
            date_posted=date_posted,
            source=self.source_name
        )                                                                               
    def _extract_text(self, markdown: str) -> str:
        match = self._text_pattern.search(markdown)
        return match.group(1) if match else markdown.strip("* ")

parsers = [
    SimplifyParser("https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/refs/heads/dev/README.md"),
    SimplifyParser("https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/refs/heads/dev/README.md"),

]

all_jobs = []
for parser in parsers:
    all_jobs.extend(parser.parse_jobs())