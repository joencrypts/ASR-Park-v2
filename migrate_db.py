from app import create_app, db
from app.models import User, Entry
from flask_migrate import upgrade, init, migrate
import os
import shutil

def setup_database():
    app = create_app()
    with app.app_context():
        # Remove existing migrations folder if it exists (for fresh start)
        migrations_dir = 'migrations'
        if os.path.exists(migrations_dir):
            try:
                shutil.rmtree(migrations_dir)
                print("Removed existing migrations folder")
            except Exception as e:
                print(f"Could not remove migrations folder: {e}")
        
        # Initialize fresh migrations
        try:
            init()
            print("Migrations initialized!")
        except Exception as e:
            print(f"Migrations initialization error: {e}")
            return
        
        # Create initial migration
        try:
            migrate(message="Initial migration")
            print("Initial migration created!")
        except Exception as e:
            print(f"Migration creation error: {e}")
            return
        
        # Apply migrations
        try:
            upgrade()
            print("Migrations applied successfully!")
        except Exception as e:
            print(f"Upgrade error: {e}")
            return
        
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