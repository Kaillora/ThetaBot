from typing import Optional
import re
from .base import BaseParser, Job


class JobrightParser(BaseParser):
    def __init__(self, readme_url: str):
        super().__init__(source_name="jobright", readme_url=readme_url)
        self._text_pattern = re.compile(r'\[([^\]]+)\]')

    def parse_row(self, parts: list[str]) -> Optional[Job]:
        # Jobright table: Company | Job Title | Location | Work Model | Date
        # Company format: **[Company Name](company_url)**
        # Job Title format: **[Job Title](apply_url)**
        if len(parts) < 5:
            return None

        company = self._extract_text(parts[0])
        title = self._extract_text(parts[1])
        apply_link = self.extract_url(parts[1]) or ""  # URL is in job title column
        location = parts[2]
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
    
parsers = [
    JobrightParser("https://raw.githubusercontent.com/jobright-ai/2026-Software-Engineer-Internship/refs/heads/master/README.md"),
    JobrightParser("https://raw.githubusercontent.com/jobright-ai/2026-Engineer-Internship/refs/heads/master/README.md"),
    JobrightParser("https://raw.githubusercontent.com/jobright-ai/2026-Software-Engineer-New-Grad/refs/heads/master/README.md"),
    JobrightParser("https://raw.githubusercontent.com/jobright-ai/2026-Engineering-New-Grad/refs/heads/master/README.md")
]

all_jobs = []
for parser in parsers:
    all_jobs.extend(parser.parse_jobs())