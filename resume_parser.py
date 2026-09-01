"""
resume_parser.py
-----------------
Extracts raw text and structured information (name hint, email, phone,
skills, education, years of experience) from a resume file (.pdf, .docx,
or .txt) using rule-based / regex techniques -- no external API calls,
so it works completely offline.
"""

import os
import re
from typing import Dict, List

import pdfplumber
import docx

from skills_db import ALL_SKILLS, DEGREE_KEYWORDS

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}"
)
EXPERIENCE_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)\s*(?:of)?\s*(?:experience)?",
    re.IGNORECASE,
)
LINKEDIN_REGEX = re.compile(r"(https?://)?(www\.)?linkedin\.com/[A-Za-z0-9\-_/]+")
GITHUB_REGEX = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+")


def extract_text(file_path: str) -> str:
    """Extract raw text from a PDF, DOCX, or TXT file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text_chunks = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
        return "\n".join(text_chunks)

    if ext == ".docx":
        document = docx.Document(file_path)
        return "\n".join(p.text for p in document.paragraphs if p.text)

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file format: {ext}. Use .pdf, .docx, or .txt")


def extract_email(text: str) -> str:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    for match in PHONE_REGEX.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 13:
            return candidate.strip()
    return ""


def extract_links(text: str) -> Dict[str, str]:
    linkedin = LINKEDIN_REGEX.search(text)
    github = GITHUB_REGEX.search(text)
    return {
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }


def extract_name(text: str) -> str:
    """
    Heuristic: the resume's name is usually the first non-empty line
    that doesn't look like an email, phone number, or address/section header.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:
        if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
            continue
        if len(line.split()) <= 5 and not any(ch.isdigit() for ch in line):
            return line
    return "Unknown"


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for skill in ALL_SKILLS:
        # word-boundary-ish match; handles multi-word skills like "machine learning"
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)


def extract_education(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for degree in DEGREE_KEYWORDS:
        if degree in text_lower:
            found.add(degree.strip("."))
    return sorted(found)


def extract_experience_years(text: str) -> float:
    matches = EXPERIENCE_REGEX.findall(text)
    years = [float(m) for m in matches if m]
    return max(years) if years else 0.0


def parse_resume(file_path: str) -> Dict:
    """Main entry point: parse a resume file into a structured dict."""
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError("No extractable text found in the resume file.")

    links = extract_links(text)

    return {
        "file_name": os.path.basename(file_path),
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": links["linkedin"],
        "github": links["github"],
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
        "raw_text": text,
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python resume_parser.py <path_to_resume>")
        sys.exit(1)

    result = parse_resume(sys.argv[1])
    result.pop("raw_text")  # keep console output short
    print(json.dumps(result, indent=2))
