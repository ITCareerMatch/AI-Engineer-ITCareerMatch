import re
from typing import List

# Daftar skill utama yang sering muncul dalam deskripsi pekerjaan IT
MASTER_SKILLS = [
    # Programming Languages
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Ruby", "Go", 
    "Rust", "Scala", "Perl", "R", "MATLAB", "Shell Script", "Objective-C",

    # Frontend Development
    "React.js", "React Native", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js",
    "Tailwind CSS", "Bootstrap", "Material-UI", "HTML5", "CSS3",

    # Backend Development
    "Node.js", "Express.js", "Django", "Flask", "Spring Boot", "Laravel", "FastAPI",
    "ASP.NET Core", "Ruby on Rails", "Koa.js", "Hapi.js",

    # Mobile Development
    "Kotlin", "Swift", "Flutter", "Android", "iOS", "Xamarin",

    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle Database", "MariaDB",
    "Elasticsearch", "Firebase Realtime DB", "Firestore", "Cassandra", "Neo4j",

    # DevOps & Cloud
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Jenkins", "Terraform",
    "Ansible", "Vagrant", "OpenShift", "Cloudflare", "Heroku", "Netlify", "Vercel",

    # Version Control & Collaboration
    "Git", "GitHub", "GitLab", "Bitbucket", "SVN",

    # Data Science & AI/ML
    "TensorFlow", "PyTorch", "Scikit-Learn", "Keras", "Pandas", "NumPy", "Matplotlib",
    "Seaborn", "XGBoost", "LightGBM", "NLTK", "SpaCy", "OpenCV", "Hugging Face Transformers",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning",

    # Testing & QA
    "Selenium", "Cypress", "JUnit", "Mockito", "PyTest", "Jest", "Mocha", "Chai",
    "Postman", "SoapUI", "Playwright",

    # Security
    "OWASP", "Burp Suite", "Metasploit", "Wireshark", "Penetration Testing", "Ethical Hacking",
    "Cybersecurity", "SSL/TLS", "OAuth2", "JWT",

    # Other Tools & Platforms
    "Linux", "Ubuntu", "WSL", "Bash", "PowerShell", "VS Code", "IntelliJ IDEA", "Eclipse",
    "Jupyter Notebook", "Google Colab", "Streamlit", "Tableau", "Power BI", "Hadoop", "Spark",
    "Apache Kafka", "RabbitMQ", "REST API", "GraphQL", "gRPC", "Microservices", "Serverless"
]


def extract_skills(text: str) -> List[str]:
    """Mengekstrak skill menggunakan word boundaries agar presisi."""
    found_skills = set()
    text_lower = text.lower()
    
    for skill in MASTER_SKILLS:
        skill_lower = skill.lower()
        
        # Penanganan skill dengan karakter khusus
        if any(char in skill_lower for char in ['+', '#', '.']):
            escaped_skill = re.escape(skill_lower)
            if re.search(r'(?:^|\s)' + escaped_skill + r'(?:$|\s)', text_lower):
                found_skills.add(skill)
        else:
            # Penanganan skill alfanumerik biasa menggunakan word boundary
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_lower):
                found_skills.add(skill)
                
    return list(found_skills)