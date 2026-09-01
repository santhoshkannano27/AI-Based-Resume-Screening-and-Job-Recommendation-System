"""
main.py
-------
Command-line interface for the AI-Based Resume Screening and Job
Recommendation System. Useful for quick testing / batch processing
without launching the Streamlit UI.

Usage:
    # Recommend top jobs for a single resume
    python main.py recommend --resume sample_resumes/sample_resume_1.txt --top_n 5

    # Screen a resume against ALL resumes in a folder, ranked for one job
    python main.py rank_candidates --job_id 1 --resumes_dir sample_resumes/

    # Screen one resume against one specific job
    python main.py screen --resume sample_resumes/sample_resume_1.txt --job_id 1
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd  # noqa: E402
from resume_parser import parse_resume  # noqa: E402
from job_matcher import load_jobs, match_resume_to_jobs, screen_resume_against_job  # noqa: E402

JOBS_CSV = os.path.join(os.path.dirname(__file__), "data", "sample_jobs.csv")


def cmd_recommend(args):
    resume = parse_resume(args.resume)
    jobs_df = load_jobs(args.jobs_csv)
    ranked = match_resume_to_jobs(
        resume_text=resume["raw_text"],
        resume_skills=resume["skills"],
        jobs_df=jobs_df,
        top_n=args.top_n,
    )
    print(f"\nCandidate: {resume['name']}  |  Detected skills: {', '.join(resume['skills']) or 'none'}\n")
    print(ranked.to_string(index=False))


def cmd_screen(args):
    resume = parse_resume(args.resume)
    jobs_df = load_jobs(args.jobs_csv)
    job_row = jobs_df[jobs_df["job_id"] == args.job_id]
    if job_row.empty:
        print(f"No job found with job_id={args.job_id}")
        return
    job_row = job_row.iloc[0]
    result = screen_resume_against_job(
        resume_text=resume["raw_text"],
        resume_skills=resume["skills"],
        job_description=job_row["description"],
        job_required_skills=job_row["required_skills"],
    )
    print(f"\nCandidate: {resume['name']}  ->  Job: {job_row['title']} @ {job_row['company']}")
    for k, v in result.items():
        print(f"  {k}: {v}")


def cmd_rank_candidates(args):
    """Rank every resume in a folder against a single job (recruiter view)."""
    jobs_df = load_jobs(args.jobs_csv)
    job_row = jobs_df[jobs_df["job_id"] == args.job_id]
    if job_row.empty:
        print(f"No job found with job_id={args.job_id}")
        return
    job_row = job_row.iloc[0]

    rows = []
    for fname in os.listdir(args.resumes_dir):
        fpath = os.path.join(args.resumes_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if not fname.lower().endswith((".pdf", ".docx", ".txt")):
            continue
        try:
            resume = parse_resume(fpath)
        except Exception as e:  # noqa: BLE001
            print(f"Skipping {fname}: {e}")
            continue
        result = screen_resume_against_job(
            resume_text=resume["raw_text"],
            resume_skills=resume["skills"],
            job_description=job_row["description"],
            job_required_skills=job_row["required_skills"],
        )
        rows.append({
            "candidate": resume["name"],
            "file": fname,
            "match_percent": result["match_percent"],
            "verdict": result["verdict"],
            "matched_skills": ", ".join(result["matched_skills"]) or "-",
        })

    ranked_df = pd.DataFrame(rows).sort_values("match_percent", ascending=False)
    print(f"\nRanking candidates for: {job_row['title']} @ {job_row['company']}\n")
    print(ranked_df.to_string(index=False))


def build_parser():
    parser = argparse.ArgumentParser(description="AI Resume Screening & Job Recommendation CLI")
    parser.add_argument("--jobs_csv", default=JOBS_CSV, help="Path to jobs CSV file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rec = sub.add_parser("recommend", help="Recommend top jobs for a resume")
    p_rec.add_argument("--resume", required=True, help="Path to resume file (.pdf/.docx/.txt)")
    p_rec.add_argument("--top_n", type=int, default=5)
    p_rec.set_defaults(func=cmd_recommend)

    p_scr = sub.add_parser("screen", help="Screen one resume against one job")
    p_scr.add_argument("--resume", required=True)
    p_scr.add_argument("--job_id", type=int, required=True)
    p_scr.set_defaults(func=cmd_screen)

    p_rank = sub.add_parser("rank_candidates", help="Rank all resumes in a folder for one job")
    p_rank.add_argument("--resumes_dir", required=True)
    p_rank.add_argument("--job_id", type=int, required=True)
    p_rank.set_defaults(func=cmd_rank_candidates)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
