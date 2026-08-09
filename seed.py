import os
import json
import pypdf
from datetime import datetime
from app import create_app
from app.models import db, User, Candidate, Recruiter, Job, Resume, Skill, CandidateSkill, Application, Interview, InterviewQuestion, InterviewAnswer, Score, Recommendation
from app.services.skill_extractor import SKILL_TAXONOMY
from app.services.job_matcher import JobMatcher
from app.services.ranking_engine import RankingEngine

app = create_app('development')

def generate_sample_pdf(filepath, name, email, phone, text_content):
    """Generate a clean, text-based PDF resume for demo/testing."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    text = c.beginText(50, height - 55)
    text.setFont("Helvetica", 10)
    lines = [
        name,
        email,
        phone,
        "",
        *text_content.replace("\\r", "").split("\\n"),
    ]
    for line in lines:
        # Keep each PDF line within a readable width.
        line = line.strip()
        while len(line) > 105:
            text.textLine(line[:105])
            line = line[105:]
            if text.getY() < 55:
                c.drawText(text)
                c.showPage()
                text = c.beginText(50, height - 55)
                text.setFont("Helvetica", 10)
        text.textLine(line)
        if text.getY() < 55:
            c.drawText(text)
            c.showPage()
            text = c.beginText(50, height - 55)
            text.setFont("Helvetica", 10)
    c.drawText(text)
    c.save()

def seed_database():
    with app.app_context():
        print("Resetting database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding Skills Taxonomy Database...")
        skill_objs = {}
        for category, skills in SKILL_TAXONOMY.items():
            for s_name in skills:
                if s_name not in skill_objs:
                    skill = Skill(name=s_name, category=category)
                    db.session.add(skill)
                    skill_objs[s_name] = skill
        db.session.flush()

        print("Seeding Demo Recruiter Account...")
        recruiter_user = User(email='recruiter@example.com', role='recruiter')
        recruiter_user.set_password('password123')
        db.session.add(recruiter_user)
        db.session.flush()

        recruiter_profile = Recruiter(
            user_id=recruiter_user.id,
            company_name='Enterprise AI Labs',
            position='Head of Talent Acquisition',
            department='HR & Recruiting'
        )
        db.session.add(recruiter_profile)
        db.session.flush()

        print("Seeding Job Openings...")
        job1 = Job(
            recruiter_id=recruiter_profile.id,
            title='Senior Machine Learning Engineer',
            department='Artificial Intelligence',
            location='San Francisco, CA (Hybrid)',
            job_type='Full-time',
            description='We are looking for a Senior Machine Learning Engineer to design, build, and deploy production NLP and Computer Vision models. Required experience in Python, PyTorch, Scikit-learn, SQL, and Docker.',
            required_skills_text='Python, Machine Learning, Deep Learning, SQL, PyTorch, Scikit-learn, Docker, AWS',
            experience_years=3,
            question_count=5,
            difficulty='Medium',
            interview_duration_mins=15
        )
        job1.set_weights({'resume_match': 0.40, 'interview': 0.35, 'skill_match': 0.15, 'experience': 0.10})

        job2 = Job(
            recruiter_id=recruiter_profile.id,
            title='Full Stack Web Developer (Python & Flask)',
            department='Engineering',
            location='Remote',
            job_type='Full-time',
            description='Join our core web engineering team. Responsible for developing scalable Flask microservices, REST APIs, and modern Bootstrap/React frontend interfaces with PostgreSQL database design.',
            required_skills_text='Python, Flask, JavaScript, SQL, HTML5, CSS3, Bootstrap, PostgreSQL, REST API',
            experience_years=2,
            question_count=5,
            difficulty='Medium',
            interview_duration_mins=15
        )
        job2.set_weights({'resume_match': 0.40, 'interview': 0.35, 'skill_match': 0.15, 'experience': 0.10})

        job3 = Job(
            recruiter_id=recruiter_profile.id,
            title='Data Scientist & Analytics Specialist',
            department='Data & Analytics',
            location='New York, NY',
            job_type='Full-time',
            description='Looking for a Data Scientist to analyze enterprise datasets, perform predictive modeling, statistical testing, and build interactive dashboards with Pandas, NumPy, and Tableau.',
            required_skills_text='Python, Data Analysis, Pandas, NumPy, Scikit-learn, SQL, Machine Learning, Tableau',
            experience_years=2,
            question_count=5,
            difficulty='Medium',
            interview_duration_mins=15
        )
        job3.set_weights({'resume_match': 0.40, 'interview': 0.35, 'skill_match': 0.15, 'experience': 0.10})

        db.session.add_all([job1, job2, job3])
        db.session.flush()

        print("Seeding Demo Candidates & Pre-parsed Resumes...")
        candidates_data = [
            {
                'email': 'candidate1@example.com',
                'name': 'Sai',
                'headline': 'AI & Machine Learning Engineer',
                'phone': '+1 (555) 234-5678',
                'location': 'San Francisco, CA',
                'exp_years': 4.0,
                'skills': ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'SQL', 'Scikit-learn', 'Pandas', 'Flask'],
                'missing_for_job1': ['Docker', 'AWS'],
                'resume_text': """Sai - Senior ML Engineer
