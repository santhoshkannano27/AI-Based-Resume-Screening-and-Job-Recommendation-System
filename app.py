"""
app.py
------
Streamlit UI for the AI-Based Resume Screening and Job Recommendation System.

Run with:
    streamlit run app.py
"""

import os
import sys
import tempfile

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from resume_parser import parse_resume  # noqa: E402
from job_matcher import load_jobs, match_resume_to_jobs, screen_resume_against_job  # noqa: E402

JOBS_CSV = os.path.join(os.path.dirname(__file__), "data", "sample_jobs.csv")

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

st.title("📄 AI-Based Resume Screening & Job Recommendation System")
st.caption(
    "Upload a resume to extract candidate details and get ranked job "
    "recommendations, powered by TF-IDF text similarity + skill matching."
)

# ---------------------------------------------------------------------------
# Sidebar: job dataset source
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Settings")
jobs_source = st.sidebar.radio(
    "Job postings source", ["Use sample jobs dataset", "Upload my own jobs CSV"]
)

if jobs_source == "Upload my own jobs CSV":
    jobs_file = st.sidebar.file_uploader("Upload jobs CSV", type=["csv"])
    if jobs_file is not None:
        jobs_df = pd.read_csv(jobs_file)
        jobs_df["required_skills"] = jobs_df["required_skills"].fillna("")
        jobs_df["description"] = jobs_df["description"].fillna("")
    else:
        st.sidebar.info("Required columns: job_id, title, company, description, required_skills")
        jobs_df = load_jobs(JOBS_CSV)
else:
    jobs_df = load_jobs(JOBS_CSV)

top_n = st.sidebar.slider("Number of job recommendations", min_value=3, max_value=15, value=5)
text_weight = st.sidebar.slider("Text similarity weight", 0.0, 1.0, 0.6, 0.05)
skill_weight = round(1.0 - text_weight, 2)
st.sidebar.write(f"Skill overlap weight: **{skill_weight}**")

with st.sidebar.expander("📋 View job dataset"):
    st.dataframe(jobs_df[["job_id", "title", "company", "location"] if "location" in jobs_df.columns
                          else ["job_id", "title", "company"]], use_container_width=True)

# ---------------------------------------------------------------------------
# Main: resume upload
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🙋 Candidate view — Job Recommendations", "🧑‍💼 Recruiter view — Screen against a Job"])

with tab1:
    uploaded_resume = st.file_uploader(
        "Upload your resume (.pdf, .docx, or .txt)", type=["pdf", "docx", "txt"], key="resume_recommend"
    )

    if uploaded_resume is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume.name)[1]) as tmp:
            tmp.write(uploaded_resume.read())
            tmp_path = tmp.name

        try:
            resume = parse_resume(tmp_path)
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not parse resume: {e}")
            resume = None
        finally:
            os.unlink(tmp_path)

        if resume:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("👤 Extracted Candidate Info")
                st.write(f"**Name:** {resume['name']}")
                st.write(f"**Email:** {resume['email'] or '—'}")
                st.write(f"**Phone:** {resume['phone'] or '—'}")
                if resume["linkedin"]:
                    st.write(f"**LinkedIn:** {resume['linkedin']}")
                if resume["github"]:
                    st.write(f"**GitHub:** {resume['github']}")
                st.write(f"**Experience (detected):** {resume['experience_years']} years")
                st.write(f"**Education:** {', '.join(resume['education']) or 'Not detected'}")
                st.write("**Skills detected:**")
                if resume["skills"]:
                    st.write(" ".join(f"`{s}`" for s in resume["skills"]))
                else:
                    st.warning("No skills detected — try enriching the skills database in src/skills_db.py")

            with col2:
                st.subheader("🎯 Top Job Matches")
                ranked = match_resume_to_jobs(
                    resume_text=resume["raw_text"],
                    resume_skills=resume["skills"],
                    jobs_df=jobs_df,
                    top_n=top_n,
                    text_weight=text_weight,
                    skill_weight=skill_weight,
                )
                for _, row in ranked.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{row['title']}** — {row['company']}")
                            if "location" in row:
                                st.caption(f"📍 {row['location']}")
                            if row["matched_skills"] != "-":
                                st.markdown(f"✅ Matched: {row['matched_skills']}")
                            if row["missing_skills"] != "-":
                                st.markdown(f"⚠️ Missing: {row['missing_skills']}")
                        with c2:
                            st.metric("Match", f"{row['match_percent']}%")
    else:
        st.info("👆 Upload a resume to see extracted details and job recommendations.")
        st.caption("No resume handy? Try the sample files in `sample_resumes/` after downloading the project.")

with tab2:
    st.subheader("Screen a single resume against a specific job posting")
    job_options = {f"{r.title} — {r.company} (ID {r.job_id})": r.job_id for r in jobs_df.itertuples()}
    selected_job_label = st.selectbox("Select a job posting", list(job_options.keys()))
    selected_job_id = job_options[selected_job_label]
    job_row = jobs_df[jobs_df["job_id"] == selected_job_id].iloc[0]

    with st.expander("View job description"):
        st.write(job_row["description"])
        st.write(f"**Required skills:** {job_row['required_skills']}")

    uploaded_resume_2 = st.file_uploader(
        "Upload candidate resume (.pdf, .docx, or .txt)", type=["pdf", "docx", "txt"], key="resume_screen"
    )

    if uploaded_resume_2 is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume_2.name)[1]) as tmp:
            tmp.write(uploaded_resume_2.read())
            tmp_path = tmp.name

        try:
            resume2 = parse_resume(tmp_path)
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not parse resume: {e}")
            resume2 = None
        finally:
            os.unlink(tmp_path)

        if resume2:
            result = screen_resume_against_job(
                resume_text=resume2["raw_text"],
                resume_skills=resume2["skills"],
                job_description=job_row["description"],
                job_required_skills=job_row["required_skills"],
                text_weight=text_weight,
                skill_weight=skill_weight,
            )

            verdict_color = {"Strong Match": "green", "Moderate Match": "orange", "Weak Match": "red"}
            st.markdown(
                f"### Result for **{resume2['name']}**: "
                f":{verdict_color[result['verdict']]}[{result['verdict']}] — {result['match_percent']}%"
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall Match", f"{result['match_percent']}%")
            c2.metric("Text Similarity", f"{round(result['text_similarity']*100, 1)}%")
            c3.metric("Skill Overlap", f"{round(result['skill_overlap']*100, 1)}%")

            st.markdown(f"✅ **Matched skills:** {', '.join(result['matched_skills']) or 'None'}")
            st.markdown(f"⚠️ **Missing skills:** {', '.join(result['missing_skills']) or 'None'}")
    else:
        st.info("👆 Upload a candidate resume to screen it against the selected job.")

st.divider()
st.caption(
    "Built with rule-based resume parsing (pdfplumber / python-docx) and "
    "TF-IDF + cosine similarity matching (scikit-learn). No external API calls."
)
