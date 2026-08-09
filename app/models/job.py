import json
from datetime import datetime
from app.models import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Remote, Contract
    description = db.Column(db.Text, nullable=False)
    required_skills_text = db.Column(db.Text, nullable=False)  # Comma-separated or JSON list
    experience_years = db.Column(db.Integer, default=0)
    
    # Custom evaluation weights
    weights_json = db.Column(db.Text, nullable=True)  # JSON e.g. {"resume_match": 0.4, "interview": 0.35, "skill_match": 0.15, "experience": 0.1}
    
    # AI Interview Configuration
    question_count = db.Column(db.Integer, default=5)
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    interview_duration_mins = db.Column(db.Integer, default=15)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job', cascade='all, delete-orphan')

    def get_weights(self):
        if self.weights_json:
            try:
                return json.loads(self.weights_json)
            except Exception:
                pass
        return {
            'resume_match': 0.40,
            'interview': 0.35,
            'skill_match': 0.15,
            'experience': 0.10
        }

    def set_weights(self, weights_dict):
        self.weights_json = json.dumps(weights_dict)

    def get_required_skills_list(self):
        if not self.required_skills_text:
            return []
        try:
            parsed = json.loads(self.required_skills_text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [s.strip() for s in self.required_skills_text.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'company_name': self.recruiter.company_name if self.recruiter else '',
            'title': self.title,
            'department': self.department,
            'location': self.location,
            'job_type': self.job_type,
            'description': self.description,
            'required_skills': self.get_required_skills_list(),
            'experience_years': self.experience_years,
            'weights': self.get_weights(),
            'question_count': self.question_count,
            'difficulty': self.difficulty,
            'interview_duration_mins': self.interview_duration_mins,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'applicant_count': len(self.applications)
        }