Email: candidate1@example.com | Phone: +1 (555) 234-5678 | San Francisco, CA

SUMMARY:
Experienced Machine Learning Engineer with 4 years of hands-on experience building end-to-end NLP and computer vision systems.

SKILLS:
Python, Machine Learning, Deep Learning, PyTorch, SQL, Scikit-learn, Pandas, NumPy, Flask, REST API, Git.

EDUCATION:
B.Tech in Computer Science - State University (2020)

EXPERIENCE:
AI Research Engineer (2020 - Present)
- Developed PyTorch transformers and Scikit-learn NLP classifiers improving accuracy by 24%.
- Engineered database queries with SQL and Pandas pipelines."""
            },
            {
                'email': 'candidate2@example.com',
                'name': 'Alex Rivera',
                'headline': 'Full Stack Developer & Software Architect',
                'phone': '+1 (555) 987-6543',
                'location': 'Austin, TX',
                'exp_years': 3.0,
                'skills': ['Python', 'Flask', 'JavaScript', 'HTML5', 'CSS3', 'Bootstrap', 'SQL', 'PostgreSQL', 'REST API', 'Git'],
                'missing_for_job1': ['PyTorch', 'Deep Learning', 'Docker', 'AWS'],
                'resume_text': """Alex Rivera - Full Stack Developer
Email: candidate2@example.com | Phone: +1 (555) 987-6543 | Austin, TX

SKILLS:
Python, Flask, JavaScript, HTML5, CSS3, Bootstrap, SQL, PostgreSQL, REST API, Git, Django.

EDUCATION:
B.S. in Software Engineering - Tech Institute (2021)

EXPERIENCE:
Full Stack Web Developer (2021 - Present)
- Designed and maintained Flask REST APIs and Bootstrap frontend interfaces.
- Structured relational databases with PostgreSQL and SQLAlchemy."""
            },
            {
                'email': 'candidate3@example.com',
                'name': 'Priya Sharma',
                'headline': 'Data Scientist & Statistical Modeler',
                'phone': '+1 (555) 345-6789',
                'location': 'Seattle, WA',
                'exp_years': 2.5,
                'skills': ['Python', 'Data Analysis', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL', 'Machine Learning', 'Tableau', 'R'],
                'missing_for_job1': ['Deep Learning', 'PyTorch', 'Docker', 'AWS'],
                'resume_text': """Priya Sharma - Data Scientist
Email: candidate3@example.com | Phone: +1 (555) 345-6789 | Seattle, WA

SKILLS:
Python, Data Analysis, Pandas, NumPy, Scikit-learn, SQL, Machine Learning, Tableau, Data Visualization, R.

EDUCATION:
M.S. in Data Science - University of Washington (2022)

EXPERIENCE:
Data Scientist (2022 - Present)
- Performed statistical testing and built predictive machine learning models in Python using Pandas and Scikit-learn.
- Built interactive Tableau dashboards for executive business reporting."""
            },
            {
                'email': 'candidate4@example.com',
                'name': 'David Kim',
                'headline': 'Junior Python Developer',
                'phone': '+1 (555) 456-7890',
                'location': 'Chicago, IL',
                'exp_years': 1.0,
                'skills': ['Python', 'SQL', 'Git', 'HTML5', 'CSS3'],
                'missing_for_job1': ['Machine Learning', 'Deep Learning', 'PyTorch', 'Scikit-learn', 'Docker', 'AWS'],
                'resume_text': """David Kim - Junior Developer
Email: candidate4@example.com | Phone: +1 (555) 456-7890 | Chicago, IL

SKILLS:
Python, SQL, Git, HTML5, CSS3, SQLite.

EDUCATION:
B.S. in Computer Science (2023)

