import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app.models import db, Candidate, Resume, Skill, CandidateSkill, Job, Application, Interview, InterviewQuestion, InterviewAnswer, Score, Recommendation
from app.utils.decorators import role_required
from app.utils.validators import allowed_file, generate_secure_filepath, validate_pdf_file
from app.services.resume_parser import ResumeParser
from app.services.skill_extractor import extract_skills_from_text
from app.services.job_matcher import JobMatcher
from app.services.interview_engine import InterviewEngine
from app.services.answer_evaluator import AnswerEvaluator
from app.services.ranking_engine import RankingEngine

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

def get_current_candidate():
    user_id = session.get('user_id')
    return Candidate.query.filter_by(user_id=user_id).first()


@candidate_bp.route('/dashboard')
@role_required('candidate')
def dashboard():
    candidate = get_current_candidate()
    if not candidate:
        flash('Candidate profile not found.', 'danger')
        return redirect(url_for('index'))

    latest_resume = Resume.query.filter_by(candidate_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()
    applications = Application.query.filter_by(candidate_id=candidate.id).order_by(Application.applied_at.desc()).all()
    available_jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(5).all()

    # Calculate Profile Completion
    completion_items = [
        bool(candidate.full_name),
        bool(candidate.phone),
        bool(candidate.headline),
        bool(candidate.location),
        bool(latest_resume)
    ]
    completion_percentage = int((sum(completion_items) / len(completion_items)) * 100)

    # Job match previews
    job_matches = []
    if latest_resume and latest_resume.raw_text:
        cand_skills = [s.skill.name for s in candidate.candidate_skills]
        for job in available_jobs:
            req_skills = job.get_required_skills_list()
            match_res = JobMatcher.match(
                latest_resume.raw_text, cand_skills, job.description, req_skills
            )
            job_matches.append({
                'job': job,
                'match': match_res
            })

    return render_template('candidate/dashboard.html',
                           candidate=candidate,
                           latest_resume=latest_resume,
                           applications=applications,
                           job_matches=job_matches,
                           completion_percentage=completion_percentage)


@candidate_bp.route('/profile', methods=['GET', 'POST'])
@role_required('candidate')
def profile():
    candidate = get_current_candidate()
    if request.method == 'POST':
        candidate.full_name = request.form.get('full_name', '').strip()
        candidate.phone = request.form.get('phone', '').strip()
        candidate.headline = request.form.get('headline', '').strip()
        candidate.location = request.form.get('location', '').strip()
        candidate.bio = request.form.get('bio', '').strip()

        db.session.commit()
        session['name'] = candidate.full_name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('candidate.profile'))

    return render_template('candidate/profile.html', candidate=candidate)


@candidate_bp.route('/resume', methods=['GET', 'POST'])
@role_required('candidate')
def resume():
    candidate = get_current_candidate()
    latest_resume = Resume.query.filter_by(candidate_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()

    if request.method == 'POST':
        if 'resume_pdf' not in request.files:
            flash('No file selected for upload.', 'danger')
            return redirect(url_for('candidate.resume'))

        file = request.files['resume_pdf']
        if file.filename == '':
            flash('No file selected for upload.', 'danger')
            return redirect(url_for('candidate.resume'))

        if not allowed_file(file.filename):
            flash('Invalid file type! Please upload a PDF document (.pdf).', 'danger')
            return redirect(url_for('candidate.resume'))

        upload_dir = current_app.config['UPLOAD_FOLDER']
        file_path, secure_name = generate_secure_filepath(upload_dir, file.filename)
        file.save(file_path)

        # Validate PDF structure
        is_valid, err_msg = validate_pdf_file(file_path)
        if not is_valid:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'PDF validation failed: {err_msg}', 'danger')
            return redirect(url_for('candidate.resume'))

        # Parse Resume PDF with AI ResumeParser Service
        try:
            parsed_data = ResumeParser.parse(file_path)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Failed to extract resume text: {str(e)}', 'danger')
            return redirect(url_for('candidate.resume'))

        # Update candidate details if missing
        if parsed_data.get('name') and not candidate.headline:
            candidate.headline = f"Experienced Professional"
        if parsed_data.get('phone') and not candidate.phone:
            candidate.phone = parsed_data['phone']

        # Store Resume Record
        new_resume = Resume(
            candidate_id=candidate.id,
            filename=file.filename,
            file_path=file_path,
            raw_text=parsed_data['raw_text'],
            parsed_name=parsed_data['name'],
            parsed_email=parsed_data['email'],
            parsed_phone=parsed_data['phone'],
            parsed_education_json=json.dumps(parsed_data['education']),
            parsed_experience_years=parsed_data['experience_years'],
            parsed_projects_json=json.dumps(parsed_data['projects']),
            parsed_certifications_json=json.dumps(parsed_data['certifications']),
            parsed_skills_json=json.dumps([s['name'] for s in parsed_data['skills']])
        )
        db.session.add(new_resume)
        
        # Save Extracted Skills to Candidate Skills Taxonomy
        # Clear previous parsed skills
        CandidateSkill.query.filter_by(candidate_id=candidate.id, source='parsed').delete()
        for skill_item in parsed_data['skills']:
            s_name = skill_item['name']
            s_cat = skill_item['category']
            
            db_skill = Skill.query.filter_by(name=s_name).first()
            if not db_skill:
                db_skill = Skill(name=s_name, category=s_cat)
                db.session.add(db_skill)
                db.session.flush()

            cand_skill = CandidateSkill(candidate_id=candidate.id, skill_id=db_skill.id, source='parsed')
            db.session.add(cand_skill)

        db.session.commit()
        flash('Resume PDF uploaded and parsed successfully!', 'success')
        return redirect(url_for('candidate.resume'))

    return render_template('candidate/resume.html', candidate=candidate, resume=latest_resume)


@candidate_bp.route('/jobs')
@role_required('candidate')
def jobs():
    candidate = get_current_candidate()
    search_query = request.args.get('q', '').strip()
    
    query = Job.query.filter_by(is_active=True)
    if search_query:
        query = query.filter(Job.title.ilike(f"%{search_query}%") | Job.description.ilike(f"%{search_query}%"))
    
    all_jobs = query.order_by(Job.created_at.desc()).all()
    latest_resume = Resume.query.filter_by(candidate_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()

    candidate_skills = [cs.skill.name for cs in candidate.candidate_skills]
    applied_job_ids = [app.job_id for app in Application.query.filter_by(candidate_id=candidate.id).all()]

    job_card_data = []
    for job in all_jobs:
        match_info = None
        if latest_resume and latest_resume.raw_text:
            match_info = JobMatcher.match(
                latest_resume.raw_text,
                candidate_skills,
                job.description,
                job.get_required_skills_list()
            )
        job_card_data.append({
            'job': job,
            'match': match_info,
            'has_applied': job.id in applied_job_ids
        })

    return render_template('candidate/jobs.html', job_card_data=job_card_data, search_query=search_query, has_resume=bool(latest_resume))


@candidate_bp.route('/apply/<int:job_id>', methods=['POST'])
@role_required('candidate')
def apply_job(job_id):
    candidate = get_current_candidate()
    job = Job.query.get_or_404(job_id)
    if not job.is_active:
        flash('This job is no longer accepting applications.', 'warning')
        return redirect(url_for('candidate.jobs'))

    latest_resume = Resume.query.filter_by(candidate_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()
    if not latest_resume:
        flash('Please upload your resume PDF before applying for a job.', 'warning')
        return redirect(url_for('candidate.resume'))

    existing_app = Application.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
    if existing_app:
        flash('You have already applied for this position.', 'info')
        return redirect(url_for('candidate.applications'))

    cand_skills = [cs.skill.name for cs in candidate.candidate_skills]
    match_info = JobMatcher.match(
        latest_resume.raw_text,
        cand_skills,
        job.description,
        job.get_required_skills_list()
    )

    # Create Application. Before the interview, the interview component is 0,
    # while the other configured components still contribute transparently.
    exp_score = RankingEngine.calculate_experience_score(
        latest_resume.parsed_experience_years or 0,
        job.experience_years
    )
    preliminary_score, _ = RankingEngine.calculate_final_score(
        match_info['overall_match_score'],
        0.0,
        match_info['skill_match_score'],
        exp_score,
        job.get_weights()
    )

    application = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=latest_resume.id,
        status='Applied',
        match_score=match_info['overall_match_score'],
        interview_score=0.0,
        final_score=preliminary_score
    )
    db.session.add(application)
    db.session.flush()

    # Generate Skill Gap Analysis Record
    gap_analysis = RankingEngine.generate_skill_gap_analysis(
        job.title, match_info['matching_skills'], match_info['missing_skills']
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

    flash(f'Successfully applied for {job.title}! Match score: {match_info["overall_match_score"]}%. You can now start the AI Interview.', 'success')
    return redirect(url_for('candidate.applications'))


@candidate_bp.route('/applications')
@role_required('candidate')
def applications():
    candidate = get_current_candidate()
    apps = Application.query.filter_by(candidate_id=candidate.id).order_by(Application.applied_at.desc()).all()
    return render_template('candidate/applications.html', applications=apps)


@candidate_bp.route('/interview/<int:application_id>')
@role_required('candidate')
def interview(application_id):
    candidate = get_current_candidate()
    app_record = Application.query.get_or_404(application_id)
    if app_record.candidate_id != candidate.id:
        flash('Unauthorized access to interview.', 'danger')
        return redirect(url_for('candidate.applications'))

    job = app_record.job
    interview_record = Interview.query.filter_by(application_id=app_record.id).first()

    if interview_record and interview_record.status == 'Completed':
        flash('This interview has already been completed.', 'info')
        return redirect(url_for('candidate.results', application_id=app_record.id))

    if not interview_record:
        # Create Interview Session with tailored questions
        interview_record = Interview(
            application_id=app_record.id,
            status='In Progress',
            started_at=datetime.utcnow()
        )
        db.session.add(interview_record)
        db.session.flush()

        latest_resume = Resume.query.get(app_record.resume_id)
        cand_skills = latest_resume.get_parsed_skills() if latest_resume else []
        req_skills = job.get_required_skills_list()

        generated_qs = InterviewEngine.generate_questions(
            req_skills, cand_skills, question_count=job.question_count, difficulty=job.difficulty
        )

        for q in generated_qs:
            iq = InterviewQuestion(
                interview_id=interview_record.id,
                question_text=q['question'],
                category=q['category'],
                difficulty=q['difficulty'],
                expected_keywords_json=json.dumps(q.get('keywords', [])),
                sample_answer=q.get('sample_answer', '')
            )
            db.session.add(iq)

        db.session.commit()

    return render_template('candidate/interview.html',
                           application=app_record,
                           job=job,
                           interview=interview_record)


@candidate_bp.route('/interview/<int:interview_id>/submit', methods=['POST'])
@role_required('candidate')
def submit_interview(interview_id):
    interview_record = Interview.query.get_or_404(interview_id)
    app_record = interview_record.application

    # Never allow a candidate to submit another candidate's interview.
    candidate = get_current_candidate()
    if not candidate or app_record.candidate_id != candidate.id:
        flash('Unauthorized access to interview.', 'danger')
        return redirect(url_for('candidate.applications'))

    if interview_record.status == 'Completed':
        flash('This interview has already been submitted.', 'info')
        return redirect(url_for('candidate.results', application_id=app_record.id))

    qa_data = []
    for question in interview_record.questions:
        answer_text = request.form.get(f'answer_{question.id}', '').strip()
        
        # Evaluate each answer using AnswerEvaluator AI service
        keywords = question.get_keywords()
        score, feedback = AnswerEvaluator.evaluate_answer(answer_text, keywords, question.sample_answer)

        # Save or update answer
        ans_obj = InterviewAnswer.query.filter_by(question_id=question.id).first()
        if not ans_obj:
            ans_obj = InterviewAnswer(question_id=question.id)
            db.session.add(ans_obj)

        ans_obj.answer_text = answer_text
        ans_obj.score = score
        ans_obj.feedback_json = json.dumps(feedback)
        
        qa_data.append({
            'score': score,
            'feedback': feedback
        })

    # Evaluate Overall Interview Session
    avg_interview_score, strengths, weaknesses, suggestions = AnswerEvaluator.evaluate_interview_session(qa_data)

    interview_record.status = 'Completed'
    interview_record.total_score = avg_interview_score
    interview_record.completed_at = datetime.utcnow()

    # Update Application & Calculate Final Candidate Score
    app_record.status = 'Interviewed'
    app_record.interview_score = avg_interview_score

    job = app_record.job
    latest_resume = Resume.query.get(app_record.resume_id)
    cand_exp = latest_resume.parsed_experience_years if latest_resume else 1.0
    cand_skills = latest_resume.get_parsed_skills() if latest_resume else []
    
    match_info = JobMatcher.match(
        latest_resume.raw_text if latest_resume else '',
        cand_skills,
        job.description,
        job.get_required_skills_list()
    )

    exp_score = RankingEngine.calculate_experience_score(cand_exp, job.experience_years)

    final_score, breakdown = RankingEngine.calculate_final_score(
        match_info['overall_match_score'],
        avg_interview_score,
        match_info['skill_match_score'],
        exp_score,
        job.get_weights()
    )

    app_record.final_score = final_score

    # Save Score Breakdown Object
    score_obj = Score.query.filter_by(application_id=app_record.id).first()
    if not score_obj:
        score_obj = Score(application_id=app_record.id)
        db.session.add(score_obj)

    score_obj.resume_match_score = match_info['overall_match_score']
    score_obj.interview_score = avg_interview_score
    score_obj.skill_match_score = match_info['skill_match_score']
    score_obj.experience_score = exp_score
    score_obj.final_score = final_score
    score_obj.weights_json = json.dumps(breakdown['weights_used'])

    db.session.commit()

    flash(f'Interview submitted and evaluated successfully! Overall Interview Score: {avg_interview_score}%', 'success')
    return redirect(url_for('candidate.results', application_id=app_record.id))


@candidate_bp.route('/results/<int:application_id>')
@role_required('candidate')
def results(application_id):
    candidate = get_current_candidate()
    app_record = Application.query.get_or_404(application_id)
    if app_record.candidate_id != candidate.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('candidate.applications'))

    interview_record = Interview.query.filter_by(application_id=app_record.id).first()
    score_record = Score.query.filter_by(application_id=app_record.id).first()

    return render_template('candidate/results.html',
                           application=app_record,
                           interview=interview_record,
                           score=score_record)


@candidate_bp.route('/skill-gap/<int:application_id>')
@role_required('candidate')
def skill_gap(application_id):
    candidate = get_current_candidate()
    app_record = Application.query.get_or_404(application_id)
    if app_record.candidate_id != candidate.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('candidate.applications'))

    recommendation = Recommendation.query.filter_by(application_id=app_record.id).first()
    return render_template('candidate/skill_gap.html', application=app_record, recommendation=recommendation)
