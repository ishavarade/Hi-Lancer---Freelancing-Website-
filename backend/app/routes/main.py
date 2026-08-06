import os
import datetime
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.database.db import SessionLocal
from backend.app.models import Job, FreelanceProject, Application, SavedJob, FreelancerProfile, ClientProfile, IncomeTracker, User
from backend.ml_api.recommender import calculate_hybrid_job_recommendations, calculate_hybrid_project_recommendations
from backend.database.seed import ALL_CATEGORIES

main_bp = Blueprint("main", __name__)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

@main_bp.route("/")
def index():
    db = SessionLocal()
    featured_jobs = db.query(Job).order_by(Job.trending_score.desc()).limit(6).all()
    total_jobs = db.query(Job).count()
    db.close()
    return render_template("index.html", featured_jobs=featured_jobs, total_jobs=total_jobs)

@main_bp.route("/jobs")
def jobs_list():
    category_param = request.args.get("category", "").strip()
    active_tab = request.args.get("tab", "jobs").strip()

    db = SessionLocal()
    
    # User Profile Data
    user_resume = "Full-Stack Developer specializing in Python, Flask, FastAPI, Machine Learning, PostgreSQL, NLP, LangChain, RAG Systems."
    user_skills = "Python, Flask, FastAPI, Machine Learning, PostgreSQL, NLP, LangChain, Gemini API, React.js"
    user_experience = "3 years"
    user_completed_projects = []
    user_saved_ids = set()
    user_applied_ids = set()

    # Retrieve user context if logged in or demo freelancer
    user_id = session.get("user_id")
    f_prof = None
    if user_id:
        f_prof = db.query(FreelancerProfile).filter_by(user_id=user_id).first()
    if not f_prof:
        demo_user = db.query(User).filter_by(email="freelancer@hilancer.com").first()
        if demo_user:
            f_prof = db.query(FreelancerProfile).filter_by(user_id=demo_user.id).first()

    if f_prof:
        user_resume = f_prof.bio or user_resume
        user_skills = f_prof.skills or user_skills
        user_experience = f"{f_prof.experience_years} years"
        
        # Saved and Applied
        saved_records = db.query(SavedJob).filter_by(freelancer_id=f_prof.id).all()
        user_saved_ids = {s.job_id for s in saved_records}
        app_records = db.query(Application).filter_by(freelancer_id=f_prof.id).all()
        user_applied_ids = {a.job_id for a in app_records}
        
        # Completed projects history
        inc_records = db.query(IncomeTracker).filter_by(freelancer_id=f_prof.id).all()
        user_completed_projects = [inc.project_name for inc in inc_records]

    # Run Multi-Factor Hybrid AI Recommendations only for the active tab view for maximum speed
    ranked_jobs = []
    ranked_projects = []

    if active_tab == 'projects':
        proj_query = db.query(FreelanceProject)
        if category_param:
            proj_query = proj_query.filter(FreelanceProject.category == category_param)
        raw_projects = proj_query.order_by(FreelanceProject.created_at.desc()).limit(150).all()
        
        projects_dicts = [
            {
                "id": p.id,
                "title": p.title,
                "client_name": p.client_name,
                "category": p.category or "Web Development",
                "description": p.description or f"We need a freelancer for {p.title}",
                "budget": p.budget,
                "skills": p.skills,
                "duration": p.duration or "2 weeks",
                "difficulty": p.difficulty or "Intermediate",
                "deadline": p.deadline or "7 Days Left",
                "status": p.status or "Open"
            }
            for p in raw_projects
        ]

        ranked_projects = calculate_hybrid_project_recommendations(
            user_resume=user_resume,
            user_skills=user_skills,
            user_experience=user_experience,
            selected_category=category_param,
            projects=projects_dicts,
            user_completed_projects=user_completed_projects,
            limit=100
        )
    else:
        job_query = db.query(Job)
        if category_param:
            job_query = job_query.filter(Job.category == category_param)
        raw_jobs = job_query.order_by(Job.trending_score.desc()).limit(150).all()

        jobs_dicts = [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "company_logo": j.company_logo or "https://img.icons8.com/color/96/company.png",
                "company_description": j.company_description or j.description,
                "industry": j.industry or "Technology Services",
                "location": j.location,
                "remote_onsite": j.remote_onsite,
                "job_type": j.job_type,
                "salary": j.salary,
                "experience": j.experience,
                "qualification": j.qualification or "B.Tech / B.E. / Any Graduate",
                "responsibilities": j.responsibilities or "• Design, build, and deploy clean software modules.",
                "skills": j.skills,
                "description": j.description,
                "category": j.category,
                "posted_date": j.posted_date,
                "last_date_to_apply": j.last_date_to_apply or "15 Days Left",
                "trending_score": j.trending_score or 5.0
            }
            for j in raw_jobs
        ]

        ranked_jobs = calculate_hybrid_job_recommendations(
            user_resume=user_resume,
            user_skills=user_skills,
            user_experience=user_experience,
            selected_category=category_param,
            jobs=jobs_dicts,
            user_completed_projects=user_completed_projects,
            limit=100
        )

    db.close()
    return render_template(
        "jobs.html",
        jobs=ranked_jobs,
        freelance_projects=ranked_projects,
        categories=ALL_CATEGORIES,
        current_cat=category_param,
        active_tab=active_tab,
        user_saved_ids=user_saved_ids,
        user_applied_ids=user_applied_ids
    )

