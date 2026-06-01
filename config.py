"""
config.py
─────────
Centralised app configuration.
Reads values from Railway environment variables or local .env.
"""

import os
from dotenv import load_dotenv

# Base directory of project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicitly load .env from project root
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

# Debug (remove later)
print(f"Loading .env from: {ENV_PATH}")
print(f"SENDGRID_API_KEY found: {bool(os.getenv('SENDGRID_API_KEY'))}")


class Config:
    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # ── Base Paths ─────────────────────────────────────────
    BASE_DIR = BASE_DIR

    # ── Uploads ────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # ── Database ───────────────────────────────────────────
    DB_FOLDER = os.path.join(BASE_DIR, "database")
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(DB_FOLDER, 'resumes.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── SendGrid ───────────────────────────────────────────
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()

    # Verified sender email in SendGrid
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()

    # ── Test Mode ──────────────────────────────────────────
    TEST_EMAIL_OVERRIDE = os.getenv(
        "TEST_EMAIL_OVERRIDE", ""
    ).strip()

    # ── App Base URL ───────────────────────────────────────
    APP_BASE_URL = os.getenv(
        "APP_BASE_URL",
        "http://127.0.0.1:5000"
    ).strip()

    # ── University Dataset ─────────────────────────────────
    UNIVERSITY_DATA = os.path.join(
        BASE_DIR,
        "data",
        "universities.json"
    )