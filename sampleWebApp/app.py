from flask import Flask, render_template, request, Response
import re
import pdfplumber
from docx import Document
from io import BytesIO
import random
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

app = Flask(__name__)

# =====================
# Prometheus Metrics
# =====================
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint", "status"]
)

# =====================
# App Configuration
# =====================
ALLOWED_EXTENSIONS = {"pdf", "docx"}

SKILL_LIST = [
    "python", "azure", "aws", "docker", "kubernetes", "machine learning",
    "data analysis", "sql", "javascript", "react", "node.js", "git",
    "linux", "html", "css", "ci/cd", "terraform", "ansible", "splunk",
    "bash", "power bi", "tableau", "excel", "jira", "confluence",
    "agile", "scrum", "rest api", "graphql", "nosql", "mongodb",
    "postgresql", "mysql", "redis", "rabbitmq", "apache kafka"
]

# =====================
# Helper Functions
# =====================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf(file_stream):
    with pdfplumber.open(file_stream) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_docx(file_stream):
    doc = Document(file_stream)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_resume_text(file):
    content = BytesIO(file.read())
    # =====================
    # Auto-healing: retry reading up to 2 times if file extraction fails
    # =====================
    retries = 2
    while retries > 0:
        try:
            if file.filename.endswith(".pdf"):
                return extract_pdf(content)
            if file.filename.endswith(".docx"):
                return extract_docx(content)
            return ""
        except Exception as e:
            print("Error extracting resume, retrying...", e)
            retries -= 1
            time.sleep(1)
    return ""  # return empty string if all retries fail

def extract_skills(text):
    text = text.lower()
    skills_found = []
    for skill in SKILL_LIST:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            skills_found.append(skill)
    return skills_found

def extract_candidate_details(text):
    details = {}
    email = re.search(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    details["email"] = email.group() if email else "Not Found"
    phone = re.search(r"\b\d{10}\b", text)
    details["phone"] = phone.group() if phone else "Not Found"
    details["name"] = text.strip().split("\n")[0]
    exp = re.search(r"(\d+)\s+years?\s+of\s+experience", text.lower())
    details["experience"] = exp.group() if exp else "Not Mentioned"
    edu = re.search(r"(bachelor's|master's|phd|b\.sc|m\.sc|btech|mtech|mba)", text.lower())
    details["education"] = edu.group() if edu else "Not Mentioned"
    return details

def calculate_score(jd_text, resume_text):
    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))
    if not jd_skills:
        return 0, [], []
    matched = resume_skills.intersection(jd_skills)
    missed = jd_skills.difference(resume_skills)
    score = round((len(matched) / len(jd_skills)) * 100, 2)
    return score, list(matched), list(missed)

# =====================
# Chaos Testing: simulate random failures
# =====================
def maybe_inject_chaos():
    """Randomly raise an exception to simulate failure (10% chance)"""
    if random.random() < 0.1:  # 10% probability
        raise Exception("💥 Chaos injected! Simulated failure.")

# =====================
# Routes
# =====================
@app.route("/", methods=["GET", "POST"])
def index():
    start_time = time.time()
    try:
        maybe_inject_chaos()  # chaos injection
        results = []

        if request.method == "POST":
            user_role = request.form.get("role")
            if user_role == "job_seeker":
                resumes = request.files.getlist("resumes")
                jd_text = request.form.get("jd", "")
                for file in resumes:
                    if not allowed_file(file.filename):
                        continue
                    resume_text = extract_resume_text(file)  # auto-healing built-in
                    candidate = extract_candidate_details(resume_text)
                    score, matched, missed = calculate_score(jd_text, resume_text)
                    candidate.update({
                        "resume": file.filename,
                        "score": score,
                        "skills": matched,
                        "missed": missed,
                        "improvements": missed
                    })
                    results.append(candidate)
                results.sort(key=lambda x: x["score"], reverse=True)
                REQUEST_COUNT.labels("POST", "/", "200").inc()
                return render_template("job_seeker_results.html", results=results)

            elif user_role == "hiring_team":
                jd_text = request.form.get("jd_text", "")
                job_seekers = request.files.getlist("job_seekers")
                for file in job_seekers:
                    if not allowed_file(file.filename):
                        continue
                    resume_text = extract_resume_text(file)
                    candidate = extract_candidate_details(resume_text)
                    score, matched, missed = calculate_score(jd_text, resume_text)
                    candidate.update({
                        "resume": file.filename,
                        "score": score,
                        "skills": matched,
                        "missed": missed,
                        "improvements": missed
                    })
                    results.append(candidate)
                results.sort(key=lambda x: x["score"], reverse=True)
                REQUEST_COUNT.labels("POST", "/", "200").inc()
                return render_template("hiring_team_results.html", results=results)

        REQUEST_COUNT.labels("GET", "/", "200").inc()
        return render_template("index.html")

    except Exception as e:
        print("Error:", e)
        REQUEST_COUNT.labels(request.method, "/", "500").inc()
        return f"Internal Server Error: {e}", 500

    finally:
        elapsed = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint="/",
            status="200"  # optionally dynamic
        ).observe(elapsed)

# =====================
# Metrics Endpoint
# =====================
@app.route("/metrics")
def metrics():
    try:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    except Exception as e:
        print("Metrics error:", e)
        return "Error generating metrics", 500

# =====================
# Run App
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)