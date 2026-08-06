from typing import Dict, Any, List

CAREER_GOAL_TEMPLATES = {
    "AI Engineer": {
        "required_skills": ["Python", "Git", "Linux", "Docker", "AWS", "FastAPI", "CI/CD", "Kubernetes", "Redis", "Transformers", "LangChain", "RAG", "Vector DB", "MLOps"],
        "roadmap": [
            {"month": "Month 1", "title": "Python Mastery, Git & Linux", "skills": ["Advanced Python", "Git", "Linux CLI"], "desc": "Master object-oriented Python, async programming, version control, and Linux shell environment."},
            {"month": "Month 2", "title": "Containerization & Cloud Infrastructure", "skills": ["Docker", "AWS Essentials"], "desc": "Build microservice containers with Docker and deploy resilient cloud services on AWS."},
            {"month": "Month 3", "title": "Modern APIs & Pipeline Automation", "skills": ["FastAPI", "CI/CD Workflows"], "desc": "Design high-performance REST APIs with FastAPI and automate testing with GitHub Actions."},
            {"month": "Month 4", "title": "Orchestration & Caching Systems", "skills": ["Kubernetes", "Redis"], "desc": "Deploy container clusters with Kubernetes and optimize application latency using Redis caching."},
            {"month": "Month 5", "title": "Deep Learning & Transformers", "skills": ["PyTorch", "HuggingFace Transformers"], "desc": "Train and fine-tune Transformer architectures (BERT, GPT) using HuggingFace and PyTorch."},
            {"month": "Month 6", "title": "LLMs, LangChain & RAG Architectures", "skills": ["LangChain", "RAG Architecture"], "desc": "Build intelligent LLM applications, custom document Q&A agents, and Retrieval-Augmented Generation."},
            {"month": "Month 7", "title": "Vector Databases & Semantic Search", "skills": ["Pinecone / ChromaDB", "Vector Indexing"], "desc": "Index embeddings in vector stores for real-time high-dimensional semantic search."},
            {"month": "Month 8", "title": "Production MLOps & Monitoring", "skills": ["MLOps", "Model Monitoring"], "desc": "Establish automated model retraining, drift monitoring, and production deployment pipelines."}
        ]
    },
    "Full-Stack AI Developer": {
        "required_skills": ["Python", "Flask", "FastAPI", "React.js", "PostgreSQL", "Tailwind CSS", "Docker", "REST APIs", "LLM APIs", "System Architecture"],
        "roadmap": [
            {"month": "Month 1", "title": "Advanced Python & Web Fundamentals", "skills": ["Python 3.12", "REST Principles"], "desc": "Master backend Python concepts, HTTP protocols, and OOP design patterns."},
            {"month": "Month 2", "title": "Backend Engineering with Flask & FastAPI", "skills": ["Flask", "FastAPI"], "desc": "Build scalable web application servers and high-speed asynchronous REST microservices."},
            {"month": "Month 3", "title": "Relational Database Mastery", "skills": ["PostgreSQL", "SQLAlchemy ORM"], "desc": "Design normalized database schemas, write complex queries, and implement indexing."},
            {"month": "Month 4", "title": "Modern Frontend Web Development", "skills": ["React.js", "Modern CSS / Glassmorphism"], "desc": "Build interactive, component-driven user interfaces with dynamic responsive layouts."},
            {"month": "Month 5", "title": "AI Model & API Integration", "skills": ["Gemini API", "HuggingFace Models"], "desc": "Connect frontend applications with cutting-edge AI model APIs and streaming responses."},
            {"month": "Month 6", "title": "Deployment & Cloud Microservices", "skills": ["Docker", "GCP / AWS"], "desc": "Containerize web applications and deploy scalable full-stack projects to cloud environments."}
        ]
    },
    "Data Scientist & ML Developer": {
        "required_skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Data Visualization", "Feature Engineering", "TensorFlow", "NLP", "Statistical Modeling"],
        "roadmap": [
            {"month": "Month 1", "title": "Data Manipulation & Exploratory Analysis", "skills": ["Pandas", "NumPy", "SQL"], "desc": "Wrangle structured dataset records, execute complex SQL queries, and clean missing values."},
            {"month": "Month 2", "title": "Statistical Modeling & Machine Learning", "skills": ["Scikit-Learn", "Feature Engineering"], "desc": "Train classification, regression, and clustering algorithms with evaluation metrics."},
            {"month": "Month 3", "title": "Deep Learning & Neural Networks", "skills": ["TensorFlow / Keras", "PyTorch"], "desc": "Construct multi-layer artificial neural networks for complex pattern recognition."},
            {"month": "Month 4", "title": "Natural Language Processing (NLP)", "skills": ["NLTK", "spaCy", "Transformers"], "desc": "Preprocess text, extract named entities, build TF-IDF and transformer semantic models."},
            {"month": "Month 5", "title": "Production Deployment & Dashboards", "skills": ["Streamlit", "FastAPI Deployment"], "desc": "Deploy interactive data analytics dashboards and expose machine learning models via APIs."}
        ]
    }
}

