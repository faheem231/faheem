
"""
nlp_analyzer.py
───────────────
FIXED: has_fulltime bug corrected (any() → bool())
"""

import re

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

SKILL_TAXONOMY = {
    "AI/ML": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "nlp", "natural language processing", "computer vision", "neural networks",
        "transformers", "large language models", "llm", "ai", "artificial intelligence",
        "reinforcement learning", "scikit-learn", "huggingface", "opencv", "bert", "gpt",
        "gan", "diffusion models", "mlops", "langchain", "vector database"
    ],
    "Data Science": [
        "python", "r", "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
        "sql", "tableau", "power bi", "statistics", "data visualization",
        "natural language processing", "nlp", "computer vision", "spark",
        "hadoop", "big data", "feature engineering", "regression", "classification",
        "clustering", "neural network", "random forest", "xgboost", "lightgbm",
        "jupyter", "data analysis", "data mining", "etl", "airflow", "mlops",
    ],
    "Web Development": [
        "html", "css", "javascript", "typescript", "react", "angular", "vue",
        "node.js", "express", "django", "flask", "fastapi", "rest api", "graphql",
        "mongodb", "postgresql", "mysql", "redis", "docker", "kubernetes",
        "git", "github", "ci/cd", "tailwind", "bootstrap", "sass", "webpack",
        "next.js", "nuxt", "svelte", "php", "laravel", "wordpress", "aws",
        "azure", "gcp", "linux", "nginx", "apache",
    ],
    "Finance": [
        "excel", "financial analysis", "accounting", "budgeting", "forecasting",
        "valuation", "dcf", "financial modeling", "bloomberg", "vba", "sql",
        "risk management", "portfolio management", "derivatives", "equity",
        "fixed income", "investment banking", "corporate finance", "audit",
        "cfa", "frm", "quickbooks", "sap", "oracle financials", "tableau",
    ],
    "Cybersecurity": [
        "network security", "penetration testing", "ethical hacking", "siem",
        "firewall", "ids", "ips", "vulnerability assessment", "kali linux",
        "metasploit", "wireshark", "nmap", "burp suite", "cryptography",
        "compliance", "iso 27001", "soc 2", "cissp", "ceh", "security+",
        "incident response", "threat intelligence", "malware analysis",
    ],
    "Mobile Development": [
        "android", "ios", "swift", "kotlin", "java", "react native", "flutter",
        "dart", "xcode", "android studio", "firebase", "rest api", "mvvm",
        "mvc", "ui/ux", "objective-c", "mobile testing", "appstore",
    ],
    "DevOps": [
        "docker", "kubernetes", "jenkins", "ansible", "terraform", "puppet",
        "chef", "ci/cd", "git", "linux", "bash", "python", "monitoring",
        "prometheus", "grafana", "elk stack", "aws", "azure", "gcp",
        "infrastructure as code", "helm", "argo cd",
    ],
}

ALL_SKILLS = sorted(set(s for skills in SKILL_TAXONOMY.values() for s in skills), key=len, reverse=True)

