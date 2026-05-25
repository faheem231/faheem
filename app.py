"""
app.py
──────
Main Flask application
FIXED: score_breakdown included in API response
ADDED: Dashboard route + API
"""

import os
import json
from collections import Counter
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from database import db, Resume, Analysis, Verification
from resume_parser import extract_text
from nlp_analyzer import analyze_resume
from university_validator import validate_university, validate_email_domain
from emailer import generate_token, send_verification_email


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    CORS(app)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.DB_FOLDER, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Migrate: add score_breakdown_json column if missing
        try:
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE analyses ADD COLUMN score_breakdown_json TEXT DEFAULT '{}'"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    return app


app = create_app()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ── Page Routes ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/result/<int:resume_id>")
def result_page(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if not resume.analysis:
        return "Analysis not found", 404
        
    result_data = resume.analysis.to_dict()
    result_data["ats_score"] = resume.score
    result_data["filename"] = resume.filename
    result_data["filetype"] = resume.filetype
    
    verification = Verification.query.filter_by(resume_id=resume_id).first()
    result_data["university"] = verification.university_name if verification else ""
    result_data["is_verified"] = verification.verified if verification else False
    
    return render_template("result.html", result=result_data)

@app.route("/certifications/<int:resume_id>")
def certifications_page(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if not resume.analysis:
        return "Analysis not found", 404
        
    result_data = resume.analysis.to_dict()
    result_data["ats_score"] = resume.score
    result_data["filename"] = resume.filename
    result_data["filetype"] = resume.filetype
    
    verification = Verification.query.filter_by(resume_id=resume_id).first()
    result_data["university"] = verification.university_name if verification else ""
    result_data["is_verified"] = verification.verified if verification else False
    
    return render_template("certifications.html", result=result_data)

@app.route("/verify")
def verify_page():
    resume_id = request.args.get("resume_id", 0)
    return render_template("verify.html", resume_id=resume_id)


# ── API: Upload ───────────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF/DOCX allowed"}), 400

    original_name = secure_filename(file.filename)
    ext           = original_name.rsplit(".", 1)[1].lower()
    unique_name   = f"{uuid.uuid4().hex}.{ext}"
    filepath      = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    resume = Resume(filename=original_name, filepath=filepath, filetype=ext, status="pending")  # type: ignore
    db.session.add(resume)
    db.session.commit()

    return jsonify({"resume_id": resume.id, "filename": original_name}), 201


# ── API: Analyze ──────────────────────────────────────────────
@app.route("/api/analyze/<int:resume_id>")
def api_analyze(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    # Return cached analysis with stored score_breakdown
    if resume.analysis:
        data = resume.analysis.to_dict()
        data["ats_score"]  = resume.score
        data["filename"]   = resume.filename
        data["resume_id"]  = resume_id
        data["university"] = ""
        return jsonify(data)

    # Fresh analysis
    raw_text = extract_text(resume.filepath)
    if not raw_text.strip():
        return jsonify({"error": "No text extracted"}), 422

    result   = analyze_resume(raw_text)
    uni_name = result.get("university", "")

    analysis = Analysis(  # type: ignore
        resume_id        = resume_id,
        skills_json      = json.dumps(result.get("skills", [])),
        education_json   = json.dumps(result.get("education", [])),
        experience_json  = json.dumps(result.get("experience", [])),
        missing_kw_json  = json.dumps(result.get("missing_keywords", [])),
        suggestions_json = json.dumps(result.get("suggestions", [])),
        domain           = result.get("domain", ""),
        certs_json       = json.dumps(result.get("certifications", [])),
        score_breakdown_json = json.dumps(result.get("score_breakdown", {})),
    )
    db.session.add(analysis)

    resume.score  = result.get("ats_score", 0)
    resume.status = "analyzed"
    db.session.commit()

    if uni_name:
        verification = Verification(resume_id=resume_id, university_name=uni_name)  # type: ignore
        db.session.add(verification)
        db.session.commit()

    # ✅ Return full result including score_breakdown
    return jsonify({
        **result,
        "filename":  resume.filename,
        "resume_id": resume_id,
    })


# ── API: Send Verification Email ──────────────────────────────
@app.route("/api/send-verification", methods=["POST"])
def api_send_verification():
    data      = request.get_json()
    resume_id = data.get("resume_id")
    email     = data.get("email")

    if not resume_id or not email:
        return jsonify({"error": "Missing data"}), 400

    verification = Verification.query.filter_by(resume_id=resume_id).first()
    if not verification:
        verification = Verification(resume_id=resume_id)  # type: ignore
        db.session.add(verification)

    token                    = generate_token()
    verification.email       = email
    verification.verify_token = token
    verification.verified    = False
    db.session.commit()

    uni_name = verification.university_name or "your university"
    result   = send_verification_email(email, uni_name, token, resume_id)
    return jsonify(result)


# ── API: Confirm Email ────────────────────────────────────────
@app.route("/api/confirm-verification/<token>")
def confirm_email(token):
    verification = Verification.query.filter_by(verify_token=token).first()
    if not verification:
        return "Invalid link", 404

    verification.verified     = True
    verification.verify_token = ""
    db.session.commit()

    return "<h2>Email Verified Successfully ✅</h2>"


# ── API: Verification Status ──────────────────────────────────
@app.route("/api/verification-status/<int:resume_id>")
def api_verification_status(resume_id):
    verification = Verification.query.filter_by(resume_id=resume_id).first()
    if not verification:
        return jsonify({"found": False, "university_name": "", "verified": False})

    uni_result = {}
    if verification.university_name:
        uni_result = validate_university(verification.university_name, Config.UNIVERSITY_DATA)
        if uni_result.get("valid") and not verification.university_match:
            verification.university_match = uni_result.get("matched_name", "")
            db.session.commit()

    return jsonify({
        "found":            True,
        "university_name":  verification.university_name,
        "university_match": verification.university_match or uni_result.get("matched_name", ""),
        "valid_university": uni_result.get("valid", False),
        "university_domain":uni_result.get("domain", ""),
        "email":            verification.email,
        "verified":         verification.verified,
    })


# ── API: Dashboard Stats ──────────────────────────────────────
@app.route("/api/dashboard")
def api_dashboard():
    resumes   = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    total     = len(resumes)
    analyzed  = [r for r in resumes if r.status == "analyzed"]
    pending   = total - len(analyzed)
    scores    = [r.score for r in analyzed if r.score is not None]

    avg_score  = round(sum(scores) / len(scores), 1) if scores else 0
    high_score = max(scores) if scores else 0
    low_score  = min(scores) if scores else 0

    # Score distribution buckets
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for s in scores:
        if   s <= 20: buckets["0-20"]   += 1
        elif s <= 40: buckets["21-40"]  += 1
        elif s <= 60: buckets["41-60"]  += 1
        elif s <= 80: buckets["61-80"]  += 1
        else:         buckets["81-100"] += 1

    # Top skills across all analyses
    all_skills = []
    domain_counter = Counter()
    for r in analyzed:
        if r.analysis:
            all_skills.extend(r.analysis.skills)
            if r.analysis.domain:
                domain_counter[r.analysis.domain] += 1

    skill_counts = Counter(all_skills).most_common(15)
    top_skills = [{"name": s, "count": c} for s, c in skill_counts]

    # Domain breakdown
    domains = [{"name": d, "count": c} for d, c in domain_counter.most_common(10)]

    # File type breakdown
    ft_counter = Counter(r.filetype for r in resumes)
    file_types = [{"type": t, "count": c} for t, c in ft_counter.items()]

    # Verification stats
    verifications = Verification.query.all()
    verified_count = sum(1 for v in verifications if v.verified)

    # Recent resumes (last 10)
    recent = []
    for r in resumes[:10]:
        recent.append({
            "id": r.id,
            "filename": r.filename,
            "score": r.score,
            "status": r.status,
            "filetype": r.filetype,
            "uploaded_at": r.uploaded_at.isoformat(),
            "domain": r.analysis.domain if r.analysis else "",
        })

    # Score trend (chronological order for chart)
    trend = []
    for r in reversed(analyzed[-20:]):
        trend.append({
            "filename": r.filename[:20],
            "score": r.score,
            "date": r.uploaded_at.strftime("%b %d"),
        })

    return jsonify({
        "total_resumes":   total,
        "analyzed_count":  len(analyzed),
        "pending_count":   pending,
        "avg_score":       avg_score,
        "high_score":      high_score,
        "low_score":       low_score,
        "score_distribution": buckets,
        "top_skills":      top_skills,
        "domains":         domains,
        "file_types":      file_types,
        "verified_count":  verified_count,
        "total_verifications": len(verifications),
        "recent_resumes":  recent,
        "score_trend":     trend,
    })


# ── Error Handlers ────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Server running at http://127.0.0.1:5000")
    app.run(debug=True)