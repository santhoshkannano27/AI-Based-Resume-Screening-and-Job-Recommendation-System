"""
job_matcher.py
--------------
Computes similarity between a resume and a set of job postings using
TF-IDF + cosine similarity (classic, dependency-light IR approach --
no GPU / internet / pretrained embedding model required), and blends
in an explicit skill-overlap score for interpretability.
"""

from typing import Dict, List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_jobs(csv_path: str) -> pd.DataFrame:
    """
    Load job postings from a CSV file.
    Expected columns: job_id, title, company, description, required_skills, location
    """
    df = pd.read_csv(csv_path)
    required_cols = {"job_id", "title", "company", "description", "required_skills"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"jobs CSV is missing required columns: {missing}")
    df["required_skills"] = df["required_skills"].fillna("")
    df["description"] = df["description"].fillna("")
    return df


def _skill_overlap_score(resume_skills: List[str], job_required_skills: str) -> float:
    """Fraction of a job's required skills that are present in the resume."""
    job_skills = {s.strip().lower() for s in job_required_skills.split(",") if s.strip()}
    if not job_skills:
        return 0.0
    resume_skill_set = {s.lower() for s in resume_skills}
    overlap = job_skills & resume_skill_set
    return len(overlap) / len(job_skills)


def match_resume_to_jobs(
    resume_text: str,
    resume_skills: List[str],
    jobs_df: pd.DataFrame,
    top_n: int = 5,
    text_weight: float = 0.6,
    skill_weight: float = 0.4,
) -> pd.DataFrame:
    """
    Rank jobs for a single resume.

    final_score = text_weight * TFIDF_cosine_similarity
                + skill_weight * skill_overlap_ratio

    Returns a DataFrame sorted by final_score (descending), including a
    human-readable list of matched/missing skills per job.
    """
    corpus = jobs_df["description"] + " " + jobs_df["required_skills"]
    corpus = list(corpus) + [resume_text]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    resume_vector = tfidf_matrix[-1]
    job_vectors = tfidf_matrix[:-1]
    text_scores = cosine_similarity(resume_vector, job_vectors).flatten()

    results = jobs_df.copy()
    results["text_similarity"] = text_scores
    results["skill_overlap"] = results["required_skills"].apply(
        lambda s: _skill_overlap_score(resume_skills, s)
    )
    results["final_score"] = (
        text_weight * results["text_similarity"] + skill_weight * results["skill_overlap"]
    )

    def matched_skills(job_required_skills: str) -> str:
        job_skills = {s.strip().lower() for s in job_required_skills.split(",") if s.strip()}
        resume_skill_set = {s.lower() for s in resume_skills}
        return ", ".join(sorted(job_skills & resume_skill_set)) or "-"

    def missing_skills(job_required_skills: str) -> str:
        job_skills = {s.strip().lower() for s in job_required_skills.split(",") if s.strip()}
        resume_skill_set = {s.lower() for s in resume_skills}
        return ", ".join(sorted(job_skills - resume_skill_set)) or "-"

    results["matched_skills"] = results["required_skills"].apply(matched_skills)
    results["missing_skills"] = results["required_skills"].apply(missing_skills)

    results["match_percent"] = (results["final_score"] * 100).round(1).clip(0, 100)

    results = results.sort_values("final_score", ascending=False).head(top_n)
    display_cols = [
        "job_id", "title", "company", "location" if "location" in results.columns else "title",
        "match_percent", "matched_skills", "missing_skills",
    ]
    display_cols = [c for c in dict.fromkeys(display_cols)]  # dedupe, preserve order
    return results[display_cols].reset_index(drop=True)


def screen_resume_against_job(
    resume_text: str,
    resume_skills: List[str],
    job_description: str,
    job_required_skills: str,
    text_weight: float = 0.6,
    skill_weight: float = 0.4,
) -> Dict:
    """
    Screen ONE resume against ONE specific job description.
    Useful for a recruiter workflow: "does this candidate fit this role?"
    """
    corpus = [job_description + " " + job_required_skills, resume_text]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    text_similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    skill_score = _skill_overlap_score(resume_skills, job_required_skills)
    final_score = text_weight * text_similarity + skill_weight * skill_score

    job_skills = {s.strip().lower() for s in job_required_skills.split(",") if s.strip()}
    resume_skill_set = {s.lower() for s in resume_skills}

    return {
        "text_similarity": round(float(text_similarity), 4),
        "skill_overlap": round(float(skill_score), 4),
        "final_score": round(float(final_score), 4),
        "match_percent": round(float(final_score) * 100, 1),
        "matched_skills": sorted(job_skills & resume_skill_set),
        "missing_skills": sorted(job_skills - resume_skill_set),
        "verdict": (
            "Strong Match" if final_score >= 0.5 else
            "Moderate Match" if final_score >= 0.25 else
            "Weak Match"
        ),
    }