CERT_SUGGESTIONS = {
    "AI/ML": [
        {
            "name": "Machine Learning Specialization",
            "provider": "DeepLearning.AI",
            "difficulty": "Beginner",
            "duration": "8 Weeks",
            "price_type": "Paid",
            "ats_boost": 15,
            "url": "https://www.coursera.org/specializations/machine-learning-introduction",
            "skills": ["Python", "Machine Learning", "Regression", "Supervised Learning"],
            "indicator": "Trending in 2026"
        },
        {
            "name": "Deep Learning Specialization",
            "provider": "DeepLearning.AI",
            "difficulty": "Intermediate",
            "duration": "12 Weeks",
            "price_type": "Paid",
            "ats_boost": 18,
            "url": "https://www.coursera.org/specializations/deep-learning",
            "skills": ["Deep Learning", "Neural Networks", "TensorFlow", "PyTorch", "NLP"],
            "indicator": "High ATS Value"
        },
        {
            "name": "AWS Certified Machine Learning - Specialty",
            "provider": "AWS",
            "difficulty": "Advanced",
            "duration": "3 Months",
            "price_type": "Paid",
            "ats_boost": 22,
            "url": "https://aws.amazon.com/certification/certified-machine-learning-specialty/",
            "skills": ["AWS", "MLOps", "SageMaker", "Machine Learning", "Cloud Architecture"],
            "indicator": "Boosts Cloud Resume Ranking"
        },
        {
            "name": "TensorFlow Developer Professional Certificate",
            "provider": "DeepLearning.AI",
            "difficulty": "Intermediate",
            "duration": "3 Months",
            "price_type": "Paid",
            "ats_boost": 16,
            "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice",
            "skills": ["TensorFlow", "Deep Learning", "Computer Vision", "NLP"],
            "indicator": "Trending in 2026"
        },
        {
            "name": "Introduction to Generative AI",
            "provider": "Google",
            "difficulty": "Beginner",
            "duration": "1 Day",
            "price_type": "Free",
            "ats_boost": 8,
            "url": "https://www.cloudskillsboost.google/course_templates/539",
            "skills": ["Generative AI", "LLMs", "Google Cloud", "AI"],
            "indicator": "Free Official Course"
        },
        {
            "name": "Deep Reinforcement Learning Class",
            "provider": "DeepLearning.AI",
            "difficulty": "Intermediate",
            "duration": "4 Weeks",
            "price_type": "Free",
            "ats_boost": 12,
            "url": "https://huggingface.co/learn/deep-rl-course/unit0/introduction",
            "skills": ["Reinforcement Learning", "PyTorch", "Hugging Face", "Machine Learning"],
            "indicator": "100% Free & Open Source"
        },
        {
            "name": "NPTEL: Artificial Intelligence Search Methods",
            "provider": "NPTEL",
            "difficulty": "Intermediate",
            "duration": "8 Weeks",
            "price_type": "Free",
            "ats_boost": 9,
            "url": "https://onlinecourses.nptel.ac.in/noc23_cs124/preview",
            "skills": ["Artificial Intelligence", "Algorithms", "Problem Solving", "AI"],
            "indicator": "Academic Rigor Favorite"
        }
    ],
    "Data Science": [
        {
            "name": "Google Cloud Professional Data Engineer",
            "provider": "Google",
            "difficulty": "Advanced",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 20,
            "url": "https://cloud.google.com/learn/certification/data-engineer",
            "skills": ["Google Cloud", "BigQuery", "ETL", "Big Data"],
            "indicator": "Frequently Required by Recruiters"
        },
        {
            "name": "IBM Data Science Professional Certificate",
            "provider": "IBM",
            "difficulty": "Beginner",
            "duration": "5 Months",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://www.coursera.org/professional-certificates/ibm-data-science",
            "skills": ["Python", "SQL", "Data Analysis", "Data Visualization"],
            "indicator": "High ATS Value"
        },
        {
            "name": "NPTEL: Deep Learning",
            "provider": "NPTEL",
            "difficulty": "Intermediate",
            "duration": "12 Weeks",
            "price_type": "Free",
            "ats_boost": 10,
            "url": "https://onlinecourses.nptel.ac.in/noc23_cs122/preview",
            "skills": ["Deep Learning", "PyTorch", "CNN", "RNN"],
            "indicator": "Academic & Research Favorite"
        },
        {
            "name": "Kaggle: Machine Learning Courses",
            "provider": "Google",
            "difficulty": "Beginner",
            "duration": "2 Weeks",
            "price_type": "Free",
            "ats_boost": 8,
            "url": "https://www.kaggle.com/learn",
            "skills": ["Python", "Pandas", "Machine Learning", "Data Visualization"],
            "indicator": "Free Interactive Labs"
        },
        {
            "name": "NPTEL: Data Science for Engineers",
            "provider": "NPTEL",
            "difficulty": "Intermediate",
            "duration": "8 Weeks",
            "price_type": "Free",
            "ats_boost": 10,
            "url": "https://onlinecourses.nptel.ac.in/noc23_cs115/preview",
            "skills": ["Data Science", "R", "Python", "Linear Algebra"],
            "indicator": "Free Course"
        },
        {
            "name": "Microsoft Certified: Azure Data Scientist Associate",
            "provider": "Microsoft Learn",
            "difficulty": "Intermediate",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 15,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-data-scientist/",
            "skills": ["Azure", "Machine Learning", "Data Science", "MLOps"],
            "indicator": "High ATS Value"
        }
    ],
    "Web Development": [
        {
            "name": "Meta Front-End Developer Professional Certificate",
            "provider": "Meta",
            "difficulty": "Beginner",
            "duration": "7 Months",
            "price_type": "Paid",
            "ats_boost": 14,
            "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer",
            "skills": ["React", "JavaScript", "HTML", "CSS", "UI/UX"],
            "indicator": "Frequently Required by Recruiters"
        },
        {
            "name": "Meta Back-End Developer Professional Certificate",
            "provider": "Meta",
            "difficulty": "Beginner",
            "duration": "8 Months",
            "price_type": "Paid",
            "ats_boost": 15,
            "url": "https://www.coursera.org/professional-certificates/meta-back-end-developer",
            "skills": ["Python", "Django", "SQL", "APIs", "Git"],
            "indicator": "Trending in 2026"
        },
        {
            "name": "AWS Certified Developer - Associate",
            "provider": "AWS",
            "difficulty": "Intermediate",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 18,
            "url": "https://aws.amazon.com/certification/certified-developer-associate/",
            "skills": ["AWS", "Cloud Development", "Serverless", "DynamoDB"],
            "indicator": "Frequently Required by Recruiters"
        },
        {
            "name": "Microsoft Certified: Azure Developer Associate",
            "provider": "Microsoft Learn",
            "difficulty": "Intermediate",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 16,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/azure-developer/",
            "skills": ["Azure", "Cloud Development", "Security", "Optimization"],
            "indicator": "High ATS Value"
        },
        {
            "name": "Web Design Specialization",
            "provider": "Coursera",
            "difficulty": "Beginner",
            "duration": "3 Months",
            "price_type": "Free",
            "ats_boost": 10,
            "url": "https://www.coursera.org/specializations/web-design",
            "skills": ["HTML", "CSS", "JavaScript", "Responsive Design"],
            "indicator": "Free Audit Available"
        },
        {
            "name": "Microsoft Certified: Power Platform App Maker",
            "provider": "Microsoft Learn",
            "difficulty": "Beginner",
            "duration": "4 Weeks",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/power-platform-app-maker/",
            "skills": ["Low Code", "PowerApps", "Cloud Flows"],
            "indicator": "Enterprise Favorite"
        },
        {
            "name": "The Complete JavaScript Course 2026",
            "provider": "Udemy",
            "difficulty": "Beginner",
            "duration": "6 Weeks",
            "price_type": "Paid",
            "ats_boost": 11,
            "url": "https://www.udemy.com/course/the-complete-javascript-course/",
            "skills": ["JavaScript", "ES6", "OOP", "Web APIs"],
            "indicator": "Highest Rated Udemy Course"
        }
    ],
    "DevOps": [
        {
            "name": "CKA: Certified Kubernetes Administrator",
            "provider": "Google",
            "difficulty": "Advanced",
            "duration": "6 Weeks",
            "price_type": "Paid",
            "ats_boost": 25,
            "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/",
            "skills": ["Kubernetes", "Docker", "Containers", "DevOps"],
            "indicator": "High ATS Value"
        },
        {
            "name": "Docker & Kubernetes: The Complete Guide",
            "provider": "Udemy",
            "difficulty": "Intermediate",
            "duration": "3 Weeks",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
            "skills": ["Docker", "Kubernetes", "CI/CD", "Containers"],
            "indicator": "Practical Hands-on Guide"
        },
        {
            "name": "HashiCorp Certified: Terraform Associate",
            "provider": "AWS",
            "difficulty": "Intermediate",
            "duration": "4 Weeks",
            "price_type": "Paid",
            "ats_boost": 15,
            "url": "https://www.hashicorp.com/certification/terraform-associate",
            "skills": ["Terraform", "Infrastructure as Code", "AWS", "CI/CD"],
            "indicator": "Trending in 2026"
        },
        {
            "name": "AWS Certified SysOps Administrator - Associate",
            "provider": "AWS",
            "difficulty": "Intermediate",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 18,
            "url": "https://aws.amazon.com/certification/certified-sysops-admin-associate/",
            "skills": ["AWS", "SysOps", "Monitoring", "CloudFormation"],
            "indicator": "Frequently Required by Recruiters"
        },
        {
            "name": "Introduction to DevOps and Software Engineering",
            "provider": "IBM",
            "difficulty": "Beginner",
            "duration": "4 Weeks",
            "price_type": "Free",
            "ats_boost": 12,
            "url": "https://www.coursera.org/learn/intro-devops-software-engineering",
            "skills": ["DevOps", "CI/CD", "Agile", "Cloud Native"],
            "indicator": "Free Audit Available"
        },
        {
            "name": "NPTEL: Cloud Computing",
            "provider": "NPTEL",
            "difficulty": "Beginner",
            "duration": "12 Weeks",
            "price_type": "Free",
            "ats_boost": 10,
            "url": "https://onlinecourses.nptel.ac.in/noc23_cs119/preview",
            "skills": ["Cloud Computing", "Virtualization", "Containers"],
            "indicator": "Academic Credit Favorite"
        }
    ],
    "Cybersecurity": [
        {
            "name": "Google Cybersecurity Professional Certificate",
            "provider": "Google",
            "difficulty": "Beginner",
            "duration": "6 Months",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
            "skills": ["Linux", "Python", "SQL", "Network Security", "SIEM"],
            "indicator": "High ATS Value"
        },
        {
            "name": "CompTIA Security+",
            "provider": "Cisco",
            "difficulty": "Intermediate",
            "duration": "8 Weeks",
            "price_type": "Paid",
            "ats_boost": 18,
            "url": "https://www.comptia.org/certifications/security",
            "skills": ["Network Security", "Cryptography", "Identity Management", "Security"],
            "indicator": "Frequently Required by Recruiters"
        },
        {
            "name": "CEH: Certified Ethical Hacker",
            "provider": "Cisco",
            "difficulty": "Intermediate",
            "duration": "3 Months",
            "price_type": "Paid",
            "ats_boost": 20,
            "url": "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/",
            "skills": ["Ethical Hacking", "Penetration Testing", "Vulnerabilities"],
            "indicator": "High ATS Value"
        },
        {
            "name": "CISSP: Certified Information Systems Security Professional",
            "provider": "Cisco",
            "difficulty": "Advanced",
            "duration": "4 Months",
            "price_type": "Paid",
            "ats_boost": 28,
            "url": "https://www.isc2.org/certifications/cissp",
            "skills": ["Security Management", "Architecture", "Network Security"],
            "indicator": "Industry Gold Standard"
        },
        {
            "name": "Cisco: Cybersecurity Essentials",
            "provider": "Cisco",
            "difficulty": "Beginner",
            "duration": "30 Hours",
            "price_type": "Free",
            "ats_boost": 11,
            "url": "https://www.netacad.com/courses/cybersecurity/cybersecurity-essentials",
            "skills": ["Network Security", "Cybersecurity", "Cryptography"],
            "indicator": "100% Free Official Course"
        },
        {
            "name": "Microsoft Certified: Security Fundamentals SC-900",
            "provider": "Microsoft Learn",
            "difficulty": "Beginner",
            "duration": "2 Weeks",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://learn.microsoft.com/en-us/credentials/certifications/security-compliance-and-identity-fundamentals/",
            "skills": ["Azure Security", "Active Directory", "Compliance"],
            "indicator": "Recruiter Favorite"
        },
        {
            "name": "NPTEL: Cryptography and Network Security",
            "provider": "NPTEL",
            "difficulty": "Advanced",
            "duration": "12 Weeks",
            "price_type": "Free",
            "ats_boost": 12,
            "url": "https://onlinecourses.nptel.ac.in/noc23_cs126/preview",
            "skills": ["Cryptography", "Network Security", "Mathematics"],
            "indicator": "Advanced Theory"
        }
    ],
    "Mobile Development": [
        {
            "name": "Google Associate Android Developer",
            "provider": "Google",
            "difficulty": "Intermediate",
            "duration": "2 Months",
            "price_type": "Paid",
            "ats_boost": 15,
            "url": "https://developers.google.com/certification/associate-android-developer",
            "skills": ["Kotlin", "Android Studio", "Android Jetpack", "Mobile Development"],
            "indicator": "Official Google Standard"
        },
        {
            "name": "Meta iOS Developer Professional Certificate",
            "provider": "Meta",
            "difficulty": "Beginner",
            "duration": "8 Months",
            "price_type": "Paid",
            "ats_boost": 14,
            "url": "https://www.coursera.org/professional-certificates/meta-ios-developer",
            "skills": ["Swift", "iOS Development", "Xcode", "Mobile Development"],
            "indicator": "Trending in 2026"
        }
    ],
    "Finance": [
        {
            "name": "Chartered Financial Analyst (CFA)",
            "provider": "Oracle",
            "difficulty": "Advanced",
            "duration": "1 Year",
            "price_type": "Paid",
            "ats_boost": 30,
            "url": "https://www.cfainstitute.org/en/programs/cfa",
            "skills": ["Financial Analysis", "Portfolio Management", "Valuation", "Finance"],
            "indicator": "Gold Standard in Finance"
        },
        {
            "name": "Bloomberg Market Concepts (BMC)",
            "provider": "IBM",
            "difficulty": "Beginner",
            "duration": "8 Hours",
            "price_type": "Paid",
            "ats_boost": 10,
            "url": "https://www.bloomberg.com/professional/product/bloomberg-market-concepts/",
            "skills": ["Bloomberg Terminal", "Equities", "Fixed Income", "Economics"],
            "indicator": "Recruiter Favorite"
        },
        {
            "name": "Oracle Financials Cloud General Ledger Specialist",
            "provider": "Oracle",
            "difficulty": "Advanced",
            "duration": "6 Weeks",
            "price_type": "Paid",
            "ats_boost": 18,
            "url": "https://education.oracle.com/oracle-financials-cloud-general-ledger-2023-implementation-professional/pexam_1Z0-1054-23",
            "skills": ["Oracle ERP", "Financial Accounting", "General Ledger"],
            "indicator": "High ATS Value"
        }
    ],
    "General": [
        {
            "name": "AWS Certified Cloud Practitioner",
            "provider": "AWS",
            "difficulty": "Beginner",
            "duration": "4 Weeks",
            "price_type": "Paid",
            "ats_boost": 12,
            "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
            "skills": ["AWS", "Cloud Computing", "Cloud Architecture"],
            "indicator": "Boosts Cloud Resume Ranking"
        },
        {
            "name": "Google IT Support Professional Certificate",
            "provider": "Google",
            "difficulty": "Beginner",
            "duration": "6 Months",
            "price_type": "Paid",
            "ats_boost": 10,
            "url": "https://www.coursera.org/professional-certificates/google-it-support",
            "skills": ["IT Support", "Operating Systems", "Networking", "Security"],
            "indicator": "Recruiter Favorite"
        }
    ]
}

