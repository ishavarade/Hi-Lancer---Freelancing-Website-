import random
import datetime
from sqlalchemy.orm import Session
from backend.database.db import SessionLocal, init_db
from backend.app.models import User, FreelancerProfile, ClientProfile, Job, FreelanceProject, IncomeTracker, Base
from werkzeug.security import generate_password_hash

ALL_CATEGORIES = [
    "Web Development",
    "Frontend Development",
    "Backend Development",
    "Full Stack Development",
    "Mobile App Development",
    "Python Development",
    "Java Development",
    "Data Science",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Generative AI",
    "Computer Vision",
    "AI Chatbot Development",
    "LangChain Applications",
    "RAG Systems",
    "API Development",
    "Database Development",
    "Cloud Computing",
    "DevOps",
    "Cybersecurity",
    "UI/UX Design",
    "WordPress",
    "Shopify",
    "E-commerce",
    "Automation",
    "Data Engineering",
    "Business Intelligence",
    "Power BI",
    "Tableau",
    "Testing & QA",
    "Game Development"
]

ROLES_BY_CATEGORY = {
    "Web Development": ["Web Developer", "Full Stack Web Engineer", "Web Portal Specialist"],
    "Frontend Development": ["Frontend Engineer", "React.js Developer", "Vue/Next.js Specialist"],
    "Backend Development": ["Backend Engineer", "API Developer", "Node.js/Python Developer"],
    "Full Stack Development": ["Full Stack Engineer", "MERN Stack Specialist", "Full Stack Tech Lead"],
    "Mobile App Development": ["Mobile App Engineer", "Flutter Developer", "React Native Architect"],
    "Python Development": ["Python Developer", "Django/Flask Specialist", "Python Automation Lead"],
    "Java Development": ["Java Enterprise Developer", "Spring Boot Architect", "Backend Java Engineer"],
    "Data Science": ["Data Scientist", "Predictive Analytics Specialist", "Quantitative Analyst"],
    "Machine Learning": ["Machine Learning Engineer", "ML Model Specialist", "Scikit-Learn Architect"],
    "Deep Learning": ["Deep Learning Specialist", "PyTorch Developer", "Neural Network Engineer"],
    "NLP": ["NLP Specialist", "Text Analytics Engineer", "Sentiment Analysis Developer"],
    "Generative AI": ["Generative AI Engineer", "LLM Fine-Tuning Specialist", "Prompt Engineer"],
    "Computer Vision": ["Computer Vision Engineer", "OpenCV Developer", "Image Processing Lead"],
    "AI Chatbot Development": ["AI Chatbot Developer", "Conversational AI Engineer", "Dialogflow Developer"],
    "LangChain Applications": ["LangChain Developer", "Agentic AI Developer", "AI Workflow Architect"],
    "RAG Systems": ["RAG Systems Architect", "Vector Database Engineer", "Knowledge Retrieval Specialist"],
    "API Development": ["REST API Specialist", "FastAPI/GraphQL Developer", "API Gateway Architect"],
    "Database Development": ["Database Architect", "PostgreSQL Developer", "SQL Optimization Specialist"],
    "Cloud Computing": ["AWS Cloud Architect", "Azure Infrastructure Engineer", "Cloud Solutions Lead"],
    "DevOps": ["DevOps Specialist", "Kubernetes Engineer", "CI/CD Pipeline Lead"],
    "Cybersecurity": ["Cybersecurity Analyst", "Penetration Tester", "Security Auditor"],
    "UI/UX Design": ["UI/UX Designer", "Figma Design System Specialist", "Product Designer"],
    "WordPress": ["WordPress Specialist", "Custom WP Theme Developer", "WooCommerce Architect"],
    "Shopify": ["Shopify Expert", "Liquid & App Developer", "Shopify Plus Architect"],
    "E-commerce": ["E-commerce Specialist", "Payment Gateway Developer", "Cart Architect"],
    "Automation": ["RPA Automation Specialist", "Selenium/Playwright Developer", "Python Automation Engineer"],
    "Data Engineering": ["Data Engineer", "PySpark/ETL Pipeline Architect", "Snowflake Engineer"],
    "Business Intelligence": ["BI Specialist", "Data Visualization Lead", "Analytics Consultant"],
    "Power BI": ["Power BI Developer", "DAX & Dashboard Specialist", "Report Architect"],
    "Tableau": ["Tableau Specialist", "Visual Analytics Developer", "BI Architect"],
    "Testing & QA": ["QA Automation Engineer", "Test Engineer", "API Testing Specialist"],
    "Game Development": ["Unity Game Developer", "Unreal Engine Specialist", "C# Game Programmer"]
}

SKILLS_BY_CATEGORY = {
    "Web Development": ["HTML5", "CSS3", "JavaScript", "Flask", "PostgreSQL", "Bootstrap"],
    "Frontend Development": ["React.js", "Vue.js", "TypeScript", "Tailwind CSS", "HTML5"],
    "Backend Development": ["Python", "Node.js", "Flask", "FastAPI", "PostgreSQL", "Redis"],
    "Full Stack Development": ["React.js", "Python", "Flask", "PostgreSQL", "Docker", "Node.js"],
    "Mobile App Development": ["Flutter", "React Native", "Swift", "Kotlin", "Firebase"],
    "Python Development": ["Python", "Flask", "FastAPI", "PostgreSQL", "SQL", "Docker"],
    "Java Development": ["Java", "Spring Boot", "Hibernate", "PostgreSQL", "Microservices"],
    "Data Science": ["Python", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Jupyter"],
    "Machine Learning": ["Python", "Scikit-Learn", "PyTorch", "TensorFlow", "FastAPI"],
    "Deep Learning": ["PyTorch", "TensorFlow", "CUDA", "Python", "Deep Neural Networks"],
    "NLP": ["Python", "NLTK", "Spacy", "Transformers", "NLP", "PyTorch"],
    "Generative AI": ["Python", "HuggingFace", "Transformers", "LangChain", "Gemini API"],
    "Computer Vision": ["Python", "OpenCV", "PyTorch", "YOLO", "Image Processing"],
    "AI Chatbot Development": ["Python", "LangChain", "Gemini API", "FastAPI", "NLP"],
    "LangChain Applications": ["Python", "LangChain", "Gemini API", "ChromaDB", "FastAPI"],
    "RAG Systems": ["Python", "LangChain", "Pinecone", "ChromaDB", "RAG", "FastAPI"],
    "API Development": ["FastAPI", "Python", "REST APIs", "GraphQL", "Swagger", "PostgreSQL"],
    "Database Development": ["PostgreSQL", "SQL", "Database Tuning", "Redis", "Python"],
    "Cloud Computing": ["AWS", "Docker", "Kubernetes", "Terraform", "CloudFormation"],
    "DevOps": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "AWS", "Git"],
    "Cybersecurity": ["Network Security", "Ethical Hacking", "Python", "Linux", "OWASP"],
    "UI/UX Design": ["Figma", "UI/UX", "Wireframing", "Prototyping", "Adobe XD"],
    "WordPress": ["WordPress", "PHP", "MySQL", "CSS3", "WooCommerce"],
    "Shopify": ["Shopify", "Liquid", "JavaScript", "HTML5", "CSS3"],
    "E-commerce": ["React.js", "Stripe API", "Node.js", "PostgreSQL", "E-commerce"],
    "Automation": ["Python", "Selenium", "Playwright", "BeautifulSoup", "Automation"],
    "Data Engineering": ["Python", "SQL", "Spark", "Airflow", "PostgreSQL", "Snowflake"],
    "Business Intelligence": ["SQL", "Power BI", "Tableau", "Python", "Excel"],
    "Power BI": ["Power BI", "DAX", "SQL", "Data Modeling", "Excel"],
    "Tableau": ["Tableau", "SQL", "Data Visualization", "Python", "Excel"],
    "Testing & QA": ["Selenium", "PyTest", "Postman", "QA Automation", "Jira"],
    "Game Development": ["Unity", "C#", "Unreal Engine", "C++", "3D Graphics"]
}