PRACTICE_PLATFORM_LINKS = [
    {
        "platform": "W3Schools",
        "title": "Practice Python, SQL & Web Development on W3Schools",
        "url": "https://www.w3schools.com/python/",
        "note": "Interactive tutorials, quizzes, and instant code editor practice."
    },
    {
        "platform": "W3Schools",
        "title": "Practice Machine Learning & Data Science on W3Schools",
        "url": "https://www.w3schools.com/datascience/",
        "note": "Step-by-step code exercises for Pandas, NumPy, and Scikit-learn."
    },
    {
        "platform": "GeeksforGeeks",
        "title": "Practice Problem Solving & Algorithms on GeeksforGeeks",
        "url": "https://practice.geeksforgeeks.org/explore?page=1&category[]=Python&sortBy=submissions",
        "note": "Solve real-world coding problems, data structures, and algorithm challenges."
    },
    {
        "platform": "GeeksforGeeks",
        "title": "Practice Machine Learning & System Design on GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/machine-learning/",
        "note": "Comprehensive tutorials, interview questions, and practice problems."
    }
]

COURSE_PLATFORMS = [
    {
        "platform": "Udemy",
        "name": "Complete AI & Machine Learning Masterclass",
        "url": "https://www.udemy.com/topic/artificial-intelligence/",
        "badge": "Top Rated"
    },
    {
        "platform": "Udemy",
        "name": "Docker & Kubernetes: The Practical Guide",
        "url": "https://www.udemy.com/topic/docker/",
        "badge": "Bestseller"
    },
    {
        "platform": "YouTube",
        "name": "FreeCodeCamp Complete AI & Python Engineer Courses",
        "url": "https://www.youtube.com/@freecodecamp",
        "badge": "Free Course"
    }
]

def generate_ai_career_recommendation(user_skills_str: str, preferred_role: str, experience_years: int = 2) -> Dict[str, Any]:
    # Select template based on preferred role
    role_key = "AI Engineer"
    for k in CAREER_GOAL_TEMPLATES.keys():
        if k.lower() in preferred_role.lower():
            role_key = k
            break

    template = CAREER_GOAL_TEMPLATES[role_key]
    req_skills = template["required_skills"]
    
    # Extract user skills
    user_skill_list = [s.strip().lower() for s in user_skills_str.split(",") if s.strip()]
    
    matched = []
    missing = []
    for sk in req_skills:
        if any(user_s in sk.lower() or sk.lower() in user_s for user_s in user_skill_list):
            matched.append(sk)
        else:
            missing.append(sk)

    skill_score = round((len(matched) / max(1, len(req_skills))) * 100, 1)
    readiness_pct = round(min(98.0, skill_score + (experience_years * 4.5)), 1)
    job_readiness_pct = round(min(95.0, readiness_pct * 0.92), 1)

    return {
        "target_role": role_key,
        "current_skill_score": skill_score,
        "readiness_pct": readiness_pct,
        "job_readiness_pct": job_readiness_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "roadmap": template["roadmap"],
        "practice_links": PRACTICE_PLATFORM_LINKS,
        "recommended_courses": COURSE_PLATFORMS
    }
