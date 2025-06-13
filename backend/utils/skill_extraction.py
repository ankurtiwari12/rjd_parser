import spacy
from typing import List, Dict
from rapidfuzz import fuzz, process

# Try to load transformer-based NER if available
try:
    nlp = spacy.load("en_core_web_trf")
except Exception:
    nlp = spacy.load("en_core_web_sm")

# Example expanded skill/tech/certification/soft skill lists (expand as needed)
TECH_SKILLS = [
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "ruby", "php", "swift", "kotlin", "scala", "rust", "perl", "matlab", "r", "objective-c", "bash", "shell", "powershell",
    # Web/Frontend
    "html", "css", "sass", "less", "react", "angular", "vue.js", "next.js", "nuxt.js", "redux", "jquery", "bootstrap", "tailwindcss", "material-ui",
    # Backend/Frameworks
    "node.js", "express", "django", "flask", "spring", "spring boot", "dotnet", ".net", "laravel", "rails", "fastapi", "gin", "hapi", "symfony", "cakephp",
    # Databases
    "mysql", "postgresql", "sqlite", "mongodb", "redis", "cassandra", "oracle", "mariadb", "dynamodb", "elasticsearch", "firebase", "couchdb", "neo4j",
    # Cloud/DevOps
    "aws", "azure", "gcp", "google cloud", "heroku", "docker", "kubernetes", "jenkins", "travis ci", "circleci", "gitlab ci", "terraform", "ansible", "puppet", "chef", "vagrant", "openshift", "cloudformation", "helm",
    # Data/ML/AI
    "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "keras", "pytorch", "matplotlib", "seaborn", "xgboost", "lightgbm", "nltk", "spacy", "opencv", "hadoop", "spark", "hive", "pig", "tableau", "power bi", "qlikview",
    # Tools/Other
    "git", "svn", "jira", "confluence", "slack", "trello", "microsoft office", "excel", "word", "powerpoint", "visio", "outlook", "figma", "adobe xd", "photoshop", "illustrator", "after effects", "premiere pro", "unity", "unreal engine", "blender", "autocad", "solidworks", "sap", "salesforce", "zoho", "hubspot", "mailchimp", "wordpress", "shopify", "magento", "woocommerce", "woocommerce", "woocommerce", "woocommerce"
]
SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "adaptability", "creativity", "time management", "critical thinking", "collaboration", "initiative", "work ethic", "empathy", "conflict resolution", "negotiation", "public speaking", "presentation", "decision making", "organization", "attention to detail", "customer service", "emotional intelligence", "resilience", "stress management", "self-motivation", "accountability", "flexibility", "active listening", "mentoring", "coaching", "delegation", "influencing", "networking", "strategic thinking", "goal setting", "multitasking", "resourcefulness"
]
CERTIFICATIONS = [
    "aws certified", "pmp", "scrum master", "oracle certified", "microsoft certified", "gcp certified", "azure certified"
]

# Fuzzy matching helper
def fuzzy_skill_match(text: str, skill_list: List[str], threshold: int = 85) -> List[str]:
    found = set()
    for skill in skill_list:
        if process.extractOne(skill, [text], scorer=fuzz.token_set_ratio)[1] >= threshold:
            found.add(skill)
    # Also check for each word in text
    for word in text.lower().split():
        match, score, _ = process.extractOne(word, skill_list, scorer=fuzz.token_set_ratio)
        if score >= threshold:
            found.add(match)
    return list(found)

def extract_entities_and_skills(text: str) -> Dict:
    doc = nlp(text)
    entities = {"technologies": set(), "certifications": set(), "soft_skills": set(), "other": set()}
    found_skills = set()
    # spaCy NER
    for ent in doc.ents:
        ent_text = ent.text.lower()
        if ent.label_ in ["ORG", "PRODUCT"]:
            for skill in fuzzy_skill_match(ent_text, TECH_SKILLS):
                entities["technologies"].add(skill)
        elif ent.label_ == "PERSON":
            for skill in fuzzy_skill_match(ent_text, SOFT_SKILLS):
                entities["soft_skills"].add(skill)
        elif ent.label_ == "ORG":
            for cert in fuzzy_skill_match(ent_text, CERTIFICATIONS):
                entities["certifications"].add(cert)
        else:
            entities["other"].add(ent.text)
    # Fuzzy skill matching for the whole text
    for skill in fuzzy_skill_match(text, TECH_SKILLS):
        found_skills.add(skill)
    for skill in fuzzy_skill_match(text, SOFT_SKILLS):
        entities["soft_skills"].add(skill)
    for cert in fuzzy_skill_match(text, CERTIFICATIONS):
        entities["certifications"].add(cert)
    return {
        "skills": list(found_skills),
        "entities": {k: list(v) for k, v in entities.items()}
    } 