from dataclasses import dataclass, field
from typing import Optional
from datetime import date
from abc import ABC, abstractmethod
import requests
import re


@dataclass
class Job:
    # Represents a single job listing scraped from GitHub repos
    company: str
    title: str
    location: str
    apply_link: str
    date_posted: str
    source: str  # "jobright" or "simplify"
    category: Optional[str] = None  # Will be set by NLP classifier later

    @property
    def unique_id(self) -> str:
        #Generate a unique identifier to prevent duplicate posts
        return f"{self.company}|{self.title}|{self.location}"

    def __hash__(self):
        return hash(self.unique_id)

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False
        return self.unique_id == other.unique_id


class BaseParser(ABC):
    # Abstract base class for job listing parsers.
    # Subclasses must implement:
    #    - get_readme_url(): Returns the raw GitHub README URL
    #    - parse_row(parts: list[str]) -> Optional[Job]: Parses a table row into a Job
    
    
    def __init__(self, source_name: str, readme_url: str):
        self.source_name = source_name
        self.readme_url = readme_url
        self._link_pattern = re.compile(r'\((https?://.*?)\)')
        self._text_pattern = re.compile(r'\[([^\]]+)\]')
        self._html_tag_pattern = re.compile(r'<[^>]+>')

    def extract_text(self, text: str) -> str:
        # Extract plain text from markdown or HTML formatted string
        match = self._text_pattern.search(text)
        if match:
            return match.group(1)
        cleaned = self._html_tag_pattern.sub('', text).strip()
        return cleaned if cleaned else text.strip("*[]")

    def fetch_readme(self) -> Optional[str]:
        # Fetch the raw README content from GitHub
        try:
            response = requests.get(self.readme_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[{self.source_name}] Failed to fetch README: {e}")
            return None

    def extract_url(self, markdown_link: str) -> Optional[str]:
        # Extract URL from markdown link format
        match = self._link_pattern.search(markdown_link)
        return match.group(1) if match else None

    def extract_rows(self, content: str) -> list[list[str]]:
        rows = []
        for line in content.splitlines():
            line = line.strip()
            
            if not line.startswith("|") or "---" in line or "Company" in line:
                continue
            
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            
            rows.append(parts)
        return rows
    
    def parse_jobs(self) -> list[Job]:
        content = self.fetch_readme()
        if content is None:
            return []
        jobs = []
        for parts in self.extract_rows(content):
            job = self.parse_row(parts)
            if job is not None:
                jobs.append(job)
    
        return jobs
                    

    @abstractmethod
    def parse_row(self, parts: list[str]) -> Optional[Job]:
        # Parse a single table row into a Job object.
        # parts - List of cell values from a markdown table row
        # Returns 'Job' object if parsing successful, None if unsuccessful
        pass
