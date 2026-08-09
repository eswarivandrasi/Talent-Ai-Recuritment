import json
from datetime import datetime
from app.models import db

class Interview(db.Model):
    __tablename__ = 'interviews'
    __table_args__ = (
        db.UniqueConstraint('application_id', name='uq_interview_application'),
    )

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    status = db.Column(db.String(30), default='Pending')  # Pending, In Progress, Completed
    total_score = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    questions = db.relationship('InterviewQuestion', backref='interview', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'status': self.status,
            'total_score': round(self.total_score, 1),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'question_count': len(self.questions)
        }


class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Technical')  # Technical, HR, Behavioral, Project-based
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    expected_keywords_json = db.Column(db.Text, nullable=True)
    sample_answer = db.Column(db.Text, nullable=True)

    # Relationships
    answer = db.relationship('InterviewAnswer', backref='question', uselist=False, cascade='all, delete-orphan')

    def get_keywords(self):
        if self.expected_keywords_json:
            try:
                return json.loads(self.expected_keywords_json)
            except Exception:
                pass
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'question_text': self.question_text,
            'category': self.category,
            'difficulty': self.difficulty,
            'keywords': self.get_keywords(),
            'answer': self.answer.to_dict() if self.answer else None
        }


class InterviewAnswer(db.Model):
    __tablename__ = 'interview_answers'
    __table_args__ = (
        db.UniqueConstraint('question_id', name='uq_interview_answer_question'),
    )

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('interview_questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, default=0.0)
    feedback_json = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_feedback(self):
        if self.feedback_json:
            try:
                return json.loads(self.feedback_json)
            except Exception:
                pass
        return {}

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'score': round(self.score, 1),
            'feedback': self.get_feedback(),
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None
        }
