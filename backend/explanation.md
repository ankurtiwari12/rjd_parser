# RJD Parser [Resume - Job Description Parser]: Project Explanation

## 1. Project Overview & Motivation
This project is a full-stack, AI-powered tool that matches a candidate's resume to a job description (JD) using advanced NLP and ML. It extracts skills/entities, computes semantic and categorical matches, and generates a detailed, actionable report (including a skill gap table). The goal is to help candidates (or recruiters) quickly assess fit and identify improvement areas.

## 2. Tech Stack
- **Backend:** FastAPI (Python), spaCy (en_core_web_trf), Sentence-BERT, rapidfuzz, fpdf, HuggingFace transformers
- **Frontend:** Next.js (React, TypeScript), Tailwind CSS
- **Other:** PyPDF2, python-docx (for file extraction)

**Why this stack?**
- FastAPI: Fast, async, easy to document/test
- spaCy: Robust NER/entity extraction, transformer support
- Sentence-BERT: State-of-the-art semantic similarity
- rapidfuzz: Fast fuzzy skill matching
- Next.js/Tailwind: Modern, responsive UI/UX

## 3. Backend Pipeline & Code Structure
- **Entry Point:** `backend/main.py` (FastAPI app, all endpoints)
- **Text Extraction:** `utils/text_extraction.py` (PDF/DOCX to text)
- **Entity/Skill Extraction:** `utils/skill_extraction.py` (spaCy NER + fuzzy matching, large skill DB)
- **Matching Engine:** `models/matching_engine.py` (semantic similarity, category scores, skill/soft/cert/exp/edu analysis, recommendations, skill table)
- **Report Generation:** `models/report_generation.py` (LLM or fallback template, PDF with ASCII skill table)

**Pipeline Steps:**
1. **Input:** Resume (file) + JD (text)
2. **Extraction:** Text extraction from file
3. **Entity Recognition:** spaCy NER (transformer if available)
4. **Skill Extraction:** Fuzzy match against large skill DB
5. **Embedding:** Sentence-BERT for semantic similarity
6. **Similarity/Scoring:** Cosine similarity + category scores
7. **Gap Analysis:** Find missing/extra skills, soft skills, certs, exp, edu
8. **Recommendations:** Actionable suggestions
9. **Results:** JSON for frontend, PDF report (with skill table)

## 4. Frontend Structure & UX
- **File:** `frontend/src/app/page.tsx`
- **Flow:**
  1. Upload resume (drag/drop or click)
  2. Paste JD
  3. Click "Analyze" → shows match, strengths, missing skills, recommendations, skill table
  4. Click "Generate PDF Report" → downloads detailed report
- **UI:** Modern, accessible, color-coded, responsive (Tailwind)
- **Skill Table:** Side-by-side, color-coded, bold/dark text for readability

## 5. Key Code Explanations
- **Skill Extraction:** Uses spaCy NER + rapidfuzz fuzzy match over a large curated skill list (tech, soft, certs)
- **Matching:** Sentence-BERT for semantic similarity, plus category scores (skills, soft, certs, exp, edu)
- **Skill Table:** Backend computes a table of all relevant skills, marking required/present; shown in frontend and PDF (ASCII for PDF)
- **Report Generation:** Uses HuggingFace LLM (if available) for natural language report, else fallback template; PDF generated with fpdf

## 6. Extending/Customizing
- Add more skills/certs to `utils/skill_extraction.py`
- Swap out Sentence-BERT model for higher accuracy (at cost of speed)
- Add more detailed experience/education parsing
- Add authentication, user accounts, or analytics
- Improve LLM prompt or use a more powerful model

## 7. Interviewer Talking Points
- End-to-end ML/NLP pipeline, not just keyword matching
- Modular, extensible codebase (easy to add skills, models, features)
- Modern, user-friendly UI/UX
- Handles Unicode/PDF/report edge cases robustly
- Clear separation of concerns (extraction, matching, reporting, UI)
- Designed for both demo and real-world extensibility

---
**For more, see the code comments and README for setup/running instructions.** 