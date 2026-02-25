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
        # ── Computer Science ──────────────────────────────────────────────────
        # Software Engineering
        'software engineer': 'Computer Science',
        'software developer': 'Computer Science',
        'software development': 'Computer Science',
        'software architect': 'Computer Science',
        'software toolchain': 'Computer Science',
        'software intern': 'Computer Science',
        'swe intern': 'Computer Science',
        'sde intern': 'Computer Science',
        'application developer': 'Computer Science',
        'application engineer': 'Computer Science',
        'api engineer': 'Computer Science',
        'api developer': 'Computer Science',
        'compiler engineer': 'Computer Science',
        'programming': 'Computer Science',
        'microservices': 'Computer Science',
        'distributed systems': 'Computer Science',
        # Web
        'full stack': 'Computer Science',
        'fullstack': 'Computer Science',
        'frontend': 'Computer Science',
        'front end': 'Computer Science',
        'front-end': 'Computer Science',
        'backend': 'Computer Science',
        'back end': 'Computer Science',
        'back-end': 'Computer Science',
        'web developer': 'Computer Science',
        'web dev': 'Computer Science',
        'web engineer': 'Computer Science',
        'web application': 'Computer Science',
        'react developer': 'Computer Science',
        'react engineer': 'Computer Science',
        'node.js': 'Computer Science',
        'javascript developer': 'Computer Science',
        'typescript developer': 'Computer Science',
        # Mobile
        'ios developer': 'Computer Science',
        'ios engineer': 'Computer Science',
        'android developer': 'Computer Science',
        'android engineer': 'Computer Science',
        'mobile developer': 'Computer Science',
        'mobile engineer': 'Computer Science',
        'react native': 'Computer Science',
        'flutter developer': 'Computer Science',
        # AI / ML
        'machine learning': 'Computer Science',
        'deep learning': 'Computer Science',
        'computer vision': 'Computer Science',
        'natural language processing': 'Computer Science',
        'large language model': 'Computer Science',
        'generative ai': 'Computer Science',
        'gen ai': 'Computer Science',
        'llm engineer': 'Computer Science',
        'ai/ml': 'Computer Science',
        'ml engineer': 'Computer Science',
        'ai engineer': 'Computer Science',
        'ai engineering': 'Computer Science',
        'artificial intelligence': 'Computer Science',
        'ai researcher': 'Computer Science',
        'nlp engineer': 'Computer Science',
        # Cloud / Infrastructure / DevOps
        'devops': 'Computer Science',
        'dev ops': 'Computer Science',
        'devsecops': 'Computer Science',
        'cloud engineer': 'Computer Science',
        'cloud architect': 'Computer Science',
        'cloud infrastructure': 'Computer Science',
        'cloud developer': 'Computer Science',
        'site reliability': 'Computer Science',
        'sre': 'Computer Science',
        'platform engineer': 'Computer Science',
        'infrastructure engineer': 'Computer Science',
        'kubernetes': 'Computer Science',
        'terraform': 'Computer Science',
        'solutions architect': 'Computer Science',
        'network engineer': 'Computer Science',
        'network administrator': 'Computer Science',
        'network operations': 'Computer Science',
        'noc engineer': 'Computer Science',
        # Systems / Embedded SW
        'systems software': 'Computer Science',
        'systems programmer': 'Computer Science',
        'kernel engineer': 'Computer Science',
        'operating systems': 'Computer Science',
        'embedded software': 'Computer Science',
        'embedded software engineer': 'Computer Science',
        # IT
        'information technology': 'Computer Science',
        'information systems': 'Computer Science',
        'it engineer': 'Computer Science',
        'it specialist': 'Computer Science',
        'it support engineer': 'Computer Science',
        'computer engineer': 'Computer Science',
        'integration engineer': 'Computer Science',
        'digital logic': 'Computer Science',
        # QA / Test (software)
        'qa engineer': 'Computer Science',
        'quality assurance engineer': 'Computer Science',
        'software test engineer': 'Computer Science',
        'software tester': 'Computer Science',
        'test automation': 'Computer Science',
        'sdet': 'Computer Science',
        # Game / Simulation
        'game engineer': 'Computer Science',
        'game developer': 'Computer Science',
        'graphics engineer': 'Computer Science',
        'rendering engineer': 'Computer Science',
        'simulation software': 'Computer Science',
        # Misc CS
        '5g software': 'Computer Science',
        'wireless research': 'Computer Science',
        'database engineer': 'Computer Science',
        'database developer': 'Computer Science',
        'data platform': 'Computer Science',

        # ── Electrical Engineering ────────────────────────────────────────────
        # Core
        'electrical engineer': 'Electrical Engineering',
        'electrical intern': 'Electrical Engineering',
        'electrical designer': 'Electrical Engineering',
        'electrical technician': 'Electrical Engineering',
        'electrical systems': 'Electrical Engineering',
        'electrical design': 'Electrical Engineering',
        # Power
        'power systems': 'Electrical Engineering',
        'power engineer': 'Electrical Engineering',
        'power generation': 'Electrical Engineering',
        'power electronics': 'Electrical Engineering',
        'power delivery': 'Electrical Engineering',
        'power distribution': 'Electrical Engineering',
        'transmission engineer': 'Electrical Engineering',
        'distribution engineer': 'Electrical Engineering',
        'utilities engineer': 'Electrical Engineering',
        'substation': 'Electrical Engineering',
        'grid engineer': 'Electrical Engineering',
        'smart grid': 'Electrical Engineering',
        'energy engineer': 'Electrical Engineering',
        'solar engineer': 'Electrical Engineering',
        'wind engineer': 'Electrical Engineering',
        'photovoltaic': 'Electrical Engineering',
        'battery engineer': 'Electrical Engineering',
        'battery management': 'Electrical Engineering',
        'bms engineer': 'Electrical Engineering',
        'ev engineer': 'Electrical Engineering',
        'electric vehicle engineer': 'Electrical Engineering',
        'motor engineer': 'Electrical Engineering',
        'motor control': 'Electrical Engineering',
        'drives engineer': 'Electrical Engineering',
        'generator technician': 'Electrical Engineering',
        'transformer engineer': 'Electrical Engineering',
        'relay engineer': 'Electrical Engineering',
        'protection engineer': 'Electrical Engineering',
        # Hardware / Circuit
        'hardware engineer': 'Electrical Engineering',
        'hardware design': 'Electrical Engineering',
        'hardware developer': 'Electrical Engineering',
        'circuit design': 'Electrical Engineering',
        'circuit engineer': 'Electrical Engineering',
        'circuit board': 'Electrical Engineering',
        'pcb': 'Electrical Engineering',
        'schematic': 'Electrical Engineering',
        'analog engineer': 'Electrical Engineering',
        'analog design': 'Electrical Engineering',
        'mixed-signal': 'Electrical Engineering',
        'mixed signal': 'Electrical Engineering',
        # Semiconductors / Chip
        'vlsi': 'Electrical Engineering',
        'semiconductor': 'Electrical Engineering',
        'ic design': 'Electrical Engineering',
        'chip design': 'Electrical Engineering',
        'asic': 'Electrical Engineering',
        'asic design': 'Electrical Engineering',
        'process engineer semiconductor': 'Electrical Engineering',
        # RF / Wireless HW
        'rf engineer': 'Electrical Engineering',
        'rf technician': 'Electrical Engineering',
        'rf designer': 'Electrical Engineering',
        'antenna': 'Electrical Engineering',
        'microwave engineer': 'Electrical Engineering',
        'radar engineer': 'Electrical Engineering',
        'wireless hardware': 'Electrical Engineering',
        'satellite engineer': 'Electrical Engineering',
        # Firmware
        'firmware': 'Electrical Engineering',
        'firmware engineer': 'Electrical Engineering',
        'firmware developer': 'Electrical Engineering',
        # Signal Processing
        'signal processing': 'Electrical Engineering',
        'dsp engineer': 'Electrical Engineering',
        'digital signal': 'Electrical Engineering',
        # Embedded HW
        'embedded systems': 'Electrical Engineering',
        'embedded engineer': 'Electrical Engineering',
        'embedded hardware': 'Electrical Engineering',
        'electronics': 'Electrical Engineering',
        'electronics engineer': 'Electrical Engineering',
        # FPGA / RTL
        'fpga': 'Electrical Engineering',
        'fpga engineer': 'Electrical Engineering',
        'rtl engineer': 'Electrical Engineering',
        'verilog': 'Electrical Engineering',
        'vhdl': 'Electrical Engineering',
        # Controls / Instrumentation
        'controls engineer': 'Electrical Engineering',
        'control systems engineer': 'Electrical Engineering',
        'plc engineer': 'Electrical Engineering',
        'plc programmer': 'Electrical Engineering',
        'instrumentation': 'Electrical Engineering',
        'test & measurement': 'Electrical Engineering',
        'measurement engineer': 'Electrical Engineering',
        'electromechanical': 'Electrical Engineering',
        # Avionics
        'avionics': 'Electrical Engineering',
        'avionics engineer': 'Electrical Engineering',
        'avionics technician': 'Electrical Engineering',

        # ── Mechanical Engineering ────────────────────────────────────────────
        # Core
        'mechanical engineer': 'Mechanical Engineering',
        'mechanical design': 'Mechanical Engineering',
        'mechanical designer': 'Mechanical Engineering',
        'mechanical intern': 'Mechanical Engineering',
        'mechanical technician': 'Mechanical Engineering',
        'mechatronics': 'Mechanical Engineering',
        # HVAC
        'hvac': 'Mechanical Engineering',
        'hvac engineer': 'Mechanical Engineering',
        'hvac technician': 'Mechanical Engineering',
        'mechanical systems': 'Mechanical Engineering',
        # Thermal / Fluids
        'thermodynamic': 'Mechanical Engineering',
        'heat transfer': 'Mechanical Engineering',
        'thermal engineer': 'Mechanical Engineering',
        'thermal analysis': 'Mechanical Engineering',
        'fluid dynamics': 'Mechanical Engineering',
        'cfd engineer': 'Mechanical Engineering',
        'computational fluid': 'Mechanical Engineering',
        'hydraulics engineer': 'Mechanical Engineering',
        'pneumatics': 'Mechanical Engineering',
        # Manufacturing
        'manufacturing engineer': 'Mechanical Engineering',
        'manufacturing technician': 'Mechanical Engineering',
        'process engineer': 'Mechanical Engineering',
        'production engineer': 'Mechanical Engineering',
        'industrial engineer': 'Mechanical Engineering',
        'lean engineer': 'Mechanical Engineering',
        'assembly engineer': 'Mechanical Engineering',
        'tooling engineer': 'Mechanical Engineering',
        'tool and die': 'Mechanical Engineering',
        'fixture design': 'Mechanical Engineering',
        'cnc': 'Mechanical Engineering',
        'cnc programmer': 'Mechanical Engineering',
        'cnc machinist': 'Mechanical Engineering',
        'fabrication': 'Mechanical Engineering',
        'fabrication engineer': 'Mechanical Engineering',
        'welding engineer': 'Mechanical Engineering',
        'sheet metal': 'Mechanical Engineering',
        'machine design': 'Mechanical Engineering',
        # Aerospace / Propulsion
        'aerospace engineer': 'Mechanical Engineering',
        'propulsion': 'Mechanical Engineering',
        'propulsion engineer': 'Mechanical Engineering',
        'spacecraft engineer': 'Mechanical Engineering',
        'launch vehicle': 'Mechanical Engineering',
        'gas turbine': 'Mechanical Engineering',
        'steam turbine': 'Mechanical Engineering',
        'turbine engineer': 'Mechanical Engineering',
        # Robotics
        'robotics engineer': 'Mechanical Engineering',
        'robotics technician': 'Mechanical Engineering',
        'robot programmer': 'Mechanical Engineering',
        'automation engineer': 'Mechanical Engineering',
        # CAD / Design
        'cad designer': 'Mechanical Engineering',
        'cad engineer': 'Mechanical Engineering',
        'cad technician': 'Mechanical Engineering',
        'solidworks': 'Mechanical Engineering',
        'catia': 'Mechanical Engineering',
        'siemens nx': 'Mechanical Engineering',
        'mechanical drafter': 'Mechanical Engineering',
        'design engineer': 'Mechanical Engineering',
        'product engineer': 'Mechanical Engineering',
        'product design engineer': 'Mechanical Engineering',
        # Materials
        'materials engineer': 'Mechanical Engineering',
        'metallurgist': 'Mechanical Engineering',
        'composites engineer': 'Mechanical Engineering',
        'materials scientist': 'Mechanical Engineering',
        # Structural (ME context)
        'stress engineer': 'Mechanical Engineering',
        'structural analysis': 'Mechanical Engineering',
        'fea engineer': 'Mechanical Engineering',
        'finite element': 'Mechanical Engineering',
        # Automotive
        'automotive engineer': 'Mechanical Engineering',
        'vehicle engineer': 'Mechanical Engineering',
        'powertrain engineer': 'Mechanical Engineering',
        'chassis engineer': 'Mechanical Engineering',
        'suspension engineer': 'Mechanical Engineering',
        'nvh engineer': 'Mechanical Engineering',
        # Piping
        'piping engineer': 'Mechanical Engineering',
        'pipe stress': 'Mechanical Engineering',
        'pipeline engineer': 'Mechanical Engineering',
        # Quality / Reliability
        'quality engineer': 'Mechanical Engineering',
        'reliability engineer': 'Mechanical Engineering',
        'mechanical test engineer': 'Mechanical Engineering',
        'hardware test engineer': 'Mechanical Engineering',
        'ndt engineer': 'Mechanical Engineering',
        'inspection engineer': 'Mechanical Engineering',
        'packaging engineer': 'Mechanical Engineering',

        # ── Civil Engineering ─────────────────────────────────────────────────
        # Core
        'civil engineer': 'Civil Engineering',
        'civil intern': 'Civil Engineering',
        'civil designer': 'Civil Engineering',
        'civil technician': 'Civil Engineering',
        # Structural
        'structural engineer': 'Civil Engineering',
        'structural analyst': 'Civil Engineering',
        'bridge engineer': 'Civil Engineering',
        'building engineer': 'Civil Engineering',
        'foundation engineer': 'Civil Engineering',
        # Geotechnical
        'geotechnical': 'Civil Engineering',
        'geotechnical engineer': 'Civil Engineering',
        'soil engineer': 'Civil Engineering',
        'soils': 'Civil Engineering',
        'geology engineer': 'Civil Engineering',
        # Transportation
        'transportation engineer': 'Civil Engineering',
        'traffic engineer': 'Civil Engineering',
        'highway engineer': 'Civil Engineering',
        'pavement engineer': 'Civil Engineering',
        'road engineer': 'Civil Engineering',
        # Water / Wastewater
        'water resources': 'Civil Engineering',
        'water/wastewater': 'Civil Engineering',
        'wastewater engineer': 'Civil Engineering',
        'water treatment': 'Civil Engineering',
        'hydrology': 'Civil Engineering',
        'hydraulic engineer': 'Civil Engineering',
        'hydraulic': 'Civil Engineering',
        'stormwater': 'Civil Engineering',
        'drainage engineer': 'Civil Engineering',
        'flood control': 'Civil Engineering',
        'coastal engineer': 'Civil Engineering',
        'dam engineer': 'Civil Engineering',
        'levee engineer': 'Civil Engineering',
        # Environmental
        'environmental engineer': 'Civil Engineering',
        'remediation engineer': 'Civil Engineering',
        'environmental scientist': 'Civil Engineering',
        'environmental consultant': 'Civil Engineering',
        # Survey
        'surveying': 'Civil Engineering',
        'surveyor': 'Civil Engineering',
        'survey intern': 'Civil Engineering',
        'land surveyor': 'Civil Engineering',
        'survey technician': 'Civil Engineering',
        # Construction
        'construction engineer': 'Civil Engineering',
        'construction manager': 'Civil Engineering',
        'construction project engineer': 'Civil Engineering',
        'site engineer': 'Civil Engineering',
        'site civil': 'Civil Engineering',
        # Land / Urban
        'land development': 'Civil Engineering',
        'subdivision engineer': 'Civil Engineering',
        'grading engineer': 'Civil Engineering',
        'site design': 'Civil Engineering',
        'urban planning': 'Civil Engineering',
        'city planner': 'Civil Engineering',
        'urban designer': 'Civil Engineering',
        'land use planner': 'Civil Engineering',
        # Materials / Inspection
        'materials testing': 'Civil Engineering',
        'special inspector': 'Civil Engineering',
        'geotechnical technician': 'Civil Engineering',
        'concrete testing': 'Civil Engineering',

        # ── Data Science ──────────────────────────────────────────────────────
        # Core
        'data scientist': 'Data Science',
        'data analyst': 'Data Science',
        'data engineer': 'Data Science',
        'data science': 'Data Science',
        'data analytics': 'Data Science',
        'data management': 'Data Science',
        'data mining': 'Data Science',
        # Analytics
        'analytics engineer': 'Data Science',
        'business intelligence': 'Data Science',
        'bi analyst': 'Data Science',
        'bi developer': 'Data Science',
        'business analyst': 'Data Science',
        'analytics intern': 'Data Science',
        'marketing analytics': 'Data Science',
        'sales analytics': 'Data Science',
        'operations analytics': 'Data Science',
        'product analyst': 'Data Science',
        'growth analyst': 'Data Science',
        'pricing analyst': 'Data Science',
        'supply chain analyst': 'Data Science',
        # Quantitative
        'quantitative analyst': 'Data Science',
        'quantitative researcher': 'Data Science',
        'quantitative developer': 'Data Science',
        'quant analyst': 'Data Science',
        'financial analyst': 'Data Science',
        'risk analyst': 'Data Science',
        'actuary': 'Data Science',
        'actuarial': 'Data Science',
        # Research / Statistics
        'research scientist': 'Data Science',
        'applied scientist': 'Data Science',
        'statistician': 'Data Science',
        'biostatistician': 'Data Science',
        'computational biologist': 'Data Science',
        'bioinformatics': 'Data Science',
        'operations research': 'Data Science',
        # ML (data focused)
        'machine learning engineer': 'Data Science',
        'nlp researcher': 'Data Science',
        # Visualization / Warehouse
        'data visualization': 'Data Science',
        'tableau developer': 'Data Science',
        'power bi developer': 'Data Science',
        'data warehouse': 'Data Science',
        'sql analyst': 'Data Science',
        'database analyst': 'Data Science',

        # ── Cybersecurity ─────────────────────────────────────────────────────
        # Core
        'cybersecurity': 'Cybersecurity',
        'cyber security': 'Cybersecurity',
        'information security': 'Cybersecurity',
        'infosec': 'Cybersecurity',
        # Offensive
        'penetration test': 'Cybersecurity',
        'pen tester': 'Cybersecurity',
        'red team': 'Cybersecurity',
        'ethical hacker': 'Cybersecurity',
        'exploit developer': 'Cybersecurity',
        'bug bounty': 'Cybersecurity',
        # Defensive
        'soc analyst': 'Cybersecurity',
        'security analyst': 'Cybersecurity',
        'blue team': 'Cybersecurity',
        'incident response': 'Cybersecurity',
        'digital forensics': 'Cybersecurity',
        'dfir': 'Cybersecurity',
        'threat intel': 'Cybersecurity',
        'threat hunter': 'Cybersecurity',
        'malware analyst': 'Cybersecurity',
        # Engineering
        'security engineer': 'Cybersecurity',
        'security architect': 'Cybersecurity',
        'security software': 'Cybersecurity',
        'application security': 'Cybersecurity',
        'appsec': 'Cybersecurity',
        'product security': 'Cybersecurity',
        'cloud security': 'Cybersecurity',
        'devsecops engineer': 'Cybersecurity',
        # Network Security
        'network security': 'Cybersecurity',
        'firewall engineer': 'Cybersecurity',
        'it security': 'Cybersecurity',
        # Compliance / GRC
        'grc analyst': 'Cybersecurity',
        'compliance analyst': 'Cybersecurity',
        'security auditor': 'Cybersecurity',
        'iam engineer': 'Cybersecurity',
        'identity and access': 'Cybersecurity',
        # Vulnerability
        'vulnerability': 'Cybersecurity',
        'vulnerability management': 'Cybersecurity',
        'patch management': 'Cybersecurity',
        # Misc
        'cryptographer': 'Cybersecurity',
        'security researcher': 'Cybersecurity',
        'security operations': 'Cybersecurity',
        'zero trust': 'Cybersecurity',
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
