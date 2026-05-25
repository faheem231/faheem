"""
database.py
───────────
SQLite database models using Flask-SQLAlchemy.
Three tables: Resume, Analysis, Verification.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()  # type: ignore[arg-type]


class Resume(db.Model):
    """Stores uploaded resume metadata."""
    __tablename__ = "resumes"

    id         = db.Column(db.Integer, primary_key=True)
    filename   = db.Column(db.String(255), nullable=False)        # Original filename
    filepath   = db.Column(db.String(512), nullable=False)        # Server-side path
    filetype   = db.Column(db.String(10), nullable=False)         # 'pdf' or 'docx'
    uploaded_at= db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    score      = db.Column(db.Float, default=0.0)                 # ATS score 0-100
    status     = db.Column(db.String(50), default="pending")      # pending/analyzed

    # Relationships
    analysis   = db.relationship("Analysis", backref="resume", uselist=False)
    verification = db.relationship("Verification", backref="resume", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filetype": self.filetype,
            "uploaded_at": self.uploaded_at.isoformat(),
            "score": self.score,
            "status": self.status,
        }


class Analysis(db.Model):
    """Stores NLP analysis results for a resume."""
    __tablename__ = "analyses"

    id               = db.Column(db.Integer, primary_key=True)
    resume_id        = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    skills_json      = db.Column(db.Text, default="[]")      # JSON list of skills
    education_json   = db.Column(db.Text, default="[]")      # JSON list of education entries
    experience_json  = db.Column(db.Text, default="[]")      # JSON list of experience entries
    missing_kw_json  = db.Column(db.Text, default="[]")      # JSON list of missing keywords
    suggestions_json = db.Column(db.Text, default="[]")      # JSON list of suggestions
    domain           = db.Column(db.String(100), default="")  # Detected domain
    certs_json       = db.Column(db.Text, default="[]")      # Suggested certifications
    score_breakdown_json = db.Column(db.Text, default="{}")   # JSON score breakdown
    analyzed_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Helper properties for JSON fields
    @property
    def skills(self):
        return json.loads(self.skills_json)

    @property
    def education(self):
        return json.loads(self.education_json)

    @property
    def experience(self):
        return json.loads(self.experience_json)

    @property
    def missing_keywords(self):
        return json.loads(self.missing_kw_json)

    @property
    def suggestions(self):
        return json.loads(self.suggestions_json)

    @property
    def certifications(self):
        return json.loads(self.certs_json)

    @property
    def score_breakdown(self):
        return json.loads(self.score_breakdown_json) if self.score_breakdown_json else {}

    def to_dict(self):
        return {
            "resume_id": self.resume_id,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "missing_keywords": self.missing_keywords,
            "suggestions": self.suggestions,
            "domain": self.domain,
            "certifications": self.certifications,
            "score_breakdown": self.score_breakdown,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class Verification(db.Model):
    """Stores university verification status for a resume."""
    __tablename__ = "verifications"

    id              = db.Column(db.Integer, primary_key=True)
    resume_id       = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    university_name = db.Column(db.String(255), default="")
    university_match= db.Column(db.String(255), default="")  # Matched university name
    email           = db.Column(db.String(255), default="")
    verified        = db.Column(db.Boolean, default=False)
    verify_token    = db.Column(db.String(64), default="")   # Email verification token
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "resume_id": self.resume_id,
            "university_name": self.university_name,
            "university_match": self.university_match,
            "email": self.email,
            "verified": self.verified,
            "created_at": self.created_at.isoformat(),
        }
