import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import db, Recruiter, Job, Application, Candidate, Resume, Score, Interview, Recommendation
from app.utils.decorators import role_required
from app.services.ranking_engine import RankingEngine

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

def get_current_recruiter():
    user_id = session.get('user_id')
    return Recruiter.query.filter_by(user_id=user_id).first()


def parse_job_settings(form):
    """Parse and validate recruiter-controlled job/interview settings."""
    try:
        experience_years = int(form.get('experience_years', 0))
        question_count = int(form.get('question_count', 5))
        interview_duration_mins = int(form.get('interview_duration_mins', 15))
        weights = {
            'resume_match': float(form.get('weight_resume', 40)),
            'interview': float(form.get('weight_interview', 35)),
            'skill_match': float(form.get('weight_skill', 15)),
            'experience': float(form.get('weight_exp', 10)),
        }
    except (TypeError, ValueError):
        raise ValueError('Experience, interview settings, and weights must be valid numbers.')

    if not 0 <= experience_years <= 50:
        raise ValueError('Experience years must be between 0 and 50.')
    if not 3 <= question_count <= 20:
        raise ValueError('Interview question count must be between 3 and 20.')
    if not 1 <= interview_duration_mins <= 180:
        raise ValueError('Interview duration must be between 1 and 180 minutes.')
    if any(value < 0 or value > 100 for value in weights.values()):
        raise ValueError('Ranking weights must be between 0 and 100.')
    if sum(weights.values()) <= 0:
        raise ValueError('At least one ranking weight must be greater than zero.')

    return experience_years, question_count, interview_duration_mins, {
        key: value / 100.0 for key, value in weights.items()
    }


@recruiter_bp.route('/dashboard')
@role_required('recruiter')
def dashboard():
    recruiter = get_current_recruiter()
    if not recruiter:
        flash('Recruiter profile not found.', 'danger')
        return redirect(url_for('index'))

    jobs = Job.query.filter_by(recruiter_id=recruiter.id).all()
    job_ids = [j.id for j in jobs]

    applications = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all() if job_ids else []

    total_jobs = len(jobs)
    total_applications = len(applications)
    shortlisted_count = sum(1 for a in applications if a.status == 'Shortlisted')
    rejected_count = sum(1 for a in applications if a.status == 'Rejected')
    
    avg_match_score = round(sum(a.match_score for a in applications) / total_applications, 1) if total_applications > 0 else 0.0

    # Top candidates ranked by Final Score
    top_candidates = sorted(applications, key=lambda a: a.final_score, reverse=True)[:5]

    return render_template('recruiter/dashboard.html',
                           recruiter=recruiter,
                           total_jobs=total_jobs,
                           total_applications=total_applications,
                           shortlisted_count=shortlisted_count,
                           rejected_count=rejected_count,
                           avg_match_score=avg_match_score,
                           recent_applications=applications[:5],
                           top_candidates=top_candidates)


@recruiter_bp.route('/jobs')
@role_required('recruiter')
def jobs():
    recruiter = get_current_recruiter()
    all_jobs = Job.query.filter_by(recruiter_id=recruiter.id).order_by(Job.created_at.desc()).all()
    return render_template('recruiter/jobs.html', jobs=all_jobs)


@recruiter_bp.route('/jobs/create', methods=['GET', 'POST'])
@role_required('recruiter')
def create_job():
    recruiter = get_current_recruiter()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        try:
            experience_years, question_count, interview_duration_mins, weights_dict = parse_job_settings(request.form)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('recruiter/job_form.html', action='Create', job=None)

        difficulty = request.form.get('difficulty', 'Medium')
        if difficulty not in {'Easy', 'Medium', 'Hard'}:
            flash('Invalid interview difficulty.', 'danger')
            return render_template('recruiter/job_form.html', action='Create', job=None)

        if not title or not description or not required_skills:
            flash('Title, description, and required skills are mandatory fields.', 'danger')
            return render_template('recruiter/job_form.html', action='Create')

        job = Job(
            recruiter_id=recruiter.id,
            title=title,
            department=department,
            location=location,
            job_type=job_type,
            description=description,
            required_skills_text=required_skills,
            experience_years=experience_years,
            question_count=question_count,
            difficulty=difficulty,
            interview_duration_mins=interview_duration_mins
        )
        job.set_weights(weights_dict)

        db.session.add(job)
        db.session.commit()

        flash(f'Job posting "{title}" created successfully!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/job_form.html', action='Create', job=None)


@recruiter_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@role_required('recruiter')
def edit_job(job_id):
    recruiter = get_current_recruiter()
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != recruiter.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.jobs'))

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.department = request.form.get('department', '').strip()
        job.location = request.form.get('location', '').strip()
        job.job_type = request.form.get('job_type', 'Full-time')
        job.description = request.form.get('description', '').strip()
        job.required_skills_text = request.form.get('required_skills', '').strip()
        try:
            experience_years, question_count, interview_duration_mins, weights_dict = parse_job_settings(request.form)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('recruiter/job_form.html', action='Edit', job=job)

        difficulty = request.form.get('difficulty', 'Medium')
        if difficulty not in {'Easy', 'Medium', 'Hard'}:
            flash('Invalid interview difficulty.', 'danger')
            return render_template('recruiter/job_form.html', action='Edit', job=job)

        job.experience_years = experience_years
        job.question_count = question_count
        job.difficulty = difficulty
        job.interview_duration_mins = interview_duration_mins
        job.set_weights(weights_dict)

        db.session.commit()
        flash(f'Job "{job.title}" updated successfully!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/job_form.html', action='Edit', job=job)


@recruiter_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@role_required('recruiter')
def delete_job(job_id):
    recruiter = get_current_recruiter()
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != recruiter.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.jobs'))

    db.session.delete(job)
    db.session.commit()
    flash('Job posting deleted successfully.', 'info')
    return redirect(url_for('recruiter.jobs'))


@recruiter_bp.route('/applicants')
@role_required('recruiter')
def applicants():
    recruiter = get_current_recruiter()
    jobs = Job.query.filter_by(recruiter_id=recruiter.id).all()
    job_ids = [j.id for j in jobs]

    selected_job_id = request.args.get('job_id', type=int)
    status_filter = request.args.get('status', '').strip()
    search_q = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'final_score')

    query = Application.query.filter(Application.job_id.in_(job_ids)) if job_ids else Application.query.filter(False)

    if selected_job_id:
        query = query.filter_by(job_id=selected_job_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    all_apps = query.all()

    # Client search & candidate name filter
    if search_q:
        q_lower = search_q.lower()
        all_apps = [a for a in all_apps if q_lower in a.candidate.full_name.lower() or q_lower in a.job.title.lower()]

    # Sorting
    if sort_by == 'final_score':
        all_apps = sorted(all_apps, key=lambda a: a.final_score, reverse=True)
    elif sort_by == 'match_score':
        all_apps = sorted(all_apps, key=lambda a: a.match_score, reverse=True)
    elif sort_by == 'interview_score':
        all_apps = sorted(all_apps, key=lambda a: a.interview_score, reverse=True)
    elif sort_by == 'applied_at':
        all_apps = sorted(all_apps, key=lambda a: a.applied_at, reverse=True)

    return render_template('recruiter/applicants.html',
                           applicants=all_apps,
                           jobs=jobs,
                           selected_job_id=selected_job_id,
                           status_filter=status_filter,
                           search_q=search_q,
                           sort_by=sort_by)


@recruiter_bp.route('/candidates/<int:application_id>')
@role_required('recruiter')
def candidate_detail(application_id):
    recruiter = get_current_recruiter()
    app_record = Application.query.get_or_404(application_id)
    if app_record.job.recruiter_id != recruiter.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.applicants'))

    candidate = app_record.candidate
    resume = Resume.query.get(app_record.resume_id)
    score_record = Score.query.filter_by(application_id=app_record.id).first()
    interview_record = Interview.query.filter_by(application_id=app_record.id).first()
    recommendation = Recommendation.query.filter_by(application_id=app_record.id).first()

    return render_template('recruiter/candidate_detail.html',
                           application=app_record,
                           candidate=candidate,
                           resume=resume,
                           score=score_record,
                           interview=interview_record,
                           recommendation=recommendation)


@recruiter_bp.route('/candidates/<int:application_id>/status', methods=['POST'])
@role_required('recruiter')
def update_status(application_id):
    recruiter = get_current_recruiter()
    app_record = Application.query.get_or_404(application_id)
    if app_record.job.recruiter_id != recruiter.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('recruiter.applicants'))

    new_status = request.form.get('status')
    if new_status in ['Shortlisted', 'Rejected', 'Interviewed', 'Applied']:
        app_record.status = new_status
        db.session.commit()
        flash(f'Candidate status updated to {new_status}.', 'success')

    return redirect(url_for('recruiter.candidate_detail', application_id=app_record.id))


@recruiter_bp.route('/analytics')
@role_required('recruiter')
def analytics():
    recruiter = get_current_recruiter()
    jobs = Job.query.filter_by(recruiter_id=recruiter.id).all()
    job_ids = [j.id for j in jobs]

    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []

    # Prepare Chart Data
    job_titles = [j.title for j in jobs]
    apps_per_job = [len(j.applications) for j in jobs]

    # Score Distribution buckets
    bins = {'0-20%': 0, '21-40%': 0, '41-60%': 0, '61-80%': 0, '81-100%': 0}
    for app in applications:
        s = app.final_score
        if s <= 20: bins['0-20%'] += 1
        elif s <= 40: bins['21-40%'] += 1
        elif s <= 60: bins['41-60%'] += 1
        elif s <= 80: bins['61-80%'] += 1
        else: bins['81-100%'] += 1

    # Status counts
    status_counts = {
        'Applied': sum(1 for a in applications if a.status == 'Applied'),
        'Interviewed': sum(1 for a in applications if a.status == 'Interviewed'),
        'Shortlisted': sum(1 for a in applications if a.status == 'Shortlisted'),
        'Rejected': sum(1 for a in applications if a.status == 'Rejected')
    }

    return render_template('recruiter/analytics.html',
                           jobs=jobs,
                           total_applications=len(applications),
                           job_titles_json=json.dumps(job_titles),
                           apps_per_job_json=json.dumps(apps_per_job),
                           score_bins_json=json.dumps(bins),
                           status_counts_json=json.dumps(status_counts))
