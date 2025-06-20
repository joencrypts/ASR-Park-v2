from app import create_app, db
from app.models import User, Entry
from datetime import datetime

def init_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@asrparking.com').first()
        if not admin_user:
            # Create admin user
            admin = User(username='admin', email='admin@asrparking.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create staff user
            staff = User(username='staff', email='staff@asrparking.com', role='staff')
            staff.set_password('staff123')
            db.session.add(staff)
            
            db.session.commit()
            print("Default users created:")
            print("Admin: admin / admin@asrparking.com / admin123")
            print("Staff: staff / staff@asrparking.com / staff123")

if __name__ == '__main__':
    init_database() 