EXPERIENCE:
Junior Software Engineer (2023 - Present)
- Assisted with Python scripting and SQL queries."""
            }
        ]

        upload_dir = os.path.join(app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        for cdata in candidates_data:
            c_user = User(email=cdata['email'], role='candidate')
            c_user.set_password('password123')
            db.session.add(c_user)
            db.session.flush()

            cand_profile = Candidate(
                user_id=c_user.id,
                full_name=cdata['name'],
                phone=cdata['phone'],
                headline=cdata['headline'],
                location=cdata['location']
            )
            db.session.add(cand_profile)
            db.session.flush()

            # Create sample PDF resume file
            pdf_filename = f"sample_{cdata['name'].lower().replace(' ', '_')}.pdf"
            pdf_path = os.path.join(upload_dir, pdf_filename)
            generate_sample_pdf(pdf_path, cdata['name'], cdata['email'], cdata['phone'], cdata['resume_text'])

            # Create Resume Record
            res = Resume(
                candidate_id=cand_profile.id,
                filename=pdf_filename,
                file_path=pdf_path,
                raw_text=cdata['resume_text'],
                parsed_name=cdata['name'],
                parsed_email=cdata['email'],
                parsed_phone=cdata['phone'],
                parsed_education_json=json.dumps(["B.Tech / B.S. Computer Science"]),
                parsed_experience_years=cdata['exp_years'],
                parsed_projects_json=json.dumps(["AI Talent Recruitment Engine", "Predictive Analytics Dashboard"]),
                parsed_skills_json=json.dumps(cdata['skills'])
            )
            db.session.add(res)
            db.session.flush()

            # Map Candidate Skills
            for sk_name in cdata['skills']:
                if sk_name in skill_objs:
                    cs = CandidateSkill(candidate_id=cand_profile.id, skill_id=skill_objs[sk_name].id, source='parsed')
                    db.session.add(cs)

            # Create Application for Job 1 (Senior ML Engineer)
            match_res = JobMatcher.match(
                cdata['resume_text'],
                cdata['skills'],
                job1.description,
                job1.get_required_skills_list()
            )

            # Pre-evaluate mock interview scores
            interview_score = 82.0 if cdata['name'] == 'Sai' else (74.0 if cdata['name'] == 'Alex Rivera' else 78.0)
            exp_score = RankingEngine.calculate_experience_score(cdata['exp_years'], job1.experience_years)

            final_score, breakdown = RankingEngine.calculate_final_score(
                match_res['overall_match_score'],
                interview_score,
                match_res['skill_match_score'],
                exp_score,
                job1.get_weights()
            )

            status = 'Shortlisted' if cdata['name'] == 'Sai' else ('Interviewed' if cdata['name'] == 'Alex Rivera' else 'Applied')

            application = Application(
                candidate_id=cand_profile.id,
                job_id=job1.id,
                resume_id=res.id,
                status=status,
                match_score=match_res['overall_match_score'],
                interview_score=interview_score,
                final_score=final_score
            )
            db.session.add(application)
            db.session.flush()

            # Create Score Record
            score_obj = Score(
                application_id=application.id,
                resume_match_score=match_res['overall_match_score'],
                interview_score=interview_score,
                skill_match_score=match_res['skill_match_score'],
                experience_score=exp_score,
                final_score=final_score,
                weights_json=json.dumps(breakdown['weights_used'])
            )
            db.session.add(score_obj)

            # Create Recommendation Record
            gap_analysis = RankingEngine.generate_skill_gap_analysis(
                job1.title, match_res['matching_skills'], match_res['missing_skills']
            )
            rec = Recommendation(
                application_id=application.id,
                strong_skills_json=json.dumps(gap_analysis['strong_skills']),
                missing_skills_json=json.dumps(gap_analysis['missing_skills']),
                learning_recommendations_json=json.dumps(gap_analysis['learning_recommendations']),
                overall_summary=gap_analysis['summary']
            )
            db.session.add(rec)

        db.session.commit()
        print("\n=======================================================")
        print("DEMO DATABASE SEEDED SUCCESSFULLY!")
        print("=======================================================")
        print("Demo Recruiter Account:")
        print("  Email:    recruiter@example.com")
        print("  Password: password123")
        print("\nDemo Candidate Accounts:")
        print("  Candidate 1: candidate1@example.com / password123 (Sai - 88% Match)")
        print("  Candidate 2: candidate2@example.com / password123 (Alex)")
        print("  Candidate 3: candidate3@example.com / password123 (Priya)")
        print("  Candidate 4: candidate4@example.com / password123 (David)")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_database()
