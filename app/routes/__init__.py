from app.routes.auth import auth_bp
from app.routes.candidate import candidate_bp
from app.routes.recruiter import recruiter_bp
from app.routes.api import api_bp

__all__ = ['auth_bp', 'candidate_bp', 'recruiter_bp', 'api_bp']
