# 📄 AI-Based Resume Screening and Job Recommendation System

An offline, rule-based + TF-IDF powered system that:

1. **Parses resumes** (PDF / DOCX / TXT) to extract candidate name, email,
   phone, skills, education, and years of experience.
2. **Screens resumes against job descriptions** using TF-IDF cosine
   similarity combined with explicit skill-overlap scoring.
3. **Recommends the best-fit jobs** for a candidate from a job postings
   dataset, or **ranks candidates** for a recruiter against a chosen job.

No paid APIs, no GPU, and no internet connection required at runtime —
everything runs locally using `scikit-learn`, `pandas`, `pdfplumber`, and
`python-docx`.

---

## ✨ Features

- 🔍 **Resume Parsing** — extracts contact info, skills, education, and
  experience using regex + a curated, extensible skills database
  (`src/skills_db.py`).
- 🧠 **Smart Matching** — blends TF-IDF text similarity with a skill
  overlap ratio for an interpretable, tunable match score.
- 🎯 **Job Recommendations** — given one resume, ranks all jobs in the
  dataset by fit (candidate-side view).
- 🧑‍💼 **Recruiter Screening** — given one job, ranks all resumes in a
  folder by fit (recruiter-side view).
- 🖥️ **Two interfaces**:
  - `app.py` — interactive **Streamlit** web UI (upload & explore visually)
  - `main.py` — **command-line interface** for scripting / batch use
- 📊 Shows **matched vs. missing skills** per job so results are explainable,
  not a black box.
- 🧩 Fully offline and dependency-light — easy to extend with your own
  skills list, job dataset, or swap in embeddings (e.g. `sentence-transformers`)
  later.

---

## 📁 Project Structure

```
resume_screening_system/
├── app.py                     # Streamlit web app (main UI)
├── main.py                    # CLI entry point
├── requirements.txt
├── README.md
├── src/
│   ├── resume_parser.py       # PDF/DOCX/TXT text + field extraction
│   ├── job_matcher.py         # TF-IDF + skill-overlap matching logic
│   └── skills_db.py           # Editable skills keyword database
├── data/
│   └── sample_jobs.csv        # 18 sample job postings across roles
├── sample_resumes/
│   ├── sample_resume_1.txt    # Data Scientist example
│   └── sample_resume_2.txt    # Frontend Developer example
└── outputs/                   # (optional) exported results land here
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> If you hit an "externally managed environment" error on Linux, use:
> `pip install -r requirements.txt --break-system-packages`
> or create a virtual environment first (recommended):
> ```bash
> python -m venv .venv
> source .venv/bin/activate   # On Windows: .venv\Scripts\activate
> pip install -r requirements.txt
> ```

### 2. Run the web app (recommended)

```bash
streamlit run app.py
```

This opens a browser tab with two views:
- **Candidate view** — upload a resume, see extracted details, and get
  ranked job recommendations with matched/missing skills.
- **Recruiter view** — pick a job posting, upload a candidate resume, and
  get a match score + verdict (Strong / Moderate / Weak Match).

### 3. Or use the CLI

```bash
# Recommend the top 5 jobs for a resume
python main.py recommend --resume sample_resumes/sample_resume_1.txt --top_n 5

# Screen ONE resume against ONE specific job (by job_id from data/sample_jobs.csv)
python main.py screen --resume sample_resumes/sample_resume_1.txt --job_id 1

# Rank every resume in a folder against ONE job (recruiter batch view)
python main.py rank_candidates --resumes_dir sample_resumes/ --job_id 1
```

---

## 🧮 How the Matching Works

For each resume ↔ job pair, the system computes:

```
final_score = (text_weight × TF-IDF cosine similarity)
            + (skill_weight × skill overlap ratio)
```

- **TF-IDF cosine similarity**: vectorizes the resume text and the job
  description + required skills, then measures their cosine similarity —
  captures overall contextual relevance.
- **Skill overlap ratio**: `|matched skills| / |required skills|` — a
  transparent, explainable signal that's easy for both candidates and
  recruiters to trust.
- Weights (`text_weight`, `skill_weight`) default to `0.6` / `0.4` and are
  adjustable via sliders in the Streamlit sidebar, or function arguments
  in code.

This hybrid approach is intentionally **lightweight and explainable**
rather than relying on a black-box embedding model — see
[Future Improvements](#-future-improvements) for how to upgrade it.

---

## 🛠️ Customizing

- **Add more skills**: edit `SKILLS_DB` in `src/skills_db.py` — add new
  categories or keywords; matching updates automatically.
- **Use your own job postings**: replace `data/sample_jobs.csv` (or upload
  a CSV in the Streamlit sidebar) with columns:
  `job_id, title, company, location, description, required_skills`
  (`required_skills` should be a comma-separated string).
- **Tune scoring weights**: adjust `text_weight` / `skill_weight` in
  `src/job_matcher.py` function calls, or via the sidebar sliders in the app.

---

## 🧪 Tested Example Output

```
$ python main.py recommend --resume sample_resumes/sample_resume_1.txt --top_n 3

Candidate: Aditi Sharma | Detected skills: data visualization, git, github,
machine learning, numpy, pandas, power bi, python, scikit-learn, sql,
statistics, tensorflow

 job_id            title          company  location  match_percent          matched_skills
      1  Data Scientist   Acme Analytics Bengaluru           65.4  data visualization, ...
      7    Data Analyst  Insight Metrics    Mumbai           40.1  power bi, python, ...
     18   ML Researcher  DeepMind Labs     Remote            24.6  machine learning, ...
```

---

## 🔮 Future Improvements

- Swap TF-IDF for semantic embeddings (e.g. `sentence-transformers`,
  OpenAI/Anthropic embeddings) for deeper contextual matching.
- Add named-entity recognition (spaCy) for more robust name/organization
  extraction.
- Persist results to a database and add an authentication layer for a
  multi-recruiter SaaS setup.
- Add resume "improvement suggestions" — highlight missing skills for a
  target role and suggest courses/certifications.
- Support bulk resume upload (ZIP) directly in the Streamlit UI.
- Add unit tests (`pytest`) for `resume_parser.py` and `job_matcher.py`.

---

## 📜 License

This project is provided as-is for educational and portfolio purposes.
Feel free to modify and reuse it.
