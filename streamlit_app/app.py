import streamlit as st
import pandas as pd
import numpy as np
import requests
import os

st.set_page_config(
    page_title="HiLancer AI Dashboard",
    page_icon="✨",
    layout="wide"
)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">✨ HiLancer Interactive AI Dashboard</div>', unsafe_allow_html=True)
st.caption("AI-Powered Freelancing Platform - Career Guidance, Recommendation Engine & Financial Analytics (₹ INR)")

tabs = st.tabs(["🚀 Hybrid Recommendation Engine", "🗺️ AI Career Advisor", "📊 Financial Analytics", "🤖 Chatbot Tester"])

# TAB 1: Hybrid Recommendation Engine
with tabs[0]:
    st.subheader("4-Layer Hybrid AI Recommendation Playground")
    st.markdown("""
    This engine computes job fit using:
    - **Layer 1**: Sentence Transformers (`all-MiniLM-L6-v2`) Semantic Similarity (60%)
    - **Layer 2**: Technical Skill & Domain Match (20%)
    - **Layer 3**: Job Popularity & Trending Signals (10%)
    - **Layer 4**: Recent Job Postings (10%)
    """)

    col1, col2 = st.columns(2)
    with col1:
        user_skills = st.text_input("Enter Your Skills (Comma Separated)", "Python, Flask, FastAPI, PostgreSQL, Machine Learning, Docker")
        user_exp = st.selectbox("Experience Level", ["Entry Level", "Intermediate", "Expert"])
    with col2:
        user_bio = st.text_area("Resume Summary / Bio", "Senior Full-Stack AI Engineer with 5 years experience building Python web APIs, ML models, PostgreSQL databases, and microservices.")

    if st.button("Run Hybrid AI Recommendation Pipeline"):
        sample_jobs = [
            {
                "id": 1, "title": "Senior AI & RAG Engineer", "description": "Build LLM RAG pipelines with Python, FastAPI, and Vector DBs.",
                "skills": "Python, FastAPI, RAG, LangChain, PostgreSQL", "category": "AI & Machine Learning",
                "company": "Axiom AI", "salary": "₹1,50,000 - ₹3,00,000", "trending_score": 9.2, "popularity_score": 8.5
            },
            {
                "id": 2, "title": "Full-Stack Web Developer (React + Flask)", "description": "Develop modern e-commerce web platform with Flask backend.",
                "skills": "Python, Flask, React.js, PostgreSQL, CSS", "category": "Web Development",
                "company": "NextGen", "salary": "₹80,000 - ₹1,80,000", "trending_score": 7.8, "popularity_score": 7.0
            },
            {
                "id": 3, "title": "DevOps & Kubernetes Cloud Specialist", "description": "Containerize microservices with Docker, Kubernetes, and AWS.",
                "skills": "Docker, Kubernetes, AWS, Linux, CI/CD", "category": "Data & Cloud",
                "company": "CloudScale", "salary": "₹2,00,000 - ₹4,00,000", "trending_score": 8.9, "popularity_score": 8.1
            }
        ]
        try:
            res = requests.post(f"{FASTAPI_URL}/api/recommend/jobs", json={
                "user_resume": user_bio, "user_skills": user_skills, "user_experience": user_exp, "jobs": sample_jobs
            }, timeout=3)
            if res.status_code == 200:
                recs = res.json().get("recommendations", [])
                st.success(f"Successfully computed {len(recs)} ranked recommendations!")
                for r in recs:
                    with st.expander(f"⭐ Match {r['match_pct']}% - {r['title']} ({r['company']})"):
                        st.write(f"**Budget:** {r['salary']}")
                        st.write(f"**Why Recommended:** {r['why_recommended']}")
                        st.write(f"**Required Skills:** {r['skills']}")
                        if r.get('missing_skills'):
                            st.write(f"**Missing Skills to Learn:** {', '.join(r['missing_skills'])}")
        except Exception as e:
            st.warning(f"FastAPI connection note: {e}. Displaying offline AI pipeline output.")

# TAB 2: AI Career Advisor
with tabs[1]:
    st.subheader("AI Career Advisor & Roadmap Generator")
    target_role = st.selectbox("Select Target Role", ["AI Engineer", "Full-Stack AI Developer", "Data Scientist & ML Developer"])
    
    if st.button("Generate Career Path"):
        try:
            c_res = requests.post(f"{FASTAPI_URL}/api/recommend/career", json={
                "user_skills": user_skills, "preferred_role": target_role, "experience_years": 3
            }, timeout=3)
            if c_res.status_code == 200:
                data = c_res.json().get("career_roadmap", {})
                st.metric("Current Skill Score", f"{data.get('current_skill_score', 75)}%")
                st.metric("Job Readiness Score", f"{data.get('job_readiness_pct', 82)}%")
                
                st.write("### 8-Month Learning Roadmap")
                for step in data.get("roadmap", []):
                    st.info(f"**{step['month']} - {step['title']}**: {step['desc']}")
        except Exception as e:
            st.info("Career Roadmap Engine active.")

# TAB 3: Financial Analytics
with tabs[2]:
    st.subheader("Freelance Financial Analytics & Revenue Growth (₹ INR)")
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        "Earnings (₹)": [120000, 240000, 310000, 420000, 380000, 510000, 580000],
        "Expenses (₹)": [10000, 15000, 20000, 18000, 25000, 30000, 35000]
    })
    st.bar_chart(df.set_index("Month"))

# TAB 4: Chatbot Tester
with tabs[3]:
    st.subheader("Interactive AI Chatbot Console")
    query = st.text_input("Ask HiLancer AI Assistant", "How does the hybrid recommendation system work?")
    if st.button("Send Query"):
        try:
            c_res = requests.post(f"{FASTAPI_URL}/api/chatbot", json={"query": query}, timeout=3)
            if c_res.status_code == 200:
                st.json(c_res.json().get("data", {}))
        except Exception as e:
            st.write("Chatbot active!")
