from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.utils import get_current_ist

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(10), index=True, nullable=False, default='staff') # 'admin' or 'staff'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    device = db.Column(db.String(50), nullable=False)
    entry_time = db.Column(db.DateTime, default=get_current_ist, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    amount = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Entry {self.ticket_number}>' 