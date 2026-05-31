from pydantic import BaseModel
from typing import List, Optional

# --- SKEMA INPUT UTAMA ---
class JobInput(BaseModel):
    job_id: str
    title: str
    company_name: str
    description: str 

class MatchRequest(BaseModel):
    user_id: str
    cv_id: Optional[str] = None
    cv_text: str 
    filtered_jobs: List[JobInput] 

# ==========================================
# ENDPOINT 1: Match Scoring dan Rekomendasi Job
# ==========================================
class JobScore(BaseModel):
    job_id: str
    job_title: str
    company: str
    match_score: float 

class MatchResponse(BaseModel):
    cv_id: Optional[str]
    user_id: str
    extracted_skills: List[str]
    recommendations: List[JobScore]

# ==========================================
# ENDPOINT 2: Analisis Gap Skill
# ==========================================
class SingleMatchRequest(BaseModel):
    cv_text: str
    job: JobInput 

class JobDetailAnalysis(BaseModel):
    job_id: str
    job_title: str
    company: str
    match_score: float 
    skill_match: List[str]
    skill_gap: List[str]
    ai_insight: str

class SingleMatchResponse(BaseModel):
    extracted_skills: List[str]
    analysis: JobDetailAnalysis