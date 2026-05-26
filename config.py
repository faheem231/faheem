"""
config.py
─────────
Centralised app configuration.
Reads values from .env via python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    # ── Flask ────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ── File uploads ─────────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # ── SQLite database ───────────────────────────────────────────────────
    DB_FOLDER = os.path.join(BASE_DIR, "database")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DB_FOLDER, 'resumes.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Email (Gmail SMTP) ────────────────────────────────────────────────
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").strip()  # ← .strip() removes spaces Google adds in App Password display

    # ── Test mode: redirect ALL emails to this address ────────────────────
    # Set TEST_EMAIL_OVERRIDE in .env to intercept emails during development.
    # Leave blank (or unset) to send to the actual address entered by user.
    TEST_EMAIL_OVERRIDE = os.getenv("TEST_EMAIL_OVERRIDE", "").strip()

    # ── App base URL (used in verification links) ─────────────────────────
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000").strip()

    # ── University dataset ────────────────────────────────────────────────
    UNIVERSITY_DATA = os.path.join(BASE_DIR, "data", "universities.json")