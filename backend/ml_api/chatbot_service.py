import os
import re
import numpy as np
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

FAQ_KNOWLEDGE_BASE = [
    {
        "questions": ["How do I apply for jobs on HiLancer?", "How to apply for a job?", "Apply project steps"],
        "answer": "To apply for jobs on HiLancer:\n1. Log in to your Freelancer account.\n2. Browse recommended jobs on your AI Dashboard.\n3. Click 'Apply Now' on any job card.\n4. Submit a tailored cover letter highlighting your matched skills!"
    },
    {
        "questions": ["How do clients post projects on HiLancer?", "Post project guide", "How to hire freelancers?"],
        "answer": "Clients can post projects easily:\n1. Log in to your Client Account.\n2. Navigate to 'Post Project' from your dashboard.\n3. Enter project title, detailed description, required skills, budget range, and category.\n4. Click 'Publish Job' to instantly start receiving AI-matched applications!"
    },
    {
        "questions": ["How does the AI Hybrid Recommendation System work?", "AI job matching algorithm"],
        "answer": "HiLancer uses a 4-Layer Hybrid AI Engine:\n- Layer 1: Sentence Transformers (all-MiniLM-L6-v2) for semantic description & resume matching.\n- Layer 2: Skill & Category content matching.\n- Layer 3: Trending & Popularity metrics.\n- Layer 4: Weighted Hybrid Scoring (60% Semantic + 20% Skills + 10% Trending + 10% Recency)."
    },
    {
        "questions": ["What is the AI Career Advisor?", "Career roadmap guide", "How to build skills?"],
        "answer": "The AI Career Advisor analyzes your current resume and skills against industry standard job graphs. It generates a month-by-month learning roadmap, readiness scores, YouTube video playlists, and direct practice links on GeeksforGeeks & W3Schools!"
    },
    {
        "questions": ["How do I check if my resume is ATS friendly?", "ATS resume score check"],
        "answer": "HiLancer provides an integrated ATS Resume Analyzer. Go to your Freelancer Dashboard -> 'ATS Resume Check' to get instant keyword match scores, formatting analysis, and referral access to top ATS building platforms!"
    },
    {
        "questions": ["What are the platform payment fees and policies?", "Platform fees", "Payment safety"],
        "answer": "HiLancer ensures secure transactions for both freelancers and clients. Client payments are protected in escrow until milestone deliverables are approved. Platform service fee is a flat competitive 5% per contract."
    }
]

# Quick action buttons for UI display
QUICK_ACTIONS = [
    {"label": "Recommended Jobs", "query": "How to see recommended jobs?"},
    {"label": "Post a Project", "query": "How to post a project?"},
    {"label": "ATS Resume Score", "query": "How do I check if my resume is ATS friendly?"},
    {"label": "Contact Support", "query": "How to contact support?"}
]

def search_faq(user_query: str, threshold: float = 0.45) -> Dict[str, Any]:
    from backend.ml_api.recommender import compute_semantic_similarity

    best_match_answer = None
    max_sim = 0.0

    for faq in FAQ_KNOWLEDGE_BASE:
        for q in faq["questions"]:
            sim = compute_semantic_similarity(user_query.lower(), q.lower())
            if sim > max_sim:
                max_sim = sim
                best_match_answer = faq["answer"]

    if max_sim >= threshold and best_match_answer:
        return {
            "found": True,
            "response": best_match_answer,
            "source": "FAQ Semantic Search",
            "confidence": round(max_sim * 100, 1),
            "quick_actions": QUICK_ACTIONS
        }
    return {"found": False, "confidence": round(max_sim * 100, 1)}

def call_gemini_fallback(user_query: str) -> str:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        return f"HiLancer Assistant: Thank you for asking about '{user_query}'. Our AI platform connects freelancers with personalized job recommendations, career roadmaps, and client project hiring. Please ensure GOOGLE_API_KEY is configured in your .env for full Gemini generative capabilities."

    try:
        import google.generativeai as genai
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = (
            "You are HiLancer AI Assistant, an expert freelancing platform concierge. "
            "Help the user professionally, concisely, and clearly. "
            f"User Question: {user_query}"
        )
        res = model.generate_content(prompt)
        if res and res.text:
            return res.text.strip()
    except Exception as e:
        print(f"Gemini API call note: {e}")

    return f"HiLancer Assistant: I'm here to assist you with jobs, career advice, and hiring on HiLancer! You can ask about job applications, posting projects, or ATS resume checks."

def get_chatbot_response(user_query: str) -> Dict[str, Any]:
    faq_res = search_faq(user_query)
    if faq_res["found"]:
        return {
            "response": faq_res["response"],
            "source": faq_res["source"],
            "confidence": faq_res["confidence"],
            "quick_actions": QUICK_ACTIONS
        }
    
    # Gemini Fallback
    gemini_text = call_gemini_fallback(user_query)
    return {
        "response": gemini_text,
        "source": "Gemini AI",
        "confidence": 95.0,
        "quick_actions": QUICK_ACTIONS
    }
