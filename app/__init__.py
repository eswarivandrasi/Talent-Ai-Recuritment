import os
from flask import Flask, render_template, jsonify
from config import config
from app.models import db

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'database'), exist_ok=True)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.candidate import candidate_bp
    from app.routes.recruiter import recruiter_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(api_bp)

    # Root routes
    @app.route('/')
    def index():
        from app.models import Job
        featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(6).all()
        return render_template('index.html', featured_jobs=featured_jobs)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'talentai-recruitment'})

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # CLI Command to create database tables
    @app.cli.command('init-db')
    def init_db_command():
        db.create_all()
        print('Initialized the database tables.')

    return app
