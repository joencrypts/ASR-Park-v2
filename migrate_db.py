from app import create_app, db
from app.models import User, Entry
from flask_migrate import upgrade, init, migrate
import os

def setup_database():
    app = create_app()
    with app.app_context():
        # Initialize migrations if not already done
        try:
            init()
            print("Migrations initialized!")
        except Exception as e:
            print(f"Migrations already initialized or error: {e}")
        
        # Create migration
        try:
            migrate()
            print("Migration created!")
        except Exception as e:
            print(f"Migration error: {e}")
        
        # Apply migrations
        try:
            upgrade()
            print("Migrations applied successfully!")
        except Exception as e:
            print(f"Upgrade error: {e}")
        
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
        else:
            print("Default users already exist!")

if __name__ == '__main__':
    setup_database() 