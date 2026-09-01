# Walkthrough: AI-Based Resume Screening & Job Recommendation System

We have created the full **AI-Based Resume Screening and Job Recommendation System** as a complete, standalone, interactive single-page HTML application and project codebase.

## 📂 Deliverables & Locations

- **Direct HTML Application**: [`ai_resume_system.html`](file:///C:/Users/Admin/.gemini/antigravity/brain/7d16609b-a9d5-4bb9-b38c-3a4356292b09/ai_resume_system.html)
- **Project Workspace Directory**: [`ai-resume-system`](file:///C:/Users/Admin/.gemini/antigravity/scratch/ai-resume-system/)
  - Main HTML App: [`index.html`](file:///C:/Users/Admin/.gemini/antigravity/scratch/ai-resume-system/index.html)
  - Documentation: [`README.md`](file:///C:/Users/Admin/.gemini/antigravity/scratch/ai-resume-system/README.md)

---

## 🌟 Key Modules & Features

### 1. 📄 Resume Parser & ATS Audit Scanner
- **Entity Extraction**: Automatically parses Candidate Name, Contact Email, Phone, Location, Total Experience Duration, and Education Degree.
- **Skill Extraction**: Maps technical and soft skills using a 300+ skill taxonomy with alias support (e.g. `k8s` ↔ `kubernetes`, `py` ↔ `python`, `reactjs` ↔ `react`).
- **ATS Audit Scorecard (0–100)**: Evaluates resumes across 4 metrics:
  - **Quantifiable Impact & Numbers** (metrics, percentages, revenue/efficiency gains)
  - **Power Action Verbs** (spearheaded, architected, optimized, etc.)
  - **Section Completeness & ATS Readability**
  - **Keyword Placement & Advice**

### 2. 🎯 Real-Time Job Match & Skill Gap Analysis
- **NLP TF-IDF & Cosine Similarity Engine**: Computes vector similarity between resume content and job description text.
- **Skill Gap Matrix**:
  - 🟢 **Matched Core Skills**
  - 🔴 **Missing In-Demand Skills** with targeted upskilling recommendations.
- **Competency Radar Chart**: Spider chart visually comparing candidate proficiency across 6 core technical domains vs the target job benchmark.

### 3. 💼 Algorithmic Job Recommendation Engine
- Automatically ranks candidate profiles against 12+ preloaded industry job roles.
- Dynamic filtering by **Domain** (AI/ML, Software Engineering, DevOps, Security, Product), **Match Tier** (85%+ Strong Match, 70%+ Good Fit), and **Work Mode** (Remote, Hybrid, Onsite).
- 1-Click **"View ATS Tips"** modal showing job-tailored resume keywords.

### 4. 👥 Recruiter Batch Screening & HR Pipeline
- Screen multiple candidate resumes simultaneously against a target job requisition.
- Ranked leaderboard with pass/fail decision workflows (**Shortlist**, **Review**, **Reject**).
- Export complete candidate evaluation sheets to **CSV**.

### 5. 🎤 AI Dynamic Interview Preparation
- Automatically generates role-specific interview questions tailored to the candidate's strengths, missing skill gaps, and STAR behavioral scenarios.

---

## 🚀 How to Open and Run

### Option 1: View Direct in Browser
Open the file [`index.html`](file:///C:/Users/Admin/.gemini/antigravity/scratch/ai-resume-system/index.html) directly in any web browser by double-clicking it or dragging it into Chrome/Edge/Firefox.

### Option 2: Run with Python HTTP Server
Run the following in PowerShell:
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\ai-resume-system
py -m http.server 8080
```
Then navigate to `http://localhost:8080` in your web browser.