DEGREE_PATTERNS = [
    r"\b(B\.?S\.?|B\.?E\.?|B\.?Tech\.?|Bachelor(?:\'s)?(?:\s+of\s+\w+)?)\b",
    r"\b(M\.?S\.?|M\.?E\.?|M\.?Tech\.?|Master(?:\'s)?(?:\s+of\s+\w+)?|MBA)\b",
    r"\b(Ph\.?D\.?|Doctorate|Doctoral)\b",
    r"\b(Associate(?:\'s)?\s+(?:Degree|of\s+\w+))\b",
    r"\b(Diploma|Certificate|High\s+School|Secondary|HSC|SSC|10th|12th)\b",
]

COMMON_SECTIONS = [
    "education", "experience", "skills", "projects", "certifications",
    "summary", "objective", "publications", "awards", "languages",
    "volunteer", "internship", "achievements", "interests",
]


# ── University Extraction ─────────────────────────────────────
def extract_university(text: str) -> str:
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(kw in lower for kw in [
            "university", "institute of technology", "college of engineering",
            "institute", "college", "iit", "nit", "iiit", "bits", "vtu",
            "deemed university", "academy"
        ]):
            if 3 <= len(line.split()) <= 12 and len(line) < 100:
                return line.strip()

    patterns = [
        r'([A-Z][A-Za-z\s&,\.]+(?:University|Institute of Technology|College of Engineering|College|Institute|Academy))',
        r'(University of [A-Z][A-Za-z\s&,\.]+)',
        r'(Indian Institute of [A-Za-z\s]+)',
        r'\b((?:IIT|NIT|IIIT|BITS|VIT|SRM|PES|RVCE|BMSCE|MSRIT|NMIT|CMRIT|DBIT|ATRIA)[A-Za-z\s,\.]*)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            uni = match.strip().rstrip(",.")
            if 1 <= len(uni.split()) <= 10:
                return uni

    if SPACY_AVAILABLE:
        try:
            doc = nlp(text[:3000])
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    if any(w in ent.text.lower() for w in ["university", "college", "institute", "iit", "nit"]):
                        return ent.text.strip()
        except Exception:
            pass

    return ""


# ── Public API ────────────────────────────────────────────────
def analyze_resume(text: str) -> dict:
    text_lower = text.lower()

    skills     = extract_skills(text_lower)
    education  = extract_education(text)
    university = extract_university(text)
    experience = extract_experience(text)
    domain     = detect_domain(text_lower, skills)
    missing_kw = get_missing_keywords(text_lower, domain)
    certs      = CERT_SUGGESTIONS.get(domain, CERT_SUGGESTIONS["General"])

    ats_score, breakdown = calculate_ats_score(text, text_lower, skills, education, experience)
    suggestions = generate_suggestions(text_lower, skills, education, experience, ats_score)

    return {
        "skills":          skills,
        "education":       education,
        "university":      university,
        "experience":      experience,
        "domain":          domain,
        "ats_score":       ats_score,
        "score_breakdown": breakdown,
        "missing_keywords":missing_kw,
        "suggestions":     suggestions,
        "certifications":  certs,
    }


def extract_skills(text_lower: str) -> list:
    found = set()
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill.title())
    return sorted(found)


