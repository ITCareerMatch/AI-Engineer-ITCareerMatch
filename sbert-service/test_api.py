import os
import requests
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "app", ".env")
load_dotenv(dotenv_path)

BASE_URL = "http://127.0.0.1:8000" 
INTERNAL_KEY = os.getenv("INTERNAL_API_KEY")

headers = {
    "Content-Type": "application/json",
    "X-Internal-Request": INTERNAL_KEY or ""
}

# Dummy CV Text 
cv_text = """Lulusan S1 Informatika dengan pengalaman tiga tahun sebagai Fullstack Web Developer, berfokus pada pengembangan aplikasi berbasis web menggunakan React.js, Tailwind CSS, dan Vite untuk frontend, serta Node.js dan Express.js untuk backend. Berpengalaman membangun sistem end-to-end mulai dari desain antarmuka, integrasi API, hingga deployment menggunakan platform seperti Vercel dan Railway. Terampil dalam pengelolaan database PostgreSQL, integrasi AI/ML, serta penerapan autentikasi dan keamanan aplikasi. Familiar dengan version control menggunakan Git/GitHub dan terbiasa bekerja dalam tim kolaboratif. Berorientasi pada pengembangan aplikasi web yang responsif, scalable, dan sesuai kebutuhan industri modern.
"""

# Dummy Jobs
jobs = [
    {
        "job_id": "job-001",
        "title": "AI Engineer",
        "company_name": "PT Sinergi",
        "description": "Mencari AI Engineer dengan pengalaman Python, TensorFlow, dan Machine Learning."
    },
    {
        "job_id": "job-002",
        "title": "Fullstack Developer",
        "company_name": "PT Webindo",
        "description": "Butuh developer dengan skill PHP, PostgreSQL, React, dan Docker."
    },
    {
        "job_id": "job-003",
        "title": "Backend Developer",
        "company_name": "PT FintechKu",
        "description": "Menguasai Java, Spring Boot, SQL, dan REST API. Pengalaman di fintech lebih disukai."
    },
    {
        "job_id": "job-004",
        "title": "Data Scientist",
        "company_name": "PT Analitika",
        "description": "Menguasai Python, Pandas, Scikit-learn, dan pengalaman analisis data besar."
    },
    {
        "job_id": "job-005",
        "title": "Mobile Developer (Android)",
        "company_name": "PT MobileTech",
        "description": "Mencari Android dev dengan Kotlin, Java, Firebase, dan pengalaman CI/CD."
    },
    {
        "job_id": "job-006",
        "title": "DevOps Engineer",
        "company_name": "PT CloudIndo",
        "description": "Menguasai Docker, Kubernetes, CI/CD pipeline, dan cloud AWS/GCP."
    },
    {
        "job_id": "job-007",
        "title": "Frontend Developer",
        "company_name": "PT Kreatif",
        "description": "Menguasai HTML, CSS, JavaScript, React, dan UX dasar."
    },
    {
        "job_id": "job-008",
        "title": "Cybersecurity Analyst",
        "company_name": "PT SecureNet",
        "description": "Menguasai network security, penetration testing, SIEM tools, dan Python."
    },
    {
        "job_id": "job-009",
        "title": "Machine Learning Engineer",
        "company_name": "PT AIWorks",
        "description": "Menguasai Python, TensorFlow/PyTorch, NLP, dan deployment model ML."
    },
    {
        "job_id": "job-010",
        "title": "Cloud Engineer",
        "company_name": "PT Cloudify",
        "description": "Menguasai AWS, GCP, Terraform, Docker, dan pengalaman migrasi sistem ke cloud."
    }
]

def test_batch_match():
    print("\n--- TEST ENDPOINT 1: BATCH MATCH (/internal/ai/match) ---")
    payload = {
        "user_id": "user-123",
        "cv_id": "cv-456",
        "cv_text": cv_text,
        "filtered_jobs": jobs
    }
    response = requests.post(f"{BASE_URL}/internal/ai/match", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)

def test_single_match():
    print("\n--- TEST ENDPOINT 2: SINGLE MATCH (/internal/ai/analyze-single) ---")
    payload = {
        "cv_text": cv_text,
        "job": jobs[4]
    }
    response = requests.post(f"{BASE_URL}/internal/ai/analyze-single", json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)

if __name__ == "__main__":
    if not INTERNAL_KEY:
        print("Warning: INTERNAL_API_KEY not set in environment. Requests will likely be 401.")
    print("Memulai Testing API...")
    test_batch_match()
    test_single_match()
    print("\nTesting Selesai!")
