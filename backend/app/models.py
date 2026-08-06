import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'freelancer' or 'client'
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    freelancer_profile = relationship("FreelancerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class FreelancerProfile(Base):
    __tablename__ = "freelancer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    title = Column(String(255), default="")
    bio = Column(Text, default="")
    skills = Column(Text, default="")  # Comma separated
    experience_years = Column(Integer, default=0)
    education = Column(String(255), default="")
    portfolio_url = Column(String(255), default="")
    resume_filename = Column(String(255), default="")
    hourly_rate = Column(Float, default=0.0)

    user = relationship("User", back_populates="freelancer_profile")
    applications = relationship("Application", back_populates="freelancer")
    saved_jobs = relationship("SavedJob", back_populates="freelancer")
    incomes = relationship("IncomeTracker", back_populates="freelancer")
    roadmaps = relationship("CareerRoadmap", back_populates="freelancer")

class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_name = Column(String(255), default="")
    industry = Column(String(255), default="")
    location = Column(String(255), default="")
    website = Column(String(255), default="")

    user = relationship("User", back_populates="client_profile")
    jobs = relationship("Job", back_populates="client")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client_profiles.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)
    experience = Column(String(100), default="Intermediate")
    salary = Column(String(100), default="$500 - $1,500")
    category = Column(String(100), default="Web Development")
    company = Column(String(255), default="TechCorp")
    remote_onsite = Column(String(50), default="Remote")
    location = Column(String(255), default="Worldwide")
    posted_date = Column(DateTime, default=datetime.datetime.utcnow)
    deadline = Column(String(100), default="2 weeks")
    job_type = Column(String(100), default="Fixed-price")
    education = Column(String(100), default="Bachelor's")
    industry = Column(String(100), default="Technology")
    popularity_score = Column(Float, default=5.0)
    views = Column(Integer, default=10)
    applications_count = Column(Integer, default=2)
    rating = Column(Float, default=4.5)
    trending_score = Column(Float, default=8.0)

    client = relationship("ClientProfile", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    saved_by = relationship("SavedJob", back_populates="job")
    company_logo = Column(String(255), default="")
    company_description = Column(Text, default="")
    qualification = Column(String(255), default="B.Tech / Any Graduate")
    responsibilities = Column(Text, default="")
    last_date_to_apply = Column(String(100), default="15 Days Left")

class FreelanceProject(Base):
    __tablename__ = "freelance_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    client_name = Column(String(255), nullable=False)
    category = Column(String(100), default="Web Development")
    description = Column(Text, default="")
    budget = Column(Float, nullable=False)
    skills = Column(Text, nullable=False)
    duration = Column(String(100), default="2 weeks")
    difficulty = Column(String(50), default="Intermediate")
    deadline = Column(String(100), default="7 Days Left")
    status = Column(String(50), default="Open")  # 'Open', 'In Progress', 'Completed'
    freelancer_id = Column(Integer, ForeignKey("freelancer_profiles.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("freelancer_profiles.id"), nullable=False)
    cover_letter = Column(Text, default="")
    status = Column(String(50), default="Submitted")  # 'Submitted', 'Hired', 'Rejected'
    applied_date = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    freelancer = relationship("FreelancerProfile", back_populates="applications")

class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    freelancer_id = Column(Integer, ForeignKey("freelancer_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_date = Column(DateTime, default=datetime.datetime.utcnow)

    freelancer = relationship("FreelancerProfile", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")

class IncomeTracker(Base):
    __tablename__ = "income_tracker"

    id = Column(Integer, primary_key=True, index=True)
    freelancer_id = Column(Integer, ForeignKey("freelancer_profiles.id"), nullable=False)
    project_name = Column(String(255), nullable=False)
    client_name = Column(String(255), default="Client")
    amount = Column(Float, nullable=False)
    expense_amount = Column(Float, default=0.0)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    category = Column(String(100), default="Freelance Revenue")

    freelancer = relationship("FreelancerProfile", back_populates="incomes")

class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    freelancer_id = Column(Integer, ForeignKey("freelancer_profiles.id"), nullable=False)
    target_role = Column(String(255), nullable=False)
    current_score = Column(Float, default=70.0)
    readiness_pct = Column(Float, default=75.0)
    roadmap_data = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    freelancer = relationship("FreelancerProfile", back_populates="roadmaps")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    source = Column(String(50), default="FAQ")  # 'FAQ' or 'Gemini'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