def extract_education(text: str) -> list:
    found = []
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            degree = m.strip()
            if degree and degree not in found:
                found.append(degree)
    return found


def extract_experience(text: str) -> list:
    patterns = [
        r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s+years?\s+(?:of\s+)?(?:work|professional|industry)',
        r'experience\s+of\s+(\d+)\+?\s+years?',
    ]
    found = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            entry = f"{m}+ years of experience"
            if entry not in found:
                found.append(entry)

    if re.findall(r'(intern|internship|trainee|apprentice)', text, re.IGNORECASE) and not found:
        found.append("Internship experience")

    job_patterns = [r'(developer|engineer|analyst|designer|manager|consultant|architect)']
    for p in job_patterns:
        if re.search(p, text, re.IGNORECASE) and not found:
            found.append("Professional experience")
            break

    return found


def detect_domain(text_lower: str, skills: list) -> str:
    skills_lower = [s.lower() for s in skills]
    scores = {}
    for domain, domain_skills in SKILL_TAXONOMY.items():
        count = sum(1 for s in domain_skills if s in skills_lower)
        scores[domain] = count
    best_domain = max(scores, key=scores.get)
    return best_domain if scores[best_domain] > 0 else "General"


def get_missing_keywords(text_lower: str, domain: str) -> list:
    domain_skills = SKILL_TAXONOMY.get(domain, ALL_SKILLS)
    missing = []
    for skill in domain_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if not re.search(pattern, text_lower):
            missing.append(skill.title())
        if len(missing) >= 10:
            break
    return missing


