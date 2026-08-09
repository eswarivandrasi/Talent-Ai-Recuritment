from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.user import User, Candidate, Recruiter
from app.models.job import Job
from app.models.resume import Resume, Skill, CandidateSkill
from app.models.application import Application
from app.models.interview import Interview, InterviewQuestion, InterviewAnswer
from app.models.evaluation import Score, Recommendation
