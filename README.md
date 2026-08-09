# AI-Powered Intelligent Interview & Recruitment System

A complete, production-grade final-year AI/ML capstone project designed to automate corporate recruitment pipelines.

The platform provides automated **Resume PDF Parsing**, **TF-IDF & Cosine Similarity Job Matching**, **Adaptive AI Technical Interviewing**, **NLP Answer Evaluation**, **Multi-Criteria Weighted Candidate Ranking**, and **Skill Gap Analysis** with modern SaaS dashboards for both Candidates and Recruiters.

---

## 🌟 Key Features

### 👤 Candidate Features
* **Authentication & Profile Management**: Secure registration, password hashing (Werkzeug), role-based session authorization.
* **Resume PDF Parser**: Upload PDF resumes; extract email, phone, education background, estimated experience years, projects, certifications, and technical skills automatically.
* **Real-time AI Match Calculator**: View instant job match percentages, TF-IDF text similarity scores, skill overlap ratios, matching skills, and missing skills.
* **Adaptive AI Interview**: Live timed technical & HR interview assessments tailored specifically to job requirements and candidate background.
* **NLP Answer Evaluator**: Evaluates text responses against key concepts, expected keywords, and reference answers.
* **Skill Gap Analysis**: View candidate strengths, missing skill gaps, and personalized recommended learning roadmaps.

### 👔 Recruiter Features
* **Recruiter SaaS Dashboard**: Summary metrics for Total Jobs, Applicants, Avg Match Score, Shortlisted candidates, and Recent Applications.
* **Job Posting Management**: Create, edit, and delete job listings with custom experience requirements and interview parameters.
* **Configurable Dynamic Ranking Weights**: Customize evaluation factor weights (Resume Match %, Technical Interview %, Skill Match %, Experience Years %).
* **Applicant Ranking Table**: Filter, search, and rank candidate applications by composite scores.
* **Candidate Detail Inspector**: Inspect extracted resume text, score breakdown, keyword coverage, and shortlist/reject applicants.
* **Recruitment Analytics**: Interactive Chart.js graphs for applications per job, candidate score distribution histograms, and application status breakdown.

---

## 📐 AI/ML Architecture & Mathematical Foundations

### 1. TF-IDF & Cosine Similarity Job Matcher
Resume text ($A$) and Job Descriptions ($B$) are converted into Term Frequency-Inverse Document Frequency (TF-IDF) sparse vector space representations. Text similarity is calculated using the vector Cosine angle:

$$\text{Cosine Similarity}(A, B) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

Skill Overlap Ratio is computed as:

$$\text{Skill Match Ratio} = \frac{|S_{\text{resume}} \cap S_{\text{job}}|}{|S_{\text{job}}|} \times 100$$

Unified Resume Match Score:

$$\text{Match Score} = (0.50 \times \text{Cosine Similarity}) + (0.50 \times \text{Skill Match Ratio})$$

### 2. Multi-Criteria Weighted Candidate Ranking Formula
Recruiters can adjust dynamic weights $w_1, w_2, w_3, w_4$. The final score is calculated from stored empirical components:

$$\text{Final Score} = (w_1 \times S_{\text{resume}}) + (w_2 \times S_{\text{interview}}) + (w_3 \times S_{\text{skill}}) + (w_4 \times S_{\text{experience}})$$

*Default Weights: Resume Match (40%), Technical Interview (35%), Skill Match (15%), Experience Years (10%).*

---

## 🛠️ Technology Stack

* **Backend Framework**: Python 3.11+, Flask 3.0
* **Database & ORM**: SQLAlchemy, SQLite (Development), PostgreSQL-ready architecture
* **AI & NLP Libraries**: Scikit-Learn (TfidfVectorizer, Cosine Similarity), pypdf, pdfplumber
* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4
* **Security & Auth**: Werkzeug Password Hashing, Session Management, Input Sanitization
* **WSGI Production Server**: Gunicorn

---

## 📁 Project Architecture

