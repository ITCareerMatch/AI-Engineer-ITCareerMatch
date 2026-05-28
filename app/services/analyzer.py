from typing import List, Dict
from app.utils.text_cleaner import clean_it_text
from app.services.skill_extractor import extract_skills

# Fungsi untuk menganalisis kecocokan dan gap skill antara CV dan deskripsi pekerjaan
def analyze_match_and_gap(cv_skills: List[str], job_desc: str) -> Dict:
    cleaned_job = clean_it_text(job_desc)
    job_skills = extract_skills(cleaned_job)
    
    cv_skills_set = set(s.lower() for s in cv_skills)
    job_skills_set = set(s.lower() for s in job_skills)
    
    match_set = cv_skills_set.intersection(job_skills_set)
    gap_set = job_skills_set.difference(cv_skills_set)
    
    skill_match = [skill for skill in job_skills if skill.lower() in match_set]
    skill_gap = [skill for skill in job_skills if skill.lower() in gap_set]
    
    if not job_skills:
        insight = "Lowongan ini tidak menyebutkan spesifikasi teknis (skill) secara eksplisit."
    elif not skill_gap:
        insight = f"Luar biasa! Seluruh skill teknis utama yang dibutuhkan ({', '.join(skill_match[:3])}) sudah Anda kuasai."
    elif len(skill_match) > len(skill_gap):
        insight = f"Profil Anda sangat cocok. Anda sudah menguasai {', '.join(skill_match[:2])}. Pertimbangkan untuk mempelajari {skill_gap[0]} untuk peluang lolos yang lebih besar."
    elif skill_match:
        insight = f"Anda memiliki dasar {skill_match[0]}, namun perusahaan sangat membutuhkan keahlian di {', '.join(skill_gap[:2])}."
    else:
        insight = f"Lowongan ini membutuhkan {', '.join(skill_gap[:3])}. Sepertinya Anda perlu mempelajari skill tersebut terlebih dahulu."

    return {
        "skill_match": skill_match,
        "skill_gap": skill_gap,
        "ai_insight": insight
    }