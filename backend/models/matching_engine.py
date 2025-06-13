from sentence_transformers import SentenceTransformer, util
from utils.skill_extraction import TECH_SKILLS, SOFT_SKILLS, CERTIFICATIONS
from typing import Dict, List
import numpy as np

# Load Sentence-BERT model (use a small, fast model for demo)
model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_skill_comparison_table(resume_skills, jd_skills):
    # Both are sets
    all_skills = sorted(set(jd_skills) | set(resume_skills))
    table = []
    for skill in all_skills:
        table.append({
            "skill": skill,
            "required": skill in jd_skills,
            "present": skill in resume_skills
        })
    return table

def match_resume_to_jd(resume_text: str, jd_text: str, resume_entities: Dict, jd_entities: Dict) -> Dict:
    # Semantic similarity (overall)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    overall_match = float(util.pytorch_cos_sim(resume_emb, jd_emb).item() * 100)

    # Skill alignment
    resume_skills = set(resume_entities['skills'])
    jd_skills = set(jd_entities['skills'])
    matched_skills = resume_skills & jd_skills
    missing_skills = list(jd_skills - resume_skills)
    strengths = list(resume_skills & jd_skills)
    skill_score = (len(matched_skills) / max(1, len(jd_skills))) * 100 if jd_skills else 0

    # Soft skills
    resume_soft = set(resume_entities['entities']['soft_skills'])
    jd_soft = set(jd_entities['entities']['soft_skills'])
    matched_soft = resume_soft & jd_soft
    missing_soft = list(jd_soft - resume_soft)
    soft_score = (len(matched_soft) / max(1, len(jd_soft))) * 100 if jd_soft else 0

    # Certifications
    resume_cert = set(resume_entities['entities']['certifications'])
    jd_cert = set(jd_entities['entities']['certifications'])
    matched_cert = resume_cert & jd_cert
    missing_cert = list(jd_cert - resume_cert)
    cert_score = (len(matched_cert) / max(1, len(jd_cert))) * 100 if jd_cert else 0

    # Experience/Education (simple heuristic: count years/degree keywords)
    def extract_years(text):
        import re
        years = re.findall(r'(\d+)\s+years?', text.lower())
        return int(years[0]) if years else 0
    resume_years = extract_years(resume_text)
    jd_years = extract_years(jd_text)
    exp_score = min(100, (resume_years / max(1, jd_years)) * 100) if jd_years else 0

    # Education (look for degree keywords)
    DEGREE_KEYWORDS = ["bachelor", "master", "phd", "b.sc", "m.sc", "b.tech", "m.tech"]
    def has_degree(text):
        return any(degree in text.lower() for degree in DEGREE_KEYWORDS)
    resume_degree = has_degree(resume_text)
    jd_degree = has_degree(jd_text)
    edu_score = 100 if resume_degree == jd_degree else 0

    category_scores = {
        "technical_skills": round(skill_score, 1),
        "soft_skills": round(soft_score, 1),
        "experience": round(exp_score, 1),
        "education": round(edu_score, 1)
    }
    # Weighted overall match (semantic 40%, skills 30%, soft 10%, exp 10%, edu 10%)
    weighted_match = (
        0.4 * overall_match +
        0.3 * skill_score +
        0.1 * soft_score +
        0.1 * exp_score +
        0.1 * edu_score
    )
    # Recommendations (simple for now)
    recommendations = []
    if missing_skills:
        recommendations.append(f"Consider learning: {', '.join(missing_skills)}.")
    if missing_soft:
        recommendations.append(f"Develop soft skills: {', '.join(missing_soft)}.")
    if missing_cert:
        recommendations.append(f"Certifications to pursue: {', '.join(missing_cert)}.")
    if not resume_degree and jd_degree:
        recommendations.append("Consider obtaining the required degree.")
    if resume_years < jd_years:
        recommendations.append(f"You have {resume_years} years experience, but {jd_years} required.")
    skill_comparison_table = compute_skill_comparison_table(resume_skills, jd_skills)
    return {
        "overall_match": round(weighted_match, 1),
        "category_scores": category_scores,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "recommendations": recommendations,
        "skill_comparison_table": skill_comparison_table
    } 