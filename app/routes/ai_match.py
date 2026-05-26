from fastapi import APIRouter, HTTPException, Request
from app.schemas.match import (
    MatchRequest, 
    MatchResponse, 
    JobScore, 
    SingleMatchRequest, 
    SingleMatchResponse, 
    JobDetailAnalysis
)
from app.utils.text_cleaner import clean_it_text
from app.services.skill_extractor import extract_skills
from app.services.analyzer import analyze_match_and_gap
from app.utils import config

router = APIRouter()

# =====================================================================
# ENDPOINT 1: Match Scoring dan Rekomendasi Job
# =====================================================================
@router.post("/internal/ai/match", response_model=MatchResponse)
async def process_match(request: MatchRequest, req: Request):
    sbert_model = req.app.state.sbert_model
    if sbert_model is None:
        raise HTTPException(status_code=503, detail="SBERT Model gagal dimuat")

    cleaned_cv = clean_it_text(request.cv_text)
    user_skills = extract_skills(cleaned_cv)

    cleaned_job_descs = [clean_it_text(job.description) for job in request.filtered_jobs]
    cv_list = [cleaned_cv] * len(cleaned_job_descs)
    
    try:
        scores = sbert_model.predict_batch(cleaned_job_descs, cv_list)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"SBERT Inference Failed: {str(e)}")

    # Hybrid Scoring: Gabungkan SBERT Score dengan Skill Match Score
    # Ini bertujuan untuk memberikan bobot lebih pada kecocokan skill yang eksplisit disebutkan di deskripsi loker
    job_with_scores = []
    for idx, job in enumerate(request.filtered_jobs):
        # 1. Ambil skor SBERT dasar
        sbert_score = float(scores[idx] * 100)
        
        # 2. Ambil skor kecocokan skill
        job_skills = extract_skills(job.description)
        if len(job_skills) > 0:
            match_count = len(set(user_skills).intersection(set(job_skills)))
            skill_score = (match_count / len(job_skills)) * 100
            final_score = (sbert_score * 0.6) + (skill_score * 0.4)
        else:
            final_score = sbert_score
            
        job_with_scores.append((job, final_score))

    job_with_scores.sort(key=lambda x: x[1], reverse=True)
    top_k_jobs = job_with_scores[:config.TOP_K_RECOMMENDATIONS]

    # Rangkai output
    recommendations = []
    for job, score in top_k_jobs:
        recommendations.append(
            JobScore(
                job_id=job.job_id,
                job_title=job.title,
                company=job.company_name,
                match_score=round(float(score), 2)
            )
        )

    return MatchResponse(
        cv_id=request.cv_id,
        user_id=request.user_id,
        extracted_skills=user_skills,
        recommendations=recommendations
    )

# =====================================================================
# ENDPOINT 2: Analisis Gap Skill
# =====================================================================
@router.post("/internal/ai/analyze-single", response_model=SingleMatchResponse)
async def process_single_match(request: SingleMatchRequest, req: Request):
    sbert_model = req.app.state.sbert_model
    if sbert_model is None:
        raise HTTPException(status_code=503, detail="SBERT Model gagal dimuat")

    cleaned_cv = clean_it_text(request.cv_text)
    user_skills = extract_skills(cleaned_cv)
    cleaned_job = clean_it_text(request.job.description)

    try:
        scores = sbert_model.predict_batch([cleaned_job], [cleaned_cv])
        sbert_score = float(scores[0] * 100)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"SBERT Inference Failed: {str(e)}")

    # Hybrid Scoring
    job_skills = extract_skills(request.job.description)
    if len(job_skills) > 0:
        match_count = len(set(user_skills).intersection(set(job_skills)))
        skill_score = (match_count / len(job_skills)) * 100
        match_score = (sbert_score * 0.6) + (skill_score * 0.4)
    else:
        match_score = sbert_score

    # Menjalankan analisis gap skill untuk lowongan yang dipilih
    analysis = analyze_match_and_gap(user_skills, request.job.description)

    detail_analysis = JobDetailAnalysis(
        job_id=request.job.job_id,
        job_title=request.job.title,
        company=request.job.company_name,
        match_score=round(match_score, 2),
        skill_match=analysis["skill_match"],
        skill_gap=analysis["skill_gap"],
        ai_insight=analysis["ai_insight"]
    )

    return SingleMatchResponse(
        extracted_skills=user_skills,
        analysis=detail_analysis
    )