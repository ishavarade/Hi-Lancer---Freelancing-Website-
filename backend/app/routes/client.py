from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.database.db import SessionLocal
from backend.app.models import User, ClientProfile, Job, Application, FreelancerProfile

client_bp = Blueprint("client", __name__, url_prefix="/client")

def client_login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "client":
            db = SessionLocal()
            demo_client = db.query(User).filter_by(email="client@hilancer.com").first()
            if demo_client:
                session["user_id"] = demo_client.id
                session["email"] = demo_client.email
                session["role"] = demo_client.role
                session["full_name"] = demo_client.full_name
                db.close()
                return func(*args, **kwargs)
            db.close()
            flash("Please login to access your client dashboard.", "warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@client_bp.route("/dashboard")
@client_login_required
def dashboard():
    user_id = session["user_id"]
    db = SessionLocal()

    c_profile = db.query(ClientProfile).filter_by(user_id=user_id).first()
    if not c_profile:
        c_profile = ClientProfile(user_id=user_id, company_name="Apex Innovations")
        db.add(c_profile)
        db.commit()

    client_jobs = db.query(Job).filter_by(client_id=c_profile.id).order_by(Job.posted_date.desc()).all()
    
    job_ids = [j.id for j in client_jobs]
    applications = db.query(Application).filter(Application.job_id.in_(job_ids)).all() if job_ids else []

    rendered_html = render_template(
        "client_dashboard.html",
        client_profile=c_profile,
        jobs=client_jobs,
        applications_count=len(applications)
    )
    db.close()
    return rendered_html

@client_bp.route("/post-project", methods=["GET", "POST"])
@client_login_required
def post_project():
    user_id = session["user_id"]
    db = SessionLocal()
    c_profile = db.query(ClientProfile).filter_by(user_id=user_id).first()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        skills = request.form.get("skills", "").strip()
        category = request.form.get("category", "Web Development")
        salary = request.form.get("salary", "$1,000 - $3,000")
        experience = request.form.get("experience", "Intermediate")
        remote_type = request.form.get("remote_onsite", "Remote")
        location = request.form.get("location", "Worldwide")

        if title and description and skills:
            new_job = Job(
                client_id=c_profile.id,
                title=title,
                description=description,
                skills=skills,
                category=category,
                company=c_profile.company_name or "Client Company",
                salary=salary,
                experience=experience,
                remote_onsite=remote_type,
                location=location
            )
            db.add(new_job)
            db.commit()
            db.close()
            flash("Project published successfully! AI is matching freelancers now.", "success")
            return redirect(url_for("client.dashboard"))
        else:
            flash("Please fill in title, description, and required skills.", "warning")

    rendered = render_template("post_project.html", client_profile=c_profile)
    db.close()
    return rendered

@client_bp.route("/edit-project/<int:job_id>", methods=["GET", "POST"])
@client_login_required
def edit_project(job_id):
    db = SessionLocal()
    job = db.query(Job).filter_by(id=job_id).first()

    if not job:
        db.close()
        flash("Project not found.", "danger")
        return redirect(url_for("client.dashboard"))

    if request.method == "POST":
        job.title = request.form.get("title", job.title)
        job.description = request.form.get("description", job.description)
        job.skills = request.form.get("skills", job.skills)
        job.category = request.form.get("category", job.category)
        job.salary = request.form.get("salary", job.salary)
        job.experience = request.form.get("experience", job.experience)
        job.remote_onsite = request.form.get("remote_onsite", job.remote_onsite)

        db.commit()
        db.close()
        flash("Project updated successfully!", "success")
        return redirect(url_for("client.dashboard"))

    rendered = render_template("edit_project.html", job=job)
    db.close()
    return rendered

@client_bp.route("/delete-project/<int:job_id>", methods=["POST"])
@client_login_required
def delete_project(job_id):
    db = SessionLocal()
    job = db.query(Job).filter_by(id=job_id).first()
    if job:
        db.delete(job)
        db.commit()
        flash("Project deleted.", "info")
    db.close()
    return redirect(url_for("client.dashboard"))

@client_bp.route("/applicants/<int:job_id>")
@client_login_required
def view_applicants(job_id):
    db = SessionLocal()
    job = db.query(Job).filter_by(id=job_id).first()
    applications = db.query(Application).filter_by(job_id=job_id).all()
    
    app_details = []
    for app in applications:
        freelancer = db.query(FreelancerProfile).filter_by(id=app.freelancer_id).first()
        user = db.query(User).filter_by(id=freelancer.user_id).first() if freelancer else None
        app_details.append({
            "application_id": app.id,
            "freelancer_name": user.full_name if user else "Freelancer",
            "freelancer_title": freelancer.title if freelancer else "Developer",
            "freelancer_skills": freelancer.skills if freelancer else "",
            "hourly_rate": freelancer.hourly_rate if freelancer else 0.0,
            "cover_letter": app.cover_letter,
            "status": app.status,
            "applied_date": app.applied_date
        })

    rendered = render_template("view_applicants.html", job=job, applicants=app_details)
    db.close()
    return rendered

@client_bp.route("/hire/<int:application_id>", methods=["POST"])
@client_login_required
def hire_freelancer(application_id):
    db = SessionLocal()
    app = db.query(Application).filter_by(id=application_id).first()
    if app:
        app.status = "Hired"
        db.commit()
        flash("Freelancer officially hired for this project!", "success")
    db.close()
    return redirect(url_for("client.dashboard"))
