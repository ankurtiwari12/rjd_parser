from typing import Dict
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from fpdf import FPDF

# Load a small open-source LLM for demo (distilGPT2)
try:
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilgpt2")
    llm_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)
    LLM_READY = True
except Exception as e:
    llm_pipe = None
    LLM_READY = False

def generate_natural_language_report(match_result: Dict) -> str:
    """
    Generate a natural language report from the match result using an open-source LLM.
    """
    prompt = f"""
You are an expert career coach. Given the following resume-job match analysis, write a detailed, structured report for the candidate in the following format:

Title: Resume-Job Match Report

1. Overall Match:
   - Score: {match_result['overall_match']}%
   - Explanation: Explain what this score means for the candidate's fit for the job.

2. Category Scores:
   - Technical Skills: {match_result['category_scores']['technical_skills']}% (Explain this score)
   - Soft Skills: {match_result['category_scores']['soft_skills']}% (Explain this score)
   - Experience: {match_result['category_scores']['experience']}% (Explain this score)
   - Education: {match_result['category_scores']['education']}% (Explain this score)

3. Good Points / Strengths:
   - List the candidate's strengths and where they exceed requirements.

4. Shortcomings / Missing Skills:
   - List missing technical and soft skills, experience, or education.

5. Recommendations:
   - Provide actionable, specific suggestions for improvement.

6. Feedback:
   - Give a motivational, constructive paragraph to help the candidate improve their job fit.

Here is the analysis:
Overall Match: {match_result['overall_match']}%
Category Scores: {match_result['category_scores']}
Missing Skills: {', '.join(match_result['missing_skills']) if match_result['missing_skills'] else 'None'}
Strengths: {', '.join(match_result['strengths']) if match_result['strengths'] else 'None'}
Recommendations: {chr(10).join(['- ' + rec for rec in match_result['recommendations']]) if match_result['recommendations'] else 'None'}
"""
    if LLM_READY and llm_pipe is not None:
        output = llm_pipe(prompt, max_new_tokens=500, do_sample=True, temperature=0.7)[0]['generated_text']
        # Remove the prompt from the output if present
        report = output[len(prompt):].strip() if output.startswith(prompt) else output.strip()
        # Fallback if the report is too short or missing structure
        if len(report.splitlines()) < 10 or 'Overall Match' not in report or 'Recommendations' not in report:
            report = fallback_report(match_result)
        return report
    else:
        return fallback_report(match_result)

def fallback_report(match_result: Dict) -> str:
    return f"""
Resume-Job Match Report
----------------------

1. Overall Match:
   - Score: {match_result['overall_match']}%
   - Explanation: This score reflects your overall fit for the job based on your skills, experience, and education compared to the job description.

2. Category Scores:
   - Technical Skills: {match_result['category_scores']['technical_skills']}% (Your technical skills match this percentage of the job requirements.)
   - Soft Skills: {match_result['category_scores']['soft_skills']}% (Your soft skills match this percentage of the job requirements.)
   - Experience: {match_result['category_scores']['experience']}% (Your experience matches this percentage of the job requirements.)
   - Education: {match_result['category_scores']['education']}% (Your education matches this percentage of the job requirements.)

3. Good Points / Strengths:
   - {', '.join(match_result['strengths']) if match_result['strengths'] else 'None'}

4. Shortcomings / Missing Skills:
   - {', '.join(match_result['missing_skills']) if match_result['missing_skills'] else 'None'}

5. Recommendations:
   - {chr(10).join(['- ' + rec for rec in match_result['recommendations']]) if match_result['recommendations'] else 'None'}

6. Feedback:
   Keep building on your strengths and address the missing skills or experience. Focus on the recommendations above to improve your job fit and increase your chances of success!
"""

# Placeholder for PDF generation (to be implemented with reportlab or fpdf)
def generate_pdf_report(report_text: str, output_path: str, skill_comparison_table=None) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Split the report into sections
    lines = [line.strip() for line in report_text.splitlines() if line.strip()]
    section_titles = [
        "Resume-Job Match Report", "1. Overall Match:", "2. Category Scores:",
        "3. Good Points / Strengths:", "4. Shortcomings / Missing Skills:",
        "5. Recommendations:", "6. Feedback:"
    ]

    for line in lines:
        if line in section_titles:
            if line == "Resume-Job Match Report":
                pdf.set_font("Arial", "B", 18)
                pdf.cell(0, 12, line, ln=True, align="C")
                pdf.ln(4)
            else:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, line, ln=True)
                pdf.ln(2)
        elif line.startswith("- "):
            pdf.set_font("Arial", "", 12)
            pdf.cell(8)  # Indent
            pdf.multi_cell(0, 8, "- " + line[2:])
        else:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, line)

    # Add skill comparison table if provided
    if skill_comparison_table:
        pdf.ln(6)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Skill Comparison Table", ln=True)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(60, 8, "Skill", border=1, align="C")
        pdf.cell(40, 8, "Required", border=1, align="C")
        pdf.cell(40, 8, "Present", border=1, align="C")
        pdf.ln()
        pdf.set_font("Arial", "", 12)
        for row in skill_comparison_table:
            pdf.cell(60, 8, row["skill"], border=1)
            pdf.cell(40, 8, "Yes" if row["required"] else "No", border=1, align="C")
            pdf.cell(40, 8, "Yes" if row["present"] else "No", border=1, align="C")
            pdf.ln()

    if not output_path.endswith('.pdf'):
        output_path = output_path.rsplit('.', 1)[0] + '.pdf'
    pdf.output(output_path)
    return output_path 