@main_bp.route("/api/job/<int:job_id>")
def api_job_detail(job_id):
    db = SessionLocal()
    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        db.close()
        return jsonify({"error": "Job not found"}), 404

    already_applied = False
    already_saved = False

    if "user_id" in session and session.get("role") == "freelancer":
        f_prof = db.query(FreelancerProfile).filter_by(user_id=session["user_id"]).first()
        if f_prof:
            already_applied = bool(db.query(Application).filter_by(job_id=job.id, freelancer_id=f_prof.id).first())
            already_saved = bool(db.query(SavedJob).filter_by(job_id=job.id, freelancer_id=f_prof.id).first())

    job_data = {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "company_logo": job.company_logo or "https://img.icons8.com/color/96/company.png",
        "company_description": job.company_description or f"{job.company} is a leading enterprise in the industry.",
        "industry": job.industry or "Technology Services",
        "location": job.location,
        "remote_onsite": job.remote_onsite,
        "job_type": job.job_type,
        "salary": job.salary,
        "experience": job.experience,
        "qualification": job.qualification or "B.Tech / B.E. / Any Graduate",
        "responsibilities": job.responsibilities or "• Design, build, and deploy clean software modules.\n• Optimize backend queries and API performance.\n• Maintain unit tests and code documentation.",
        "skills": [s.strip() for s in (job.skills or "").split(",") if s.strip()],
        "posted_date": job.posted_date.strftime("%b %d, %Y") if job.posted_date else "Recently",
        "last_date_to_apply": job.last_date_to_apply or "15 Days Left",
        "already_applied": already_applied,
        "already_saved": already_saved
    }
    db.close()
    return jsonify(job_data)

@main_bp.route("/freelance-project/<int:project_id>/complete", methods=["POST"])
def complete_freelance_project(project_id):
    db = SessionLocal()
    proj = db.query(FreelanceProject).filter_by(id=project_id).first()

    if not proj:
        db.close()
        flash("Project not found.", "warning")
        return redirect(url_for("main.jobs_list", tab="projects"))

    # Auto-get freelancer profile or demo freelancer
    user_id = session.get("user_id")
    f_prof = None
    if user_id:
        f_prof = db.query(FreelancerProfile).filter_by(user_id=user_id).first()
    
    if not f_prof:
        demo_user = db.query(User).filter_by(email="freelancer@hilancer.com").first()
        if demo_user:
            f_prof = db.query(FreelancerProfile).filter_by(user_id=demo_user.id).first()

    if f_prof and proj:
        proj.status = "Completed"
        proj.freelancer_id = f_prof.id
        proj.completed_at = datetime.datetime.utcnow()

        # Automatically add project amount to Income Tracker
        new_inc = IncomeTracker(
            freelancer_id=f_prof.id,
            project_name=proj.title,
            client_name=proj.client_name,
            amount=proj.budget,
            expense_amount=0.0,
            category="Freelance Project",
            date=datetime.datetime.utcnow()
        )
        db.add(new_inc)
        db.commit()
        flash(f"Project '{proj.title}' marked as completed! ₹{proj.budget:,.2f} added to your Income Tracker.", "success")

    db.close()
    return redirect(url_for("main.jobs_list", tab="projects"))

