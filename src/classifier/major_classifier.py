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
            "Each job must be assigned to exactly one category. "
            "Use the job title primarily, and company/location for context when ambiguous.\n\n"

            "=== TRADE/SERVICE OVERRIDE (check this first) ===\n"
            "Classify as General Engineering immediately — regardless of any other rule — "
            "if the title contains any of these words or phrases:\n"
            "Technician, Tech (e.g. 'Lube Tech', 'HVAC Tech'), Mechanic, Detailer, "
            "Inspector, Laborer, Installer, Apprentice, Helper, Operator, Assembler, "
            "Dispatcher, Field Service, Service Rep, Maintenance Worker, Groundskeeper, "
            "Security Guard, Loss Prevention, Armed/Unarmed Officer (non-engineering).\n"
            "Also always General Engineering: auto detailing, tire rotation/change, oil change, "
            "lube service, towing, HVAC service/repair, electrical trade work, plumbing, "
            "carpentry, welding (trade), masonry, janitorial, custodial.\n\n"

            "=== CATEGORIES ===\n\n"

            "COMPUTER SCIENCE\n"
            "Titles: Software Engineer, SWE, Developer, Programmer, Full Stack Engineer, "
            "Backend Engineer, Frontend Engineer, Web Developer, Mobile Engineer (iOS/Android), "
            "DevOps Engineer, Site Reliability Engineer (SRE), Cloud Engineer, Platform Engineer, "
            "ML Engineer, AI Engineer, AI Software Engineer, LLM Engineer, "
            "Data Engineer, QA Engineer, SDET, Test Automation Engineer, "
            "Systems Engineer (software context), Infrastructure Engineer, "
            "Network Engineer (software/cloud context), Game Developer, AR/VR Engineer, "
            "Database Engineer, DBA, IT Engineer, Solutions Architect, "
            "Application Security Engineer (AppSec), Compiler Engineer, OS/Kernel Engineer\n"
            "Keywords: software, code, programming, web, API, microservices, "
            "cloud (AWS/Azure/GCP), Kubernetes, Docker, CI/CD, DevOps, Linux, "
            "machine learning, deep learning, AI, LLM, NLP, computer vision, neural network, "
            "mobile app, iOS, Android, React, Node, Python (software context), "
            "algorithms, data structures, distributed systems, SaaS, backend, frontend\n\n"

            "ELECTRICAL ENGINEERING\n"
            "Titles: Electrical Engineer, Hardware Engineer, Circuit Design Engineer, "
            "PCB Design Engineer, Power Electronics Engineer, RF Engineer, "
            "Signal Processing Engineer, FPGA Engineer, ASIC Design Engineer, VLSI Engineer, "
            "Embedded Systems Engineer, Semiconductor Engineer, Process Engineer (semiconductor), "
            "Avionics Engineer, Photonics Engineer, Controls Engineer (electrical context), "
            "Power Systems Engineer, Hardware Test Engineer, IC Design Engineer, "
            "Analog/Digital Design Engineer, Battery Systems Engineer\n"
            "Keywords: PCB, schematic, circuit design, Verilog, VHDL, SystemVerilog, "
            "FPGA, ASIC, RTL, tape-out, power electronics, RF, antenna, radar, "
            "signal processing, DSP, semiconductor, fab, wafer, VLSI, "
            "embedded hardware, microcontroller, RTOS (hardware context), "
            "motor drives, inverters, converters, power grid, battery, BMS, "
            "electromagnetics, EMC, EMI, avionics, photonics, optics, lidar, "
            "analog design, oscilloscope, lab bench, voltage, current, impedance\n\n"

            "MECHANICAL ENGINEERING\n"
            "Titles: Mechanical Engineer, Mechanical Design Engineer, Design Engineer (mechanical), "
            "Aerospace Engineer, Structural Engineer (mechanical/aero context), "
            "Manufacturing Engineer, Process Engineer (manufacturing context), "
            "Product Design Engineer, Propulsion Engineer, Thermal Engineer, "
            "Fluids Engineer, CFD Engineer, Aerodynamics Engineer, Robotics Engineer (hardware/mechanical), "
            "Mechatronics Engineer, Materials Engineer, Materials Scientist (industry), "
            "Tooling Engineer, Packaging Engineer (structural), NVH Engineer, "
            "Dynamics Engineer, Acoustics Engineer, Systems Engineer (mechanical context), "
            "Automotive Engineer (design/R&D roles only)\n"
            "Keywords: CAD, SolidWorks, CATIA, NX, Creo, AutoCAD, Inventor, "
            "FEA, ANSYS, Abaqus, CFD, OpenFOAM, MATLAB (mechanical context), "
            "thermal analysis, heat transfer, thermodynamics, fluid dynamics, "
            "aerodynamics, propulsion, turbine, engine design, combustion, "
            "manufacturing process, tooling, GD&T, tolerancing, "
            "composites, materials testing, fatigue, stress analysis, "
            "robotics hardware, mechatronics, mechanical systems, kinematics, dynamics, "
            "vibration, acoustics, wind tunnel, injection molding, CNC (engineering context)\n\n"

            "CIVIL ENGINEERING\n"
            "Titles: Civil Engineer, Structural Engineer (civil context), Geotechnical Engineer, "
            "Transportation Engineer, Traffic Engineer, Water Resources Engineer, "
            "Environmental Engineer, Construction Engineer, Project Engineer (construction/infrastructure), "
            "Survey Engineer, Hydraulics Engineer, Coastal Engineer, Pavement Engineer, "
            "Bridge Engineer, Foundation Engineer, Urban Planner, Site Engineer, "
            "Land Development Engineer, Stormwater Engineer\n"
            "Keywords: structural analysis, foundation, soil mechanics, geotechnical, "
            "highway, roadway, bridge, infrastructure, drainage, stormwater, grading, "
            "water treatment, wastewater, hydrology, hydraulics, floodplain, "
            "construction management, land development, site civil, surveying, GIS (civil context), "
            "AASHTO, ACI, AISC, ASCE, environmental remediation, permitting, "
            "retaining wall, earthwork, utilities, septic, wetlands\n\n"

            "DATA SCIENCE\n"
            "Titles: Data Scientist, Data Analyst, Business Intelligence Analyst, BI Engineer, "
            "Analytics Engineer, Quantitative Analyst (quant), Statistician (industry), "
            "Applied Scientist (industry/tech company), Decision Scientist, "
            "Forecasting Analyst, Marketing Analyst, Product Analyst, "
            "Operations Research Analyst, Pricing Analyst, Risk Analyst (quantitative)\n"
            "Keywords: data analysis, statistical modeling, regression, classification, "
            "A/B testing, experimentation, SQL, Python (analytics context), R, "
            "Tableau, Power BI, Looker, dashboards, reporting, metrics, KPIs, "
            "business intelligence, forecasting, time series, clustering, "
            "ETL, data pipeline (analytics), Spark (analytics context), "
            "hypothesis testing, probability, Bayesian, predictive modeling\n"
            "Exclude: research scientists focused on publishing papers; pure software data engineering\n\n"

            "CYBERSECURITY\n"
            "Titles: Security Engineer, Security Analyst, Penetration Tester, "
            "Red Team Engineer, Blue Team Analyst, SOC Analyst, Threat Analyst, "
            "Malware Analyst, Incident Responder, Vulnerability Researcher, "
            "AppSec Engineer, Application Security Engineer, Cloud Security Engineer, "
            "IAM Engineer, Identity Engineer, Cryptography Engineer, "
            "GRC Analyst, Compliance Engineer (technical), Threat Hunter, "
            "Digital Forensics Analyst, OSINT Analyst\n"
            "Keywords: penetration testing, pen test, red team, blue team, SOC, SIEM, "
            "threat intelligence, incident response, vulnerability assessment, CVE, "
            "malware analysis, reverse engineering, exploit development, CTF, "
            "AppSec, OWASP, DAST, SAST, cloud security, IAM, zero trust, "
            "encryption, PKI, TLS, firewall, IDS, IPS, SOAR, MITRE ATT&CK, "
            "endpoint security, DLP, privileged access, deception technology\n"
            "Exclude: physical security guard, loss prevention, armed/unarmed security officer, "
            "facility security, executive protection (non-technical roles)\n\n"

            "GENERAL ENGINEERING\n"
            "Use for: roles that don't clearly fit any above category, "
            "chemical engineering, industrial engineering, biomedical/biomedical engineering, "
            "systems engineering (when field is ambiguous), operations/supply chain, "
            "project management (non-technical), academic research scientists, "
            "and any role caught by the trade/service override above.\n\n"

            "=== DEFAULT RULE ===\n"
            "If a title explicitly contains a discipline name "
            "('Civil Engineer', 'Electrical Engineer', 'Mechanical Engineer', "
            "'Software Engineer', 'Systems Engineer', etc.) classify it into that category "
            "unless the trade/service override applies. "
            "Use company and location for additional context on ambiguous titles."
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