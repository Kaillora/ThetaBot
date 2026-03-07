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
            "Each category corresponds to a college major:\n\n"
            "- Computer Science: software engineering, web development, cloud computing, "
            "DevOps, mobile, ML/AI, networking, platform, IT, QA, game development — "
            "roles primarily involving writing or deploying software\n"
            "- Electrical Engineering: hardware design, circuits, firmware, PCB design, power systems, "
            "RF, semiconductors, signal processing, FPGA, embedded systems, avionics\n"
            "- Mechanical Engineering: manufacturing engineering, CAD, aerospace structures, "
            "materials, robotics hardware, propulsion, thermal, fluid dynamics\n"
            "- Civil Engineering: structural, geotechnical, transportation, water resources, "
            "construction management, surveying, environmental engineering, urban planning\n"
            "- Data Science: data analysis, analytics, business intelligence, statistics, "
            "data engineering — industry/applied roles. Do NOT include academic research scientist "
            "roles focused on publishing research\n"
            "- Cybersecurity: security engineering, penetration testing, SOC analysis, "
            "threat intelligence, information security, AppSec. Do NOT include physical security, "
            "security guard, loss prevention, or armed/unarmed guard roles\n"
            "- General Engineering: roles that don't clearly fit any above category, "
            "non-technical security roles, and academic research roles\n\n"
            "Default rule: if a job title contains an engineering discipline name (e.g. 'Civil Engineer', "
            "'Electrical Engineer', 'Mechanical Engineer'), classify it into that category. "
            "Only use General Engineering when the title clearly does not match any category "
            "(e.g. Technician, Inspector, Laborer, Security Guard, or truly ambiguous roles)."
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