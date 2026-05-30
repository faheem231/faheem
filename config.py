"""
config.py
─────────
Centralised app configuration.
Reads values from Railway environment variables or local .env.
UPDATED: Added SENDGRID_API_KEY, removed SMTP settings
"""
 
import os
from dotenv import load_dotenv
 
load_dotenv()
 
 
class Config:
    # ── Flask ─────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG      = os.getenv("FLASK_DEBUG", "false").lower() == "true"
 
    # ── Base paths ────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
    # ── Uploads ───────────────────────────────────────────────────
    UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
 
    # ── SQLite ────────────────────────────────────────────────────
    DB_FOLDER                    = os.path.join(BASE_DIR, "database")
    SQLALCHEMY_DATABASE_URI      = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'resumes.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    # ── SendGrid (replaces Gmail SMTP — works on Railway) ─────────
    # Get free API key: sendgrid.com → Settings → API Keys → Create
    # Add to Railway Variables: SENDGRID_API_KEY = SG.xxxxxxxxxx
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
 
    # Sender email — must be verified in SendGrid Sender Authentication
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()
 
    # ── Test Mode — redirect all emails here during testing ───────
    TEST_EMAIL_OVERRIDE = os.getenv("TEST_EMAIL_OVERRIDE", "").strip()
 
    # ── App Base URL — used in verification email links ───────────
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000").strip()
 
    # ── University Dataset ────────────────────────────────────────
    UNIVERSITY_DATA = os.path.join(BASE_DIR, "data", "universities.json")
 