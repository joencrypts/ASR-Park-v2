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
        admin_user = User.query.filter_by(email='dmr@asr.com').first()
        if not admin_user:
            # Create admin user
            admin = User(username='admin', email='dmr@asr.com', role='admin')
            admin.set_password('azeedmr123')
            db.session.add(admin)
            
            # Create staff user
            staff = User(username='staff', email='staff1@asr.com', role='staff')
            staff.set_password('staff1@54321')
            db.session.add(staff)
            
            db.session.commit()
            print("Default users created:")
            print("Admin: admin / dmr@asr.com / azeedmr123")
            print("Staff: staff / staff1@asr.com / staff1@54321")

if __name__ == '__main__':
    init_database() 