```text
AI-Recruitment-System/
├── app.py                      # Application entry point & WSGI runner
├── config.py                   # Environment configs (Development, Testing, Production)
├── requirements.txt            # Python dependencies
├── Procfile                    # Production web server runner (Gunicorn)
├── .env.example                # Environment variables template
├── seed.py                     # Demo data generator script
├── README.md                   # Comprehensive documentation & Viva guide
│
├── app/
│   ├── __init__.py             # Flask App Factory
│   ├── models/                 # SQLAlchemy ORM Models (User, Candidate, Recruiter, Job, Resume, Application, Interview, Score, etc.)
│   ├── routes/                 # Flask Blueprints (auth, candidate, recruiter, api)
│   ├── services/               # AI & Business Services (resume_parser, skill_extractor, job_matcher, interview_engine, answer_evaluator, ranking_engine)
│   ├── static/                 # CSS, JS (main.js, charts.js, interview.js), Images
│   ├── templates/              # Jinja2 Dynamic HTML Templates (Bootstrap 5)
│   └── utils/                  # Decorators, Security & File Validators
│
├── database/                   # SQLite database directory
├── uploads/                    # Secure PDF uploads storage
└── tests/                      # Pytest & Unittest suite (auth, resume, matching, interview, ranking)
```

---

## 🚀 Quickstart & Local Installation

### 1. Prerequisites
Ensure Python 3.11+ is installed.

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/AI-Recruitment-System.git
cd AI-Recruitment-System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed Demo Data
Populate the database with demo recruiters, jobs, candidate profiles, sample PDF resumes, and applications:
```bash
python seed.py
```

### 5. Run Local Development Server
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Recruiter** | `recruiter@example.com` | `password123` | Enterprise AI Labs Recruiter |
| **Candidate 1** | `candidate1@example.com` | `password123` | Sai (Senior ML Engineer - 88% Match) |
| **Candidate 2** | `candidate2@example.com` | `password123` | Alex Rivera (Full Stack Developer) |
| **Candidate 3** | `candidate3@example.com` | `password123` | Priya Sharma (Data Scientist) |
| **Candidate 4** | `candidate4@example.com` | `password123` | David Kim (Junior Python Dev) |

---

## 🧪 Automated Testing

Run the automated test suite covering auth, PDF parsing, job matching, interview evaluation, and ranking:

```bash
python -m unittest discover tests
```

---

## 🌐 Production Deployment (Render / Heroku)

This application is ready for production cloud deployment:

1. **Procfile**: Configured for Gunicorn execution (`web: gunicorn app:app`).
2. **PostgreSQL Compatibility**: Automatically converts `postgres://` environment strings to `postgresql://`.
3. **Environment Variables**:
   * `SECRET_KEY`: Set strong secret key.
   * `FLASK_ENV`: Set to `production`.
   * `DATABASE_URL`: Set PostgreSQL database connection string.

---

## 🛡️ Responsible AI & Ethical Hiring Guarantee

* **Protected Attributes Excluded**: The system does NOT extract, evaluate, or store gender, race, age, religion, political opinions, or medical status.
* **No Facial/Voice Emotion Recognition**: Hiring recommendations rely strictly on text relevance, technical skill extraction, and answer accuracy.
* **Decision-Support Design**: All scores are transparent recommendations intended to assist human recruiters in technical screening.

---

## 📜 License
Developed as an academic capstone project. Open source for educational and demonstration purposes.


## 🚀 Quick Start (Windows)

```powershell
# 1. Create and activate a virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Create the database and demo data
python seed.py

# 4. Start the application
python app.py
```

Open `http://127.0.0.1:5000`.

### Demo Accounts

**Recruiter**
- Email: `recruiter@example.com`
- Password: `password123`

**Candidates**
- `candidate1@example.com` / `password123`
- `candidate2@example.com` / `password123`
- `candidate3@example.com` / `password123`
- `candidate4@example.com` / `password123`

> `python seed.py` resets the development database and recreates the demo data. Do not run it against production data.

## ☁️ Render Deployment

The repository includes `render.yaml` and a production Gunicorn configuration.

For persistent production data, create a managed PostgreSQL database and set:

```text
DATABASE_URL=postgresql://...
SECRET_KEY=<long-random-secret>
FLASK_ENV=production
```

The health endpoint is available at `/health`.

## 🧪 Testing

```powershell
pytest -q
```

The tests cover authentication, resume parsing helpers, job matching, interview evaluation, and ranking calculations.

## 🔐 Security Notes

- Passwords are hashed with Werkzeug.
- Uploaded resumes are restricted to PDF files and validated by PDF magic bytes.
- Uploaded filenames are replaced with UUID-based server filenames.
- Candidate/recruiter route authorization is enforced.
- Candidate interview submissions are ownership-checked.
- AI scores are transparent, configurable, and intended only as decision support.
#   T a l e n t - A i - R e c u r i t m e n t  
 