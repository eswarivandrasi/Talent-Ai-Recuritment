from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User, Candidate, Recruiter
from app.utils.security import sanitize_input, validate_email, validate_password_strength

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect_role_dashboard(session.get('role'))

    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', '')).lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'candidate')
        full_name = sanitize_input(request.form.get('full_name', ''))
        company_name = sanitize_input(request.form.get('company_name', ''))

        # Validations
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/register.html')

        valid_pwd, msg = validate_password_strength(password)
        if not valid_pwd:
            flash(msg, 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if role not in ['candidate', 'recruiter']:
            flash('Invalid user role selected.', 'danger')
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html')

        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'candidate':
            if not full_name:
                full_name = email.split('@')[0].title()
            candidate = Candidate(user_id=user.id, full_name=full_name)
            db.session.add(candidate)
        elif role == 'recruiter':
            if not company_name:
                company_name = 'Enterprise Tech'
            recruiter = Recruiter(user_id=user.id, company_name=company_name)
            db.session.add(recruiter)

        db.session.commit()
        flash('Registration successful! Please log in to continue.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_role_dashboard(session.get('role'))

    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', '')).lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        # Set session
        session.clear()
        session['user_id'] = user.id
        session['role'] = user.role
        session['email'] = user.email

        if user.role == 'candidate' and user.candidate_profile:
            session['name'] = user.candidate_profile.full_name
            session['candidate_id'] = user.candidate_profile.id
        elif user.role == 'recruiter' and user.recruiter_profile:
            session['name'] = user.recruiter_profile.company_name
            session['recruiter_id'] = user.recruiter_profile.id
        else:
            session['name'] = user.email.split('@')[0].title()

        flash(f'Welcome back, {session["name"]}!', 'success')

        next_page = request.args.get('next')
        if next_page and not next_page.startswith('http'):
            return redirect(next_page)

        return redirect_role_dashboard(user.role)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


def redirect_role_dashboard(role):
    if role == 'candidate':
        return redirect(url_for('candidate.dashboard'))
    elif role == 'recruiter':
        return redirect(url_for('recruiter.dashboard'))
    return redirect(url_for('index'))
