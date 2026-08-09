from datetime import datetime
from app.models import db

class Application(db.Model):
    __tablename__ = 'applications'
    __table_args__ = (
        db.UniqueConstraint('candidate_id', 'job_id', name='uq_application_candidate_job'),
    )

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    
    status = db.Column(db.String(30), default='Applied')  # 'Applied', 'Interviewed', 'Shortlisted', 'Rejected'
    match_score = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    final_score = db.Column(db.Float, default=0.0)
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interviews = db.relationship('Interview', backref='application', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='application', cascade='all, delete-orphan')
    recommendation = db.relationship('Recommendation', backref='application', uselist=False, cascade='all, delete-orphan')
    resume = db.relationship('Resume')

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.full_name if self.candidate else '',
            'candidate_email': self.candidate.user.email if self.candidate and self.candidate.user else '',
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else '',
            'status': self.status,
            'match_score': round(self.match_score, 1),
            'interview_score': round(self.interview_score, 1),
            'final_score': round(self.final_score, 1),
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
