import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Dummy CV Text 
cv_text = """
Nama: Andi Pratama
Pendidikan: S1 Teknik Informatika, Universitas XYZ
Pengalaman: 2 tahun sebagai Software Engineer di perusahaan e-commerce
Skill: Python, TensorFlow, PostgreSQL, PHP, Git, Docker, REST API
Proyek: Membangun sistem rekomendasi produk menggunakan TensorFlow
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
    response = requests.post(f"{BASE_URL}/internal/ai/match", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_single_match():
    print("\n--- TEST ENDPOINT 2: SINGLE MATCH (/internal/ai/analyze-single) ---")
    payload = {
        "cv_text": cv_text,
        "job": jobs[4]  
    }
    response = requests.post(f"{BASE_URL}/internal/ai/analyze-single", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Memulai Testing API...")
    test_batch_match()
    test_single_match()
    print("\nTesting Selesai!")
