class ProductionConfig(Config):
    DEBUG = False

    db_url = os.environ.get('DATABASE_URL')

    if db_url:
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)

        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Render writable temporary directory
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/ai_recruitment.db'