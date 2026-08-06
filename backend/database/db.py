import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Database URL from environment or default to SQLite fallback
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "hilancer_db")

# Try PostgreSQL first; if connection fails or not configured, use SQLite fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

def get_engine():
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        # Test connection
        conn = engine.connect()
        conn.close()
        return engine
    except Exception:
        # Fallback to local SQLite database
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "hilancer.db"))
        sqlite_url = f"sqlite:///{sqlite_path}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.models import User, FreelancerProfile, ClientProfile, Job, FreelanceProject, Application, SavedJob, IncomeTracker, CareerRoadmap, ChatHistory
    Base.metadata.create_all(bind=engine)
