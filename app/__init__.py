from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration for Render
    if os.environ.get('DATABASE_URL'):
        # Use PostgreSQL on Render
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    else:
        # Use SQLite for local development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database creation error: {e}")

    return app 