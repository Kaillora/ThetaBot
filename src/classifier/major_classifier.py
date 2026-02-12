"""Zero-shot job title classification using Hugging Face Inference API"""
import requests
import time
from typing import Optional

from ..config import (
    HUGGINGFACE_TOKEN,
    CLASSIFICATION_CONFIDENCE_THRESHOLD,
    CLASSIFICATION_LABELS,
)

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"


class MajorClassifier:
    """Classifies job titles into college major categories via zero-shot NLI"""

    def __init__(self):
        if not HUGGINGFACE_TOKEN:
            raise ValueError("HUGGINGFACE_TOKEN not set in .env")
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        self.threshold = CLASSIFICATION_CONFIDENCE_THRESHOLD
        self.labels = CLASSIFICATION_LABELS

    def classify_job(self, title: str) -> Optional[str]:
        """Classify a single job title into a major category.

        Calls the HF zero-shot classification API with the job title
        and the configured labels. Returns the top label if its score
        meets the confidence threshold, otherwise None.

        Args:
            title: The job title string to classify

        Returns:
            The matched major label, or None if below threshold / error
        """
        # TODO(human): Implement this method
        # You have access to:
        #   self.headers  — dict with Authorization header for HF API
        #   self.labels   — list of candidate label strings
        #   self.threshold — minimum confidence score (float)
        #   API_URL       — the HF inference endpoint
        #
        # Expected behavior:
        #   1. POST to API_URL with JSON payload containing the title and candidate labels
        #   2. Parse the response JSON to get the top label and its score
        #   3. Return the label if score >= self.threshold, else None
        #   4. Handle errors: 503 (model loading) → retry after 20s,
        #      429 (rate limit) → exponential backoff, other errors → return None
        pass

    def classify_jobs(self, jobs) -> None:
        """Classify a list of Job objects in place, setting each job.category.

        Adds a 0.5s delay between API calls to respect rate limits.
        Skips jobs that already have a category set.

        Args:
            jobs: list of Job dataclass instances
        """
        for job in jobs:
            if job.category:
                continue
            try:
                job.category = self.classify_job(job.title)
            except Exception as e:
                print(f"[Classifier] Error classifying '{job.title}': {e}")
            time.sleep(0.5)
