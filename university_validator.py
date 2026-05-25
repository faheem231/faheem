"""
university_validator.py
────────────────────────
Detects the university name from a resume and validates it
against a local dataset of universities.

Uses fuzzy matching (thefuzz) to handle slight spelling variations.
"""

import json
import re
import os

try:
    from thefuzz import process as fuzz_process
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# LOAD UNIVERSITY DATASET
# ─────────────────────────────────────────────────────────────────────────────

_UNIVERSITIES = []  # List of dicts: {name, domain, country}

def _load_universities(data_path: str):
    global _UNIVERSITIES
    if _UNIVERSITIES:
        return  # Already loaded
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            _UNIVERSITIES = json.load(f)
    except Exception as e:
        print(f"[university_validator] Could not load universities.json: {e}")
        _UNIVERSITIES = []


def get_all_names(data_path: str) -> list:
    _load_universities(data_path)
    return [u["name"] for u in _UNIVERSITIES]


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSITY DETECTION FROM RAW RESUME TEXT
# ─────────────────────────────────────────────────────────────────────────────

# Common university title keywords
UNIVERSITY_KEYWORDS = [
    "university", "college", "institute", "institution", "polytechnic",
    "academy", "school of", "iit", "nit", "iiit", "mit", "iisc",
]

def detect_university_from_text(text: str) -> str:
    """
    Scan resume text for lines that likely contain a university name.
    Returns the best candidate line (or empty string if none found).
    """
    lines = text.split("\n")
    candidates = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        line_lower = line_stripped.lower()

        for kw in UNIVERSITY_KEYWORDS:
            if kw in line_lower:
                # Avoid capturing very long lines (likely not a university name)
                if 5 < len(line_stripped) < 120:
                    candidates.append(line_stripped)
                break

    # Return the first candidate (most likely near the Education section)
    return candidates[0] if candidates else ""


# ─────────────────────────────────────────────────────────────────────────────
# FUZZY VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_university(name: str, data_path: str, threshold: int = 70) -> dict:
    """
    Fuzzy-match a detected university name against the dataset.

    Args:
        name:       Detected university name from the resume.
        data_path:  Path to universities.json.
        threshold:  Minimum fuzzy score (0-100) to consider a match valid.

    Returns:
        {
            "valid": bool,
            "matched_name": str,
            "domain": str,       # e.g. "mit.edu"
            "country": str,
            "score": int,        # fuzzy score
        }
    """
    _load_universities(data_path)

    if not name or not _UNIVERSITIES:
        return {"valid": False, "matched_name": "", "domain": "", "country": "", "score": 0}

    all_names = [u["name"] for u in _UNIVERSITIES]

    if FUZZ_AVAILABLE:
        result = fuzz_process.extractOne(name, all_names, score_cutoff=threshold)
        if result:
            matched_name, score = result[0], result[1]
            # Find the university details
            uni = next((u for u in _UNIVERSITIES if u["name"] == matched_name), {})
            return {
                "valid": True,
                "matched_name": matched_name,
                "domain": uni.get("domain", ""),
                "country": uni.get("country", ""),
                "score": score,
            }
    else:
        # Simple fallback: case-insensitive substring match
        name_lower = name.lower()
        for uni in _UNIVERSITIES:
            if name_lower in uni["name"].lower() or uni["name"].lower() in name_lower:
                return {
                    "valid": True,
                    "matched_name": uni["name"],
                    "domain": uni.get("domain", ""),
                    "country": uni.get("country", ""),
                    "score": 80,
                }

    return {"valid": False, "matched_name": "", "domain": "", "country": "", "score": 0}


def validate_email_domain(email: str, expected_domain: str) -> bool:
    """
    Check if the given email address ends with the university's domain.
    e.g. student@mit.edu  →  matches mit.edu
    """
    if not email or not expected_domain:
        return False
    email_domain = email.split("@")[-1].lower().strip()
    return email_domain.endswith(expected_domain.lower().strip())