def calculate_ats_score(text: str, text_lower: str, skills: list,
                         education: list, experience: list):

    # ── 1. Skills (max 30) ────────────────────────────────────
    skill_pts = round(min(len(skills) / 15, 1.0) * 30, 1)

    # ── 2. Education (max 20) ─────────────────────────────────
    if education:
        edu_pts = 20
    elif any(w in text_lower for w in ["studying", "pursuing", "undergraduate"]):
        edu_pts = 10
    else:
        edu_pts = 0

    # ── 3. Experience (max 20) ────────────────────────────────
    # ✅ FIXED: bool() instead of any() on single re.search result
    has_fulltime = bool(re.search(r'(\d+)\+?\s+years?\s+(?:of\s+)?experience', text, re.IGNORECASE))
    has_intern   = bool(re.search(r'intern|internship|trainee', text, re.IGNORECASE))
    has_projects = bool(re.search(r'project|built|developed|created', text, re.IGNORECASE))

    if has_fulltime:
        exp_pts = 20
    elif has_intern:
        exp_pts = 12
    elif has_projects:
        exp_pts = 6
    else:
        exp_pts = 0

    # ── 4. Formatting / Sections (max 15) ─────────────────────
    sections_found = sum(1 for s in COMMON_SECTIONS if s in text_lower)
    fmt_pts = round(min(sections_found / 7, 1.0) * 15, 1)

    # ── 5. Bonus (max 15) ─────────────────────────────────────
    cert_bonus    = 3 if any(w in text_lower for w in ["certification", "certified", "certificate"]) else 0
    achieve_bonus = 3 if any(w in text_lower for w in ["achievement", "award", "winner", "rank", "hackathon"]) else 0
    links_bonus   = 3 if any(w in text_lower for w in ["github", "linkedin", "portfolio"]) else 0
    length_bonus  = 3 if len(text_lower.split()) >= 300 else 0
    summary_bonus = 3 if any(w in text_lower for w in ["summary", "objective"]) else 0
    bonus = cert_bonus + achieve_bonus + links_bonus + length_bonus + summary_bonus

    # ── Total ─────────────────────────────────────────────────
    total = round(min(skill_pts + edu_pts + exp_pts + fmt_pts + bonus, 100), 1)

    breakdown = {
        "skills":        skill_pts,  "skills_max":  30,
        "education":     edu_pts,    "edu_max":     20,
        "experience":    exp_pts,    "exp_max":     20,
        "formatting":    fmt_pts,    "fmt_max":     15,
        "bonus":         bonus,      "bonus_max":   15,
        "cert_bonus":    cert_bonus,
        "achieve_bonus": achieve_bonus,
        "links_bonus":   links_bonus,
        "length_bonus":  length_bonus,
        "summary_bonus": summary_bonus,
    }

    return total, breakdown


