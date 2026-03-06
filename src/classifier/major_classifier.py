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
            "Each category corresponds to a college major:\n"
            "All roles must require a bachelor's degree or higher. If a role typically requires "
            "only a high school diploma, trade certification, or associate's degree, classify it "
            "as General Engineering regardless of the job title.\n\n"
            "- Computer Science: software engineering, web development, cloud computing, "
            "DevOps, mobile, ML/AI, networking, platform, IT, QA, game development — "
            "degree-level roles primarily involving writing or deploying software\n"
            "- Electrical Engineering: hardware design, circuits, firmware, PCB design, power systems, "
            "RF, semiconductors, signal processing, FPGA, embedded systems, avionics — "
            "degree-level engineering/design roles only, not technician or field service roles\n"
            "- Mechanical Engineering: manufacturing engineering, CAD, aerospace structures, "
            "materials, robotics hardware, propulsion, thermal, fluid dynamics — "
            "degree-level engineering/design roles only, not technician or field service roles\n"
            "- Civil Engineering: structural, geotechnical, transportation, water resources, "
            "construction management, surveying, environmental engineering, urban planning — "
            "degree-level roles only\n"
            "- Data Science: data analysis, analytics, business intelligence, statistics, "
            "data engineering — industry/applied degree-level roles only. Do NOT include academic "
            "research, research scientist, scientist, or roles focused on publishing research\n"
            "- Cybersecurity: security engineering, penetration testing, SOC analysis, "
            "threat intelligence, information security, AppSec — degree-level technical roles only. "
            "Do NOT include physical security, security guard, loss prevention, armed/unarmed guard, "
            "or any non-technical security role\n"
            "- General Engineering: anything that doesn't clearly fit the above, "
            "computer architecture/hardware-software co-design roles, roles requiring "
            "less than a bachelor's degree, trades/technician/field service roles, physical security "
            "roles, and academic research roles not focused on industry applications\n\n"
            "When a title is ambiguous, use the company and location for context. "
            "Hands-on field and technician roles are General Engineering even if the title contains "
            "an engineering discipline name. Research scientist roles are General Engineering unless "
            "clearly industry data/analytics at a tech or finance company."
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