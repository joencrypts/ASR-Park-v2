from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from app.utils import format_device_time_full, format_device_time_medium, format_device_time_short, format_device_date, format_device_date_short, format_device_time_receipt, format_device_receipt_id, format_ist_time_full, format_ist_time_medium, format_ist_time_short, format_ist_date, format_ist_date_short, format_ist_time_receipt, format_ist_receipt_id, get_current_device_time

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Register custom Jinja2 filters for device time formatting
    app.jinja_env.filters['device_full'] = format_device_time_full
    app.jinja_env.filters['device_medium'] = format_device_time_medium
    app.jinja_env.filters['device_short'] = format_device_time_short
    app.jinja_env.filters['device_date'] = format_device_date
    app.jinja_env.filters['device_date_short'] = format_device_date_short
    app.jinja_env.filters['device_receipt'] = format_device_time_receipt
    app.jinja_env.filters['device_receipt_id'] = format_device_receipt_id

    # Register custom Jinja2 filters for IST time formatting (for display)
    app.jinja_env.filters['ist_full'] = format_ist_time_full
    app.jinja_env.filters['ist_medium'] = format_ist_time_medium
    app.jinja_env.filters['ist_short'] = format_ist_time_short
    app.jinja_env.filters['ist_date'] = format_ist_date
    app.jinja_env.filters['ist_date_short'] = format_ist_date_short
    app.jinja_env.filters['ist_receipt'] = format_ist_time_receipt
    app.jinja_env.filters['ist_receipt_id'] = format_ist_receipt_id

    # Add get_current_device_time to template context
    app.jinja_env.globals['get_current_device_time'] = get_current_device_time

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app 
 