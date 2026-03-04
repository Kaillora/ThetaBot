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

    def classify_jobs(self, jobs) -> None:
        """
        """

        to_api = [job for job in jobs if not job.category]
        if not to_api:
            return

        job_lines = "\n".join(
            f"{i + 1}. {job.title} at {job.company}"
            + (f" in {job.location}" if job.location else "")
            for i, job in enumerate(to_api)
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
            "- Computer Science: software engineering, web development, cloud computing, "
            "DevOps, mobile, ML/AI, networking, platform, IT, QA, game development, "
            "any role primarily involving writing or deploying software\n"
            "- Electrical Engineering: hardware, circuits, firmware, PCB design, power systems, "
            "RF, semiconductors, signal processing, FPGA, embedded systems, avionics\n"
            "- Mechanical Engineering: manufacturing, CAD, aerospace structures, HVAC, "
            "materials, robotics hardware, propulsion, thermal, fluid dynamics, CNC\n"
            "- Civil Engineering: structural, geotechnical, transportation, water resources, "
            "construction, surveying, environmental, urban planning\n"
            "- Data Science: data analysis, analytics, business intelligence, statistics, "
            "research science, data engineering\n"
            "- Cybersecurity: security engineering, penetration testing, SOC, "
            "threat intelligence, information security\n"
            "- General Engineering: roles that don't clearly fit any above category\n\n"
            "When a title is ambiguous, use the company and location for context. "
            "Software, cloud, and developer roles always belong to Computer Science."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            
            result = json.loads(response.choices[0].message.content)
            categories = result.get("categories", [])
            
            for job, category in zip(to_api, categories):
                if category in self.LABELS:
                    job.category = category
            
        except Exception as e:
            print(f"[Classifier] GPT classification failed: {e}")