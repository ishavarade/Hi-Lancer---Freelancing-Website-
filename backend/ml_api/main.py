from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.ml_api.recommender import calculate_hybrid_job_recommendations, calculate_hybrid_project_recommendations
from backend.ml_api.career_advisor import generate_ai_career_recommendation
from backend.ml_api.chatbot_service import get_chatbot_response
from backend.ml_api.youtube_service import get_youtube_recommendations
from backend.ml_api.ats_service import analyze_resume_ats

app = FastAPI(
    title="HiLancer AI Engine API",
    description="FastAPI REST Microservice for Multi-Layer Hybrid Recommendations, AI Career Roadmap, Chatbot, and ATS Analysis",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class JobRecommendationRequest(BaseModel):
    user_resume: Optional[str] = ""
    user_skills: Optional[str] = "Python, Flask, PostgreSQL"
    user_experience: Optional[str] = "3 years"
    selected_category: Optional[str] = ""
    user_completed_projects: Optional[List[str]] = []
    jobs: List[Dict[str, Any]]

class ProjectRecommendationRequest(BaseModel):
    user_resume: Optional[str] = ""
    user_skills: Optional[str] = "Python, Flask, PostgreSQL"
    user_experience: Optional[str] = "3 years"
    selected_category: Optional[str] = ""
    user_completed_projects: Optional[List[str]] = []
    projects: List[Dict[str, Any]]

class CareerRoadmapRequest(BaseModel):
    user_skills: str
    preferred_role: str
    experience_years: Optional[int] = 2

class ChatbotRequest(BaseModel):
    query: str

class YouTubeRequest(BaseModel):
    topic: str
    level: Optional[str] = "All"

class ATSCheckRequest(BaseModel):
    resume_text: str
    target_job_title: Optional[str] = ""

@app.get("/")
def root():
    return {"status": "online", "message": "HiLancer AI Engine API is running!"}

@app.post("/api/recommend/jobs")
def recommend_jobs_endpoint(req: JobRecommendationRequest):
    try:
        recommendations = calculate_hybrid_job_recommendations(
            user_resume=req.user_resume or "",
            user_skills=req.user_skills or "",
            user_experience=req.user_experience or "",
            selected_category=req.selected_category or "",
            jobs=req.jobs,
            user_completed_projects=req.user_completed_projects or [],
            limit=100
        )
        return {"status": "success", "count": len(recommendations), "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/projects")
def recommend_projects_endpoint(req: ProjectRecommendationRequest):
    try:
        recommendations = calculate_hybrid_project_recommendations(
            user_resume=req.user_resume or "",
            user_skills=req.user_skills or "",
            user_experience=req.user_experience or "",
            selected_category=req.selected_category or "",
            projects=req.projects,
            user_completed_projects=req.user_completed_projects or [],
            limit=100
        )
        return {"status": "success", "count": len(recommendations), "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/career")
def recommend_career_endpoint(req: CareerRoadmapRequest):
    try:
        data = generate_ai_career_recommendation(
            user_skills_str=req.user_skills,
            preferred_role=req.preferred_role,
            experience_years=req.experience_years or 2
        )
        return {"status": "success", "career_roadmap": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chatbot")
def chatbot_endpoint(req: ChatbotRequest):
    try:
        res = get_chatbot_response(user_query=req.query)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube")
def youtube_endpoint(req: YouTubeRequest):
    try:
        videos = get_youtube_recommendations(topic=req.topic, level_filter=req.level or "All")
        return {"status": "success", "videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume/ats")
def ats_endpoint(req: ATSCheckRequest):
    try:
        ats_res = analyze_resume_ats(resume_text=req.resume_text, target_job_title=req.target_job_title or "")
        return {"status": "success", "ats_analysis": ats_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.ml_api.main:app", host="127.0.0.1", port=8000, reload=True)
