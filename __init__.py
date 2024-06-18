from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    if config_name:
        app.config.from_object(config_name)
    else:
        app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    from .models import User, Group, GroupMember, Expense

    with app.app_context():
        from . import routes  # Import routes here to avoid circular import issues
        from .routes import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

        # Uncomment this for initial database setup, then remove/comment it for production
        db.create_all()

    return app
