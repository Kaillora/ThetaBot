import json
from openai import OpenAI

from ..config import OPENAI_API_KEY, CLASSIFICATION_LABELS

class MajorClassifier:
    """Classifies job titles into college major categories via gpt-4o-mini"""

    LABELS = CLASSIFICATION_LABELS + ['General Engineering']
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    BATCH_SIZE = 25

    def _classify_batch(self, batch: list) -> None:
        """Classify a single batch of jobs (up to BATCH_SIZE) via GPT."""
        job_lines = "\n".join(
            f"{i + 1}. {job.title} at {job.company}"
            + (f" in {job.location}" if job.location else "")
            for i, job in enumerate(batch)
        )

        prompt = (
            f"Classify each job into one of the respective categories: "
            f"{', '.join(self.LABELS)}.\n\n"
            f"Return JSON: {{\"categories\": [\"category1\", \"category2\", ...]}}\n"
            f"in the same order as the jobs listed.\n\n"
            f"{job_lines}"
        )

        system_message = (
            "You are classifying job listings for an engineering college job board. "
            "Assign each job to exactly one category based on the job title. "
            "Use company and location only if the title is ambiguous.\n\n"

            "COMPUTER SCIENCE: Software/web/mobile development, DevOps, cloud, ML/AI, "
            "data engineering, QA/test automation, IT, infrastructure, game dev.\n\n"

            "ELECTRICAL ENGINEERING: Hardware design, PCB/circuit design, embedded systems, "
            "FPGA/ASIC, RF, power electronics, semiconductor, signal processing, avionics.\n\n"

            "MECHANICAL ENGINEERING: Mechanical/aerospace/manufacturing design, CAD, "
            "thermal/fluids/CFD, robotics hardware, materials, propulsion, automotive R&D.\n\n"

            "CIVIL ENGINEERING: Civil/structural/geotechnical/transportation/environmental "
            "engineering, construction, infrastructure, water resources, surveying.\n\n"

            "DATA SCIENCE: Data scientist, data analyst, BI analyst, quant analyst, "
            "applied scientist, analytics engineer, statistical modeling, forecasting.\n\n"

            "CYBERSECURITY: Security engineer/analyst, penetration tester, SOC analyst, "
            "incident response, AppSec, threat intelligence, vulnerability research.\n\n"

            "GENERAL ENGINEERING: Use only if the role doesn't fit any category above."
        )

        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            timeout=30,
        )

        result = json.loads(response.choices[0].message.content)
        categories = result.get("categories", [])

        for job, category in zip(batch, categories):
            if category in self.LABELS:
                job.category = category

    def classify_jobs(self, jobs) -> None:
        to_api = [job for job in jobs if not job.category]
        if not to_api:
            return

        for i in range(0, len(to_api), self.BATCH_SIZE):
            batch = to_api[i:i + self.BATCH_SIZE]
            try:
                self._classify_batch(batch)
            except Exception as e:
                print(f"[Classifier] GPT classification failed: {e}")