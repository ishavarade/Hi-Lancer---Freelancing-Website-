import re
from typing import Dict, Any, List

EXTERNAL_ATS_PLATFORMS = [
    {
        "name": "Jobscan ATS Resume Checker",
        "url": "https://www.jobscan.co/",
        "description": "Analyze your resume against job descriptions to pass applicant tracking systems (ATS).",
        "badge": "Top ATS API Partner"
    },
    {
        "name": "ResumeWorded ATS Analyzer",
        "url": "https://resumeworded.com/",
        "description": "Get instant feedback on your resume's impact, keywords, and ATS formatting score.",
        "badge": "Popular"
    },
    {
        "name": "Zety Resume Checker API",
        "url": "https://zety.com/resume-checker",
        "description": "Scan resume for grammar, readability, section headers, and ATS compliance.",
        "badge": "Free Scan"
    }
]

IMPORTANT_ATS_KEYWORDS = [
    "python", "flask", "fastapi", "postgresql", "sql", "machine learning", "nlp", "transformers",
    "docker", "aws", "react", "rest api", "git", "ci/cd", "scikit-learn", "pandas", "numpy",
    "agile", "microservices", "unit testing", "system architecture"
]

def analyze_resume_ats(resume_text: str, target_job_title: str = "") -> Dict[str, Any]:
    if not resume_text:
        return {
            "ats_score": 0,
            "formatting_score": 0,
            "keyword_match_pct": 0,
            "found_keywords": [],
            "missing_keywords": IMPORTANT_ATS_KEYWORDS[:8],
            "suggestions": ["Please upload or paste your resume text to perform ATS evaluation."],
            "external_ats_platforms": EXTERNAL_ATS_PLATFORMS
        }

    text_lower = resume_text.lower()

    found_kw = []
    missing_kw = []

    for kw in IMPORTANT_ATS_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            found_kw.append(kw.title())
        else:
            missing_kw.append(kw.title())

    keyword_pct = round((len(found_kw) / len(IMPORTANT_ATS_KEYWORDS)) * 100, 1)

    # Formatting checks
    has_contact = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text) or re.search(r'\+?\d[\d -]{8,}\d', resume_text))
    has_sections = any(sec in text_lower for sec in ["experience", "education", "skills", "projects", "summary"])
    word_count = len(resume_text.split())

    formatting_score = 100
    suggestions = []

    if not has_contact:
        formatting_score -= 20
        suggestions.append("Add clear contact information (email address and phone number) at the top of your resume.")
    if not has_sections:
        formatting_score -= 25
        suggestions.append("Use standard ATS section headings like 'Work Experience', 'Skills', and 'Education'.")
    if word_count < 150:
        formatting_score -= 25
        suggestions.append("Expand your work experience and key project bullet points (aim for 300+ words).")

    final_ats_score = round((0.60 * keyword_pct) + (0.40 * max(0, formatting_score)), 1)

    if final_ats_score >= 80:
        overall_status = "Excellent - Highly ATS Compliant"
    elif final_ats_score >= 60:
        overall_status = "Good - Needs Minor Keyword Optimization"
    else:
        overall_status = "Needs Improvement - Low Keyword Alignment"

    return {
        "ats_score": final_ats_score,
        "formatting_score": max(0, formatting_score),
        "keyword_match_pct": keyword_pct,
        "overall_status": overall_status,
        "word_count": word_count,
        "found_keywords": found_kw,
        "missing_keywords": missing_kw[:8],
        "suggestions": suggestions if suggestions else ["Your resume structure and keyword density are well optimized for ATS scanners!"],
        "external_ats_platforms": EXTERNAL_ATS_PLATFORMS
    }