def generate_suggestions(text_lower: str, skills: list, education: list,
                          experience: list, ats_score: float) -> list:
    suggestions = []

    if ats_score < 40:
        suggestions.append("Score is low. Add clear sections: Objective, Skills, Education, Projects, Certifications.")
    elif ats_score < 60:
        suggestions.append("Good start! Add more technical skills and quantify your achievements.")

    if len(skills) < 5:
        suggestions.append("Add more technical skills relevant to your domain.")
    elif len(skills) < 10:
        suggestions.append("Try to reach 10+ relevant skills to improve ATS matching.")

    if not education:
        suggestions.append("Add your degree, institution name, graduation year, and CGPA.")

    if experience:
        suggestions.append("Quantify your experience — add numbers, impact, and technologies used.")
    elif "intern" in text_lower:
        suggestions.append("Good internship! Mention duration and key contributions.")
    else:
        suggestions.append("Add internships, freelance work, or open-source contributions.")

    if "project" not in text_lower:
        suggestions.append("Add a Projects section with tech stack and measurable outcomes.")
    else:
        suggestions.append("Include GitHub links or live demo URLs for your projects.")

    if "certification" not in text_lower and "certified" not in text_lower:
        suggestions.append("Add certifications (Coursera, NPTEL, AWS, Google) to stand out.")

    if not any(w in text_lower for w in ["github", "linkedin", "portfolio"]):
        suggestions.append("Add your GitHub, LinkedIn, or portfolio link.")

    if "summary" not in text_lower and "objective" not in text_lower:
        suggestions.append("Add a 2-3 line professional objective at the top.")

    word_count = len(text_lower.split())
    if word_count < 200:
        suggestions.append("Resume is too short. Aim for 400-700 words.")
    elif word_count > 1000:
        suggestions.append("Resume is too long. Keep it to 1-2 pages.")

    if not any(w in text_lower for w in ["achievement", "award", "winner", "rank", "hackathon"]):
        suggestions.append("Add an Achievements section — hackathon wins or academic honors.")

    return suggestions[:6] or ["Excellent resume! Tailor keywords to each job description."]