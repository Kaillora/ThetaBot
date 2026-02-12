from typing import Optional
from .base import BaseParser, Job

class JobrightParser(BaseParser):
    def __init__(self, readme_url: str):
        super().__init__(source_name="jobright", readme_url=readme_url)

    def parse_row(self, parts: list[str]) -> Optional[Job]:
        if len(parts) < 5:
            return None

        company = self.extract_text(parts[0])
        title = self.extract_text(parts[1])
        location = parts[2].strip()
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