@main_bp.route("/job/<int:job_id>")
def job_detail(job_id):
    db = SessionLocal()
    job = db.query(Job).filter_by(id=job_id).first()

    if not job:
        db.close()
        flash("Job not found.", "warning")
        return redirect(url_for("main.jobs_list"))

    # Increment view count
    job.views = (job.views or 0) + 1
    db.commit()

    similar_jobs = db.query(Job).filter(Job.category == job.category, Job.id != job.id).limit(3).all()

    already_applied = False
    already_saved = False

    if "user_id" in session and session.get("role") == "freelancer":
        f_prof = db.query(FreelancerProfile).filter_by(user_id=session["user_id"]).first()
        if f_prof:
            already_applied = bool(db.query(Application).filter_by(job_id=job.id, freelancer_id=f_prof.id).first())
            already_saved = bool(db.query(SavedJob).filter_by(job_id=job.id, freelancer_id=f_prof.id).first())

    db.close()
    return render_template(
        "job_detail.html",
        job=job,
        similar_jobs=similar_jobs,
        already_applied=already_applied,
        already_saved=already_saved
    )

@main_bp.route("/job/<int:job_id>/apply", methods=["POST"])
def apply_job(job_id):
    if "user_id" not in session or session.get("role") != "freelancer":
        flash("Please log in as a Freelancer to apply for jobs.", "warning")
        return redirect(url_for("auth.login"))

    cover_letter = request.form.get("cover_letter", "").strip()
    db = SessionLocal()

    f_prof = db.query(FreelancerProfile).filter_by(user_id=session["user_id"]).first()
    job = db.query(Job).filter_by(id=job_id).first()

    if f_prof and job:
        existing = db.query(Application).filter_by(job_id=job.id, freelancer_id=f_prof.id).first()
        if not existing:
            app = Application(
                job_id=job.id,
                freelancer_id=f_prof.id,
                cover_letter=cover_letter,
                status="Submitted"
            )
            job.applications_count = (job.applications_count or 0) + 1
            db.add(app)
            db.commit()
            flash("Application submitted successfully!", "success")
        else:
            flash("You have already applied for this job.", "info")

    db.close()
    return redirect(url_for("main.jobs_list"))

@main_bp.route("/job/<int:job_id>/save", methods=["POST"])
def save_job(job_id):
    if "user_id" not in session or session.get("role") != "freelancer":
        flash("Please log in as a Freelancer to save jobs.", "warning")
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    f_prof = db.query(FreelancerProfile).filter_by(user_id=session["user_id"]).first()
    if f_prof:
        existing = db.query(SavedJob).filter_by(job_id=job_id, freelancer_id=f_prof.id).first()
        if existing:
            db.delete(existing)
            db.commit()
            flash("Job removed from saved list.", "info")
        else:
            saved = SavedJob(job_id=job_id, freelancer_id=f_prof.id)
            db.add(saved)
            db.commit()
            flash("Job saved to your dashboard!", "success")
    db.close()
    return redirect(url_for("main.jobs_list"))

@main_bp.route("/api/chatbot_widget", methods=["POST"])
def chatbot_widget():
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"response": "Hello! How can I assist you on HiLancer today?", "source": "HiLancer Assistant"})

    try:
        res = requests.post(f"{FASTAPI_URL}/api/chatbot", json={"query": user_query}, timeout=4)
        if res.status_code == 200:
            return jsonify(res.json().get("data", {}))
    except Exception as e:
        print(f"Chatbot widget note: {e}")

    return jsonify({
        "response": f"Thank you for reaching out! I'm here to help with HiLancer job recommendations, client projects, and ATS resume scans.",
        "source": "HiLancer Assistant",
        "quick_actions": [
            {"label": "Recommended Jobs", "query": "How to see recommended jobs?"},
            {"label": "Post a Project", "query": "How to post a project?"}
        ]
    })

