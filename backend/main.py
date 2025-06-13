from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
import os
from utils.text_extraction import extract_text_from_file
from utils.skill_extraction import extract_entities_and_skills
from models.matching_engine import match_resume_to_jd
from models.report_generation import generate_natural_language_report, generate_pdf_report
import uuid
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="RJD Parser [Resume - Job Description Parser]")

app.mount("/data", StaticFiles(directory="data"), name="data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload_resume/")
def upload_resume(resume_file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, resume_file.filename)
    with open(file_path, "wb") as f:
        f.write(resume_file.file.read())
    try:
        text = extract_text_from_file(file_path)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    return {"filename": resume_file.filename, "text": text}

@app.post("/api/analyze/parse_jd/")
def parse_jd(jd_text: str = Form(...)):
    # For now, just echo back the text
    return {"jd_text": jd_text}

@app.post("/api/skills/extract")
def skills_extract(text: str = Form(...)):
    result = extract_entities_and_skills(text)
    return result

@app.post("/api/analyze/match")
def analyze_match(resume_file: UploadFile = File(...), job_description: str = Form(...)):
    # Save and extract resume text
    file_path = os.path.join(UPLOAD_DIR, resume_file.filename)
    with open(file_path, "wb") as f:
        f.write(resume_file.file.read())
    resume_text = extract_text_from_file(file_path)
    # Extract skills/entities
    resume_entities = extract_entities_and_skills(resume_text)
    jd_entities = extract_entities_and_skills(job_description)
    # Call matching engine
    match_result = match_resume_to_jd(resume_text, job_description, resume_entities, jd_entities)
    return {
        "resume_entities": resume_entities,
        "jd_entities": jd_entities,
        "match_result": match_result
    }

@app.post("/api/reports/generate")
def generate_report(request: Request):
    import asyncio
    async def get_json():
        return await request.json()
    match_result = asyncio.run(get_json())['match_result']
    report_text = generate_natural_language_report(match_result)
    report_id = str(uuid.uuid4())
    output_path = f"data/{report_id}_report.pdf"
    skill_comparison_table = match_result.get("skill_comparison_table")
    generate_pdf_report(report_text, output_path, skill_comparison_table=skill_comparison_table)
    return {"pdf_url": output_path} 