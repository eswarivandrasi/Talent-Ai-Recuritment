import json
from flask import Blueprint, jsonify, request, session
from app.models import db, Job, Application, Candidate, Resume, Score
from app.services.job_matcher import JobMatcher
from app.services.answer_evaluator import AnswerEvaluator
from app.services.ranking_engine import RankingEngine
from app.utils.decorators import role_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(jobs),
        'jobs': [j.to_dict() for j in jobs]
    }), 200


@api_bp.route('/match', methods=['POST'])
def match_resume_to_job():
    data = request.get_json() or {}
    resume_text = data.get('resume_text', '')
    candidate_skills = data.get('candidate_skills', [])
    job_description = data.get('job_description', '')
    required_skills = data.get('required_skills', [])

    if not resume_text or not job_description:
        return jsonify({'error': 'Missing resume_text or job_description'}), 400

    match_result = JobMatcher.match(
        resume_text, candidate_skills, job_description, required_skills
    )
    return jsonify({
        'status': 'success',
        'result': match_result
    }), 200


@api_bp.route('/interview/evaluate', methods=['POST'])
def evaluate_answer_api():
    data = request.get_json() or {}
    answer_text = data.get('answer_text', '')
    expected_keywords = data.get('expected_keywords', [])
    sample_answer = data.get('sample_answer', None)

    score, feedback = AnswerEvaluator.evaluate_answer(answer_text, expected_keywords, sample_answer)
    return jsonify({
        'status': 'success',
        'score': score,
        'feedback': feedback
    }), 200


@api_bp.route('/candidates/rank/<int:job_id>', methods=['GET'])
@role_required('recruiter')
def rank_candidates(job_id):
    job = Job.query.get_or_404(job_id)
    recruiter_id = session.get('recruiter_id')
    if job.recruiter_id != recruiter_id:
        return jsonify({'error': 'You do not have access to this job.'}), 403
    applications = Application.query.filter_by(job_id=job.id).all()

    ranked = sorted(applications, key=lambda a: a.final_score, reverse=True)

    results = []
    for rank, app in enumerate(ranked, 1):
        score_rec = Score.query.filter_by(application_id=app.id).first()
        results.append({
            'rank': rank,
            'application_id': app.id,
            'candidate_name': app.candidate.full_name,
            'email': app.candidate.user.email,
            'final_score': app.final_score,
            'match_score': app.match_score,
            'interview_score': app.interview_score,
            'status': app.status,
            'score_breakdown': score_rec.to_dict() if score_rec else None
        })

    return jsonify({
        'status': 'success',
        'job_title': job.title,
        'total_candidates': len(results),
        'rankings': results
    }), 200
