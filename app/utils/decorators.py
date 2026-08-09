from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role')
            if user_role != role:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized access for your role'}), 403
                flash('You do not have permission to access that page.', 'danger')
                if user_role == 'candidate':
                    return redirect(url_for('candidate.dashboard'))
                elif user_role == 'recruiter':
                    return redirect(url_for('recruiter.dashboard'))
                else:
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
