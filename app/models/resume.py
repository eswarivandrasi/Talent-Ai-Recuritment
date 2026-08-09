import json
from datetime import datetime
from app.models import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    
    # Parsed structured data
    parsed_name = db.Column(db.String(100), nullable=True)
    parsed_email = db.Column(db.String(120), nullable=True)
    parsed_phone = db.Column(db.String(30), nullable=True)
    parsed_education_json = db.Column(db.Text, nullable=True)
    parsed_experience_years = db.Column(db.Float, default=0.0)
    parsed_projects_json = db.Column(db.Text, nullable=True)
    parsed_certifications_json = db.Column(db.Text, nullable=True)
    parsed_achievements_json = db.Column(db.Text, nullable=True)
    parsed_skills_json = db.Column(db.Text, nullable=True)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_parsed_skills(self):
        if self.parsed_skills_json:
            try:
                return json.loads(self.parsed_skills_json)
            except Exception:
                pass
        return []

    def get_parsed_education(self):
        if self.parsed_education_json:
            try:
                return json.loads(self.parsed_education_json)
            except Exception:
                pass
        return []

    def get_parsed_projects(self):
        if self.parsed_projects_json:
            try:
                return json.loads(self.parsed_projects_json)
            except Exception:
                pass
        return []

    def get_parsed_certifications(self):
        if self.parsed_certifications_json:
            try:
                return json.loads(self.parsed_certifications_json)
            except Exception:
                pass
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'parsed_name': self.parsed_name,
            'parsed_email': self.parsed_email,
            'parsed_phone': self.parsed_phone,
            'parsed_experience_years': self.parsed_experience_years,
            'skills': self.get_parsed_skills(),
            'education': self.get_parsed_education(),
            'projects': self.get_parsed_projects(),
            'certifications': self.get_parsed_certifications()
        }


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)  # Programming, AI/ML, Web, Database, Cloud/DevOps, Data

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


class CandidateSkill(db.Model):
    __tablename__ = 'candidate_skills'
    __table_args__ = (
        db.UniqueConstraint('candidate_id', 'skill_id', 'source', name='uq_candidate_skill_source'),
    )

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    source = db.Column(db.String(20), default='parsed')  # 'parsed' or 'manual'

    skill = db.relationship('Skill')
