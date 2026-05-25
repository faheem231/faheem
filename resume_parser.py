"""
resume_parser.py
────────────────
Extracts raw text from PDF and DOCX resume files.
Supports:
  - PDF  → pdfplumber (primary) with PyPDF2 fallback
  - DOCX → python-docx
"""

import os
import pdfplumber
import PyPDF2
from docx import Document


def extract_text(filepath: str) -> str:
    """
    Main entry point. Detect file type and delegate to the correct parser.

    Args:
        filepath: Absolute path to the uploaded resume file.

    Returns:
        Extracted plain text as a single string.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return _parse_pdf(filepath)
    elif ext == ".docx":
        return _parse_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _parse_pdf(filepath: str) -> str:
    """
    Parse a PDF file using pdfplumber.
    Falls back to PyPDF2 if pdfplumber fails (e.g. scanned/encrypted PDFs).
    """
    text = ""

    # ── Primary: pdfplumber (handles tables + multi-column layouts better) ──
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception:
        pass  # Fall through to PyPDF2

    # ── Fallback: PyPDF2 ──────────────────────────────────────────────────
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")

    return text.strip()


def _parse_docx(filepath: str) -> str:
    """
    Parse a DOCX file using python-docx.
    Reads every paragraph in the main document body.
    """
    try:
        doc = Document(filepath)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX: {e}")
