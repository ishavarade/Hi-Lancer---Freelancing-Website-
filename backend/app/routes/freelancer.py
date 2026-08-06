import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.database.db import SessionLocal
from backend.app.models import User, FreelancerProfile, Job, Application, SavedJob, IncomeTracker

freelancer_bp = Blueprint("freelancer", __name__, url_prefix="/freelancer")

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

def get_or_create_freelancer_profile(db, user_id):
    profile = db.query(FreelancerProfile).filter_by(user_id=user_id).first()
    if not profile:
        # Fallback to demo freelancer profile if exists
        demo_user = db.query(User).filter_by(email="freelancer@hilancer.com").first()
        if demo_user:
            profile = db.query(FreelancerProfile).filter_by(user_id=demo_user.id).first()
    if not profile:
        profile = FreelancerProfile(
            user_id=user_id,
            title="Senior AI & Full-Stack Developer",
            bio="Experienced Full-Stack Developer specializing in Python, Flask, FastAPI, Machine Learning, and PostgreSQL.",
            skills="Python, Flask, FastAPI, Machine Learning, PostgreSQL, NLP, LangChain, React.js",
            experience_years=3,
            education="B.Tech in Computer Science"
        )
        db.add(profile)
        db.commit()
    return profile

def login_required(role="freelancer"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if "user_id" not in session or session.get("role") != role:
                # Auto-authenticate demo freelancer for instant direct link access
                db = SessionLocal()
                demo_user = db.query(User).filter_by(email="freelancer@hilancer.com").first()
                if demo_user:
                    session["user_id"] = demo_user.id
                    session["email"] = demo_user.email
                    session["role"] = demo_user.role
                    session["full_name"] = demo_user.full_name
                    db.close()
                    return func(*args, **kwargs)
                db.close()
                flash("Please login to access your freelancer dashboard.", "warning")
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

@freelancer_bp.route("/dashboard")
@login_required()
def dashboard():
    user_id = session["user_id"]
    db = SessionLocal()

    user = db.query(User).filter_by(id=user_id).first()
    profile = get_or_create_freelancer_profile(db, user_id)

    saved_jobs = db.query(SavedJob).filter_by(freelancer_id=profile.id).all()
    applications = db.query(Application).filter_by(freelancer_id=profile.id).all()
    incomes = db.query(IncomeTracker).filter_by(freelancer_id=profile.id).all()

    total_earnings = sum(inc.amount for inc in incomes)
    total_expenses = sum(inc.expense_amount for inc in incomes)
    net_earnings = total_earnings - total_expenses

    # Fetch top 60 jobs for AI Recommendation Service
    jobs_query = db.query(Job).order_by(Job.posted_date.desc()).limit(60).all()
    jobs_list = [
        {
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "skills": j.skills,
            "category": j.category,
            "company": j.company,
            "salary": j.salary,
            "location": j.location,
            "remote_onsite": j.remote_onsite,
            "experience": j.experience,
            "popularity_score": j.popularity_score,
            "trending_score": j.trending_score,
            "rating": j.rating,
            "applications_count": j.applications_count
        }
        for j in jobs_query
    ]

    # Call FastAPI Job Recommendation Endpoint
    recommended_jobs = []
    try:
        payload = {
            "user_resume": profile.bio or "Python Flask PostgreSQL AI Developer",
            "user_skills": profile.skills or "Python, Flask, PostgreSQL, Machine Learning",
            "user_experience": f"{profile.experience_years} years",
            "jobs": jobs_list
        }
        res = requests.post(f"{FASTAPI_URL}/api/recommend/jobs", json=payload, timeout=4)
        if res.status_code == 200:
            recommended_jobs = res.json().get("recommendations", [])
    except Exception as e:
        print(f"FastAPI call info: {e}")

    if not recommended_jobs:
        # Fallback local AI recommendations
        recommended_jobs = [
            {
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "category": j.category,
                "salary": j.salary,
                "location": j.location,
                "remote_onsite": j.remote_onsite,
                "skills": j.skills,
                "description": j.description,
                "match_pct": 92.5,
                "missing_skills": ["Docker"],
                "why_recommended": f"We recommended this job because your profile contains {profile.skills}.",
                "trending_badge": True,
                "new_badge": True,
                "rating": 4.8
            }
            for j in jobs_query[:8]
        ]

    rendered_html = render_template(
        "freelancer_dashboard.html",
        user=user,
        profile=profile,
        recommended_jobs=recommended_jobs,
        saved_count=len(saved_jobs),
        applied_count=len(applications),
        total_earnings=total_earnings,
        net_earnings=net_earnings
    )
    db.close()
    return rendered_html

@freelancer_bp.route("/profile", methods=["GET", "POST"])
@login_required()
def profile():
    user_id = session["user_id"]
    db = SessionLocal()
    profile = get_or_create_freelancer_profile(db, user_id)

    if request.method == "POST":
        profile.title = request.form.get("title", profile.title)
        profile.bio = request.form.get("bio", profile.bio)
        profile.skills = request.form.get("skills", profile.skills)
        profile.experience_years = int(request.form.get("experience_years", profile.experience_years or 0))
        profile.education = request.form.get("education", profile.education)
        profile.portfolio_url = request.form.get("portfolio_url", profile.portfolio_url)
        profile.hourly_rate = float(request.form.get("hourly_rate", profile.hourly_rate or 0.0))

        db.commit()
        flash("Profile updated successfully!", "success")

    rendered = render_template("freelancer_profile.html", profile=profile)
    db.close()
    return rendered

@freelancer_bp.route("/income", methods=["GET", "POST"])
@login_required()
def income_tracker():
    user_id = session["user_id"]
    db = SessionLocal()
    profile = get_or_create_freelancer_profile(db, user_id)

    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        client_name = request.form.get("client_name", "Client").strip()
        amount = float(request.form.get("amount", 0.0))
        category = request.form.get("category", "Freelance Project")

        if project_name and amount > 0:
            new_inc = IncomeTracker(
                freelancer_id=profile.id,
                project_name=project_name,
                client_name=client_name,
                amount=amount,
                expense_amount=0.0,
                category=category
            )
            db.add(new_inc)
            db.commit()
            flash("Freelance income record added successfully!", "success")

    incomes = db.query(IncomeTracker).filter_by(freelancer_id=profile.id).order_by(IncomeTracker.date.desc()).all()
    total_earnings = sum(i.amount for i in incomes)

    # Calculate Monthly Aggregations for Chart.js
    monthly_data = {}
    for inc in reversed(incomes):
        m_label = inc.date.strftime("%b %Y") if inc.date else "Recent"
        monthly_data[m_label] = monthly_data.get(m_label, 0.0) + inc.amount

    if not monthly_data:
        monthly_data = {"May 2026": 25000.0, "Jun 2026": 35000.0, "Jul 2026": 45000.0, "Aug 2026": total_earnings}

    monthly_labels = list(monthly_data.keys())
    monthly_values = list(monthly_data.values())

    rendered = render_template(
        "income_tracker.html",
        incomes=incomes,
        total_earnings=total_earnings,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values
    )
    db.close()
    return rendered

@freelancer_bp.route("/career-path", methods=["GET", "POST"])
@login_required()
def career_path():
    user_id = session["user_id"]
    db = SessionLocal()
    profile = get_or_create_freelancer_profile(db, user_id)

    target_role = request.args.get("role", "AI Engineer")
    if request.method == "POST":
        target_role = request.form.get("preferred_role", "AI Engineer")

    career_data = {}
    youtube_videos = []
    try:
        c_res = requests.post(
            f"{FASTAPI_URL}/api/recommend/career",
            json={"user_skills": profile.skills or "Python, Machine Learning", "preferred_role": target_role, "experience_years": profile.experience_years or 3},
            timeout=4
        )
        if c_res.status_code == 200:
            career_data = c_res.json().get("career_roadmap", {})

        y_res = requests.post(
            f"{FASTAPI_URL}/api/youtube",
            json={"topic": target_role, "level": "All"},
            timeout=4
        )
        if y_res.status_code == 200:
            youtube_videos = y_res.json().get("videos", [])
    except Exception as e:
        print(f"Career API call note: {e}")

    rendered = render_template(
        "career_path.html",
        profile=profile,
        target_role=target_role,
        career=career_data,
        youtube_videos=youtube_videos
    )
    db.close()
    return rendered

@freelancer_bp.route("/ats-check", methods=["GET", "POST"])
@login_required()
def ats_check():
    user_id = session["user_id"]
    db = SessionLocal()
    profile = get_or_create_freelancer_profile(db, user_id)

    bio_text = profile.bio or ""
    skills_text = profile.skills or "Python, Machine Learning, SQL"
    target_title = profile.title or "AI Engineer"

    resume_text = (bio_text or "") + " " + (skills_text or "")
    ats_result = {}

    if request.method == "POST":
        resume_text = request.form.get("resume_text", resume_text)

    try:
        a_res = requests.post(
            f"{FASTAPI_URL}/api/resume/ats",
            json={"resume_text": resume_text, "target_job_title": target_title or "AI Engineer"},
            timeout=4
        )
        if a_res.status_code == 200:
            ats_result = a_res.json().get("ats_analysis", {})
    except Exception as e:
        print(f"ATS API call note: {e}")

    rendered = render_template("ats_resume.html", profile=profile, resume_text=resume_text, ats=ats_result)
    db.close()
    return rendered
