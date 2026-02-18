"""Zero-shot job title classification using Hugging Face Inference API"""
import requests
import time
from typing import Optional

from ..config import (
    HUGGINGFACE_TOKEN,
    CLASSIFICATION_CONFIDENCE_THRESHOLD,
    CLASSIFICATION_LABELS,
)

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

class MajorClassifier:
    """Classifies job titles into college major categories via zero-shot NLI"""

    def __init__(self):
        if not HUGGINGFACE_TOKEN:
            raise ValueError("HUGGINGFACE_TOKEN not set in .env")
        self.headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        self.threshold = CLASSIFICATION_CONFIDENCE_THRESHOLD
        self.labels = CLASSIFICATION_LABELS

    KEYWORD_MAP = {
        # Computer Science
        'software engineer': 'Computer Science',
        'software developer': 'Computer Science',
        'software development': 'Computer Science',
        'software toolchain': 'Computer Science',
        'full stack': 'Computer Science',
        'fullstack': 'Computer Science',
        'frontend': 'Computer Science',
        'front end': 'Computer Science',
        'front-end': 'Computer Science',
        'backend': 'Computer Science',
        'back end': 'Computer Science',
        'back-end': 'Computer Science',
        'web dev': 'Computer Science',
        'web engineer': 'Computer Science',
        'machine learning': 'Computer Science',
        'deep learning': 'Computer Science',
        'computer vision': 'Computer Science',
        'nlp': 'Computer Science',
        'devops': 'Computer Science',
        'dev ops': 'Computer Science',
        'cloud engineer': 'Computer Science',
        'cloud infrastructure': 'Computer Science',
        'site reliability': 'Computer Science',
        'ios developer': 'Computer Science',
        'android developer': 'Computer Science',
        'mobile developer': 'Computer Science',
        'mobile engineer': 'Computer Science',
        'embedded software': 'Computer Science',
        'ai/ml': 'Computer Science',
        'ml engineer': 'Computer Science',
        'ai engineer': 'Computer Science',
        'ai engineering': 'Computer Science',
        'artificial intelligence': 'Computer Science',
        'information technology': 'Computer Science',
        'information systems': 'Computer Science',
        'network engineer': 'Computer Science',
        'network operations': 'Computer Science',
        'platform engineer': 'Computer Science',
        'systems engineer': 'Computer Science',
        'systems software': 'Computer Science',
        'infrastructure engineer': 'Computer Science',
        'integration engineer': 'Computer Science',
        'digital logic': 'Computer Science',
        'computer engineer': 'Computer Science',
        'it engineer': 'Computer Science',
        'qa engineer': 'Computer Science',
        'quality assurance engineer': 'Computer Science',
        'test engineer': 'Computer Science',
        'automation engineer': 'Computer Science',
        'game engineer': 'Computer Science',
        'game developer': 'Computer Science',
        'simulation engineer': 'Computer Science',
        '5g': 'Computer Science',
        'wireless research': 'Computer Science',
        'product security': 'Computer Science',
        # Electrical Engineering
        'electrical engineer': 'Electrical Engineering',
        'power systems': 'Electrical Engineering',
        'power engineer': 'Electrical Engineering',
        'power generation': 'Electrical Engineering',
        'circuit': 'Electrical Engineering',
        'vlsi': 'Electrical Engineering',
        'semiconductor': 'Electrical Engineering',
        'pcb': 'Electrical Engineering',
        'antenna': 'Electrical Engineering',
        'rf engineer': 'Electrical Engineering',
        'rf technician': 'Electrical Engineering',
        'firmware': 'Electrical Engineering',
        'hardware engineer': 'Electrical Engineering',
        'signal processing': 'Electrical Engineering',
        'embedded systems': 'Electrical Engineering',
        'electronics': 'Electrical Engineering',
        'substation': 'Electrical Engineering',
        'grid engineer': 'Electrical Engineering',
        'field engineer': 'Electrical Engineering',
        'generator technician': 'Electrical Engineering',
        'avionics': 'Electrical Engineering',
        'controls engineer': 'Electrical Engineering',
        'instrumentation': 'Electrical Engineering',
        'ic design': 'Electrical Engineering',
        'fpga': 'Electrical Engineering',
        'motor control': 'Electrical Engineering',
        # Mechanical Engineering
        'mechanical engineer': 'Mechanical Engineering',
        'hvac': 'Mechanical Engineering',
        'thermodynamic': 'Mechanical Engineering',
        'manufacturing engineer': 'Mechanical Engineering',
        'turbine': 'Mechanical Engineering',
        'robotics': 'Mechanical Engineering',
        'cad designer': 'Mechanical Engineering',
        'cad engineer': 'Mechanical Engineering',
        'stress engineer': 'Mechanical Engineering',
        'materials engineer': 'Mechanical Engineering',
        'piping engineer': 'Mechanical Engineering',
        'design engineer': 'Mechanical Engineering',
        'product engineer': 'Mechanical Engineering',
        'aerospace engineer': 'Mechanical Engineering',
        'propulsion': 'Mechanical Engineering',
        'fluid dynamics': 'Mechanical Engineering',
        'thermal engineer': 'Mechanical Engineering',
        'manufacturing technician': 'Mechanical Engineering',
        'fabrication': 'Mechanical Engineering',
        'cnc': 'Mechanical Engineering',
        'tool and die': 'Mechanical Engineering',
        'quality engineer': 'Mechanical Engineering',
        'process engineer': 'Mechanical Engineering',
        'production engineer': 'Mechanical Engineering',
        'test engineer': 'Mechanical Engineering',
        'reliability engineer': 'Mechanical Engineering',
        'systems engineer': 'Mechanical Engineering',
        # Civil Engineering
        'civil engineer': 'Civil Engineering',
        'structural engineer': 'Civil Engineering',
        'geotechnical': 'Civil Engineering',
        'transportation engineer': 'Civil Engineering',
        'water resources': 'Civil Engineering',
        'water/wastewater': 'Civil Engineering',
        'wastewater engineer': 'Civil Engineering',
        'surveying': 'Civil Engineering',
        'survey intern': 'Civil Engineering',
        'construction engineer': 'Civil Engineering',
        'construction manager': 'Civil Engineering',
        'bridge engineer': 'Civil Engineering',
        'environmental engineer': 'Civil Engineering',
        'environmental test engineer': 'Civil Engineering',
        'site engineer': 'Civil Engineering',
        'land development': 'Civil Engineering',
        'urban planning': 'Civil Engineering',
        'hydraulic': 'Civil Engineering',
        'stormwater': 'Civil Engineering',
        'soils': 'Civil Engineering',
        'materials testing': 'Civil Engineering',
        'special inspector': 'Civil Engineering',
        # Data Science
        'data scientist': 'Data Science',
        'data analyst': 'Data Science',
        'data engineer': 'Data Science',
        'data management': 'Data Science',
        'analytics engineer': 'Data Science',
        'business intelligence': 'Data Science',
        'bi analyst': 'Data Science',
        'data science': 'Data Science',
        'quantitative analyst': 'Data Science',
        'research scientist': 'Data Science',
        'computational': 'Data Science',
        'machine learning engineer': 'Data Science',
        'statistician': 'Data Science',
        'analytics intern': 'Data Science',
        'marketing analytics': 'Data Science',
        'sales analytics': 'Data Science',
        'operations analytics': 'Data Science',
        # Cybersecurity
        'cybersecurity': 'Cybersecurity',
        'cyber security': 'Cybersecurity',
        'penetration test': 'Cybersecurity',
        'security analyst': 'Cybersecurity',
        'security engineer': 'Cybersecurity',
        'security software': 'Cybersecurity',
        'soc analyst': 'Cybersecurity',
        'information security': 'Cybersecurity',
        'threat intel': 'Cybersecurity',
        'it security': 'Cybersecurity',
        'network security': 'Cybersecurity',
        'application security': 'Cybersecurity',
        'cloud security': 'Cybersecurity',
        'vulnerability': 'Cybersecurity',
        'smart home security': 'Cybersecurity',
    }

    def classify_job(self, title: str, retries: int = 1) -> Optional[str]:
        """
        Calls the HF zero-shot classification API with the job title
        and the configured labels. Returns the top label if its score
        meets the confidence threshold, otherwise None.
        """

        title_lower = title.lower()
        for keyword, label in self.KEYWORD_MAP.items():
            if keyword in title_lower:
                return label

        try:
            
            response = requests.post(API_URL, headers=self.headers, json={"inputs": title, "parameters": {"candidate_labels": self.labels}})
            result = response.json()
            
            if response.status_code == 503:
                if retries > 0:
                    time.sleep(20)
                    return self.classify_job(title, retries - 1)
                return None
            elif response.status_code == 429:
                if retries > 0:
                    time.sleep(20)
                    return self.classify_job(title, retries - 1)
                return None
            elif response.status_code != 200:
                return None        
                
            top = result[0]

            if top["score"] >= self.threshold:
                return top["label"]
            else:
                return "General Engineering"
            
        except Exception:
            return None



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