COMPANY_DATA = [
    {"name": "TCS", "logo": "https://img.icons8.com/color/96/tcs.png", "industry": "IT Services & Consulting", "location": "Pune, Maharashtra"},
    {"name": "Infosys", "logo": "https://img.icons8.com/color/96/infosys.png", "industry": "IT Services & Software", "location": "Bangalore, Karnataka"},
    {"name": "Accenture", "logo": "https://img.icons8.com/color/96/accenture.png", "industry": "Management & IT Consulting", "location": "Mumbai, Maharashtra"},
    {"name": "Capgemini", "logo": "https://img.icons8.com/color/96/capgemini.png", "industry": "Technology Services", "location": "Hyderabad, Telangana"},
    {"name": "Google", "logo": "https://img.icons8.com/color/96/google-logo.png", "industry": "Technology & Internet", "location": "Bangalore, Karnataka"},
    {"name": "Microsoft", "logo": "https://img.icons8.com/color/96/microsoft.png", "industry": "Cloud & Software", "location": "Hyderabad, Telangana"},
    {"name": "Amazon", "logo": "https://img.icons8.com/color/96/amazon.png", "industry": "E-commerce & Cloud", "location": "Bangalore, Karnataka"},
    {"name": "Fiv9", "logo": "https://img.icons8.com/color/96/company.png", "industry": "Software & AI Solutions", "location": "Pune, Maharashtra"},
    {"name": "TechVision", "logo": "https://img.icons8.com/color/96/organization.png", "industry": "Enterprise Software", "location": "Delhi NCR"},
    {"name": "Axiom AI", "logo": "https://img.icons8.com/color/96/artificial-intelligence.png", "industry": "Artificial Intelligence", "location": "Bangalore, Karnataka"},
    {"name": "CloudScale Labs", "logo": "https://img.icons8.com/color/96/cloud.png", "industry": "Cloud Infrastructure", "location": "Remote (India)"},
    {"name": "Apex Digital", "logo": "https://img.icons8.com/color/96/domain.png", "industry": "Digital Transformation", "location": "Mumbai, Maharashtra"}
]

SALARIES_FULLTIME = ["₹3–5 LPA", "₹5–8 LPA", "₹6–10 LPA", "₹8–12 LPA", "₹12–18 LPA", "₹20–30 LPA"]
SALARIES_INTERN = ["₹20,000/month", "₹30,000/month", "₹40,000/month"]
EXPERIENCES = ["0–1 Years", "0–2 Years", "2–4 Years", "3–5 Years", "5+ Years"]
EMPLOYMENT_TYPES = ["Full-Time", "Part-Time", "Contract", "Internship", "Remote", "Hybrid"]

