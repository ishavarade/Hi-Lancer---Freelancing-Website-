from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database.db import SessionLocal
from backend.app.models import User, FreelancerProfile, ClientProfile

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = SessionLocal()
        user = db.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["email"] = user.email
            session["role"] = user.role
            session["full_name"] = user.full_name
            db.close()
            flash(f"Welcome back, {user.full_name}!", "success")
            
            if user.role == "freelancer":
                return redirect(url_for("freelancer.dashboard"))
            else:
                return redirect(url_for("client.dashboard"))
        else:
            db.close()
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "freelancer")

        if not email or not password or not full_name:
            flash("Please fill in all required fields.", "warning")
            return render_template("register.html")

        db = SessionLocal()
        existing_user = db.query(User).filter_by(email=email).first()

        if existing_user:
            db.close()
            flash("Email address is already registered. Please login.", "info")
            return redirect(url_for("auth.login"))

        pwd_hash = generate_password_hash(password)
        new_user = User(
            email=email,
            password_hash=pwd_hash,
            role=role,
            full_name=full_name
        )
        db.add(new_user)
        db.commit()

        # Create default associated profile
        if role == "freelancer":
            f_profile = FreelancerProfile(
                user_id=new_user.id,
                title="Freelance Developer",
                skills="Python, Flask, JavaScript, HTML, CSS",
                bio="Passionate developer eager to build innovative solutions on HiLancer."
            )
            db.add(f_profile)
        else:
            c_profile = ClientProfile(
                user_id=new_user.id,
                company_name=f"{full_name}'s Enterprise",
                industry="Technology"
            )
            db.add(c_profile)

        db.commit()
        db.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
