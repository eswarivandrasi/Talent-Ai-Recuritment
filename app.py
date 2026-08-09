import os
from app import create_app
from app.models import db

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# Ensure database tables exist automatically on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