def seed_data(num_jobs=1500):
    from backend.database.db import engine
    Base.metadata.drop_all(bind=engine)
    init_db()
    db: Session = SessionLocal()

    print("Seeding users, expanded corporate jobs, and freelance projects across 32 domain categories...")

    # Create Demo Freelancer User
    freelancer_user = db.query(User).filter_by(email="freelancer@hilancer.com").first()
    if not freelancer_user:
        freelancer_user = User(
            email="freelancer@hilancer.com",
            password_hash=generate_password_hash("password123"),
            role="freelancer",
            full_name="Alex Rivera"
        )
        db.add(freelancer_user)
        db.commit()

        f_profile = FreelancerProfile(
            user_id=freelancer_user.id,
            title="Senior AI & Full-Stack Developer",
            bio="Experienced Full-Stack Developer specializing in Python, Flask, FastAPI, Machine Learning, LangChain, RAG Systems, and PostgreSQL.",
            skills="Python, Flask, FastAPI, Machine Learning, PostgreSQL, NLP, LangChain, Gemini API, React.js",
            experience_years=3,
            education="B.Tech in Computer Science",
            portfolio_url="https://github.com/alexrivera-dev",
            hourly_rate=2500.0
        )
        db.add(f_profile)
        db.commit()
    else:
        f_profile = db.query(FreelancerProfile).filter_by(user_id=freelancer_user.id).first()

    # Create Demo Client User
    client_user = db.query(User).filter_by(email="client@hilancer.com").first()
    if not client_user:
        client_user = User(
            email="client@hilancer.com",
            password_hash=generate_password_hash("password123"),
            role="client",
            full_name="Sarah Jenkins"
        )
        db.add(client_user)
        db.commit()

        c_profile = ClientProfile(
            user_id=client_user.id,
            company_name="Axiom Tech",
            industry="Artificial Intelligence",
            location="Bangalore, Karnataka",
            website="https://axiomtech.ai"
        )
        db.add(c_profile)
        db.commit()
    
    c_profile_id = db.query(ClientProfile).first().id

    # Seed Initial Completed Income Records
    incomes = [
        IncomeTracker(freelancer_id=f_profile.id, project_name="AI Chatbot Development", client_name="Axiom Tech", amount=45000.0, expense_amount=0.0, category="AI Chatbot Development", date=datetime.datetime.now() - datetime.timedelta(days=30)),
        IncomeTracker(freelancer_id=f_profile.id, project_name="Build Restaurant Website", client_name="Gourmet Bistro", amount=25000.0, expense_amount=0.0, category="Web Development", date=datetime.datetime.now() - datetime.timedelta(days=15)),
        IncomeTracker(freelancer_id=f_profile.id, project_name="FastAPI & LangChain RAG Integration", client_name="CloudScale Labs", amount=60000.0, expense_amount=0.0, category="RAG Systems", date=datetime.datetime.now() - datetime.timedelta(days=5)),
    ]
    db.add_all(incomes)
    db.commit()

    # Seed Freelance Projects across ALL 32 categories
    projects_to_insert = []
    clients_pool = ["Gourmet Bistro", "Axiom Tech", "ShopEase Solutions", "FitPulse Systems", "CloudScale Labs", "DataMetrics Global", "QuickCart Express", "FinTech Hub", "HealthPulse AI", "GameRealm Inc", "EduTech Labs"]
    
    for cat in ALL_CATEGORIES:
        roles = ROLES_BY_CATEGORY[cat]
        skills_pool = SKILLS_BY_CATEGORY[cat]

        for idx in range(3):
            role_name = roles[idx % len(roles)]
            client_name = random.choice(clients_pool)
            p_title = f"{role_name} Project for {client_name}" if idx > 0 else f"{cat} Solution for {client_name}"
            budget = float(random.randint(20, 85) * 1000)
            
            proj = FreelanceProject(
                title=p_title,
                client_name=client_name,
                category=cat,
                description=f"We need an expert freelancer for {cat} to build scalable solutions using {', '.join(skills_pool)}. Deliverables include clean code architecture and testing.",
                budget=budget,
                skills=", ".join(skills_pool),
                duration=f"{random.randint(1, 6)} weeks",
                difficulty=random.choice(["Beginner", "Intermediate", "Advanced"]),
                deadline=f"{random.randint(4, 18)} Days Left",
                status="Open"
            )
            projects_to_insert.append(proj)

    db.bulk_save_objects(projects_to_insert)
    db.commit()

    # Featured Jobs Required
    featured_specs = [
        ("Fiv9", "Python Developer", "Python Development", "Pune, Maharashtra", "Full-Time", "₹6–10 LPA", "0–2 Years", "Fiv9 is hiring for Python Developer"),
        ("TCS", "Python Developer", "Python Development", "Bangalore, Karnataka", "Full-Time", "₹5–8 LPA", "0–2 Years", "TCS is hiring for Python Developer"),
        ("Infosys", "AI Engineer", "Machine Learning", "Hyderabad, Telangana", "Full-Time", "₹8–12 LPA", "2–4 Years", "Infosys is hiring for AI Engineer"),
        ("Accenture", "Data Analyst", "Data Science", "Mumbai, Maharashtra", "Full-Time", "₹6–10 LPA", "0–2 Years", "Accenture is hiring for Data Analyst"),
        ("Capgemini", "Machine Learning Engineer", "Machine Learning", "Pune, Maharashtra", "Full-Time", "₹12–18 LPA", "3–5 Years", "Capgemini is hiring for Machine Learning Engineer"),
        ("Google", "Software Engineer", "Full Stack Development", "Bangalore, Karnataka", "Full-Time", "₹20–30 LPA", "2–4 Years", "Google is hiring for Software Engineer"),
    ]

    jobs_to_insert = []
    now = datetime.datetime.now()

    for idx, (c_name, role, cat, loc, emp_type, sal, exp, full_title) in enumerate(featured_specs):
        c_info = next((c for c in COMPANY_DATA if c["name"] == c_name), COMPANY_DATA[0])
        skills_list = SKILLS_BY_CATEGORY.get(cat, ["Python", "SQL", "Flask", "PostgreSQL"])
        
        j = Job(
            client_id=c_profile_id,
            title=full_title,
            description=f"{c_name} is seeking an expert {role} for high-impact {cat} engineering projects.",
            skills=", ".join(skills_list),
            experience=exp,
            salary=sal,
            category=cat,
            company=c_name,
            company_logo=c_info["logo"],
            company_description=f"{c_name} is a leading global enterprise providing cutting edge software solutions.",
            qualification="B.Tech / B.E. in CS / IT",
            responsibilities="• Design, build, and deploy clean, high-performance software modules.\n• Work closely with senior architects and cross-functional teams.\n• Optimize backend queries, API endpoints, and database performance.",
            remote_onsite="Hybrid" if idx % 2 == 0 else "Remote",
            location=loc,
            posted_date=now - datetime.timedelta(days=idx + 1),
            deadline="15 Days Left",
            last_date_to_apply="15 Days Left",
            job_type=emp_type,
            education="B.Tech / B.E.",
            industry=c_info["industry"],
            popularity_score=9.5 - idx * 0.2,
            views=random.randint(200, 900),
            applications_count=random.randint(10, 50),
            rating=4.9,
            trending_score=9.0 - idx * 0.2
        )
        jobs_to_insert.append(j)

    # Generate synthetic jobs evenly across ALL 32 categories
    num_per_category = max(10, num_jobs // len(ALL_CATEGORIES))

    for cat in ALL_CATEGORIES:
        roles = ROLES_BY_CATEGORY[cat]
        skills_pool = SKILLS_BY_CATEGORY[cat]

        for i in range(num_per_category):
            c_info = random.choice(COMPANY_DATA)
            role = random.choice(roles)
            full_title = f"{c_info['name']} is hiring for {role}"

            emp_type = random.choice(EMPLOYMENT_TYPES)
            if emp_type == "Internship":
                sal = random.choice(SALARIES_INTERN)
                exp = "0–1 Years"
            else:
                sal = random.choice(SALARIES_FULLTIME)
                exp = random.choice(EXPERIENCES)

            j = Job(
                client_id=c_profile_id,
                title=full_title,
                description=f"{c_info['name']} is seeking a skilled {role} to deliver {cat} initiatives.",
                skills=", ".join(skills_pool),
                experience=exp,
                salary=sal,
                category=cat,
                company=c_info["name"],
                company_logo=c_info["logo"],
                company_description=f"{c_info['name']} is a premier organization in {c_info['industry']}.",
                qualification=random.choice(["B.Tech / B.E. in CS / IT", "B.Tech / M.Tech / MCA", "B.Sc / BCA / Any Graduate"]),
                responsibilities="• Design, build, and deploy clean, high-performance software modules.\n• Work closely with technical leads and cross-functional teams.\n• Maintain unit tests, code documentation, and CI/CD deployment pipelines.",
                remote_onsite=random.choice(["Remote", "Onsite", "Hybrid"]),
                location=c_info["location"],
                posted_date=now - datetime.timedelta(days=random.randint(1, 30)),
                deadline=f"{random.randint(5, 25)} Days Left",
                last_date_to_apply=f"{random.randint(5, 25)} Days Left",
                job_type=emp_type,
                education="Bachelor's Degree",
                industry=c_info["industry"],
                popularity_score=round(random.uniform(4.0, 9.8), 1),
                views=random.randint(20, 500),
                applications_count=random.randint(1, 30),
                rating=round(random.uniform(4.0, 5.0), 1),
                trending_score=round(random.uniform(3.0, 9.5), 1)
            )
            jobs_to_insert.append(j)

            if len(jobs_to_insert) >= 500:
                db.bulk_save_objects(jobs_to_insert)
                db.commit()
                jobs_to_insert = []

    if jobs_to_insert:
        db.bulk_save_objects(jobs_to_insert)
        db.commit()

    total_jobs = db.query(Job).count()
    total_projects = db.query(FreelanceProject).count()
    print(f"Successfully seeded {total_jobs} corporate jobs and {total_projects} freelance projects across all 32 categories!")
    db.close()

if __name__ == "__main__":
    seed_data(1500)
