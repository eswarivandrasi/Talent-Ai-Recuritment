import json
from datetime import datetime
from app.models import db

class Score(db.Model):
    __tablename__ = 'scores'
    __table_args__ = (
        db.UniqueConstraint('application_id', name='uq_score_application'),
    )

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    resume_match_score = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    skill_match_score = db.Column(db.Float, default=0.0)
    experience_score = db.Column(db.Float, default=0.0)
    final_score = db.Column(db.Float, default=0.0)
    weights_json = db.Column(db.Text, nullable=True)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_weights(self):
        if self.weights_json:
            try:
                return json.loads(self.weights_json)
            except Exception:
                pass
        return {}

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'resume_match_score': round(self.resume_match_score, 1),
            'interview_score': round(self.interview_score, 1),
            'skill_match_score': round(self.skill_match_score, 1),
            'experience_score': round(self.experience_score, 1),
            'final_score': round(self.final_score, 1),
            'weights': self.get_weights(),
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    __table_args__ = (
        db.UniqueConstraint('application_id', name='uq_recommendation_application'),
    )

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    strong_skills_json = db.Column(db.Text, nullable=True)
    missing_skills_json = db.Column(db.Text, nullable=True)
    learning_recommendations_json = db.Column(db.Text, nullable=True)
    overall_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_strong_skills(self):
        if self.strong_skills_json:
            try:
                return json.loads(self.strong_skills_json)
            except Exception:
                pass
        return []

    def get_missing_skills(self):
        if self.missing_skills_json:
            try:
                return json.loads(self.missing_skills_json)
            except Exception:
                pass
        return []

    def get_learning_recommendations(self):
        if self.learning_recommendations_json:
            try:
                return json.loads(self.learning_recommendations_json)
            except Exception:
                pass
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'strong_skills': self.get_strong_skills(),
            'missing_skills': self.get_missing_skills(),
            'learning_recommendations': self.get_learning_recommendations(),
            'overall_summary': self.overall_summary
        }
