from app import create_app, db
from app.models import User, Entry
from flask_migrate import Migrate, upgrade, init, migrate
import os

def setup_migrations():
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        # Initialize migrations if not already done
        if not os.path.exists('migrations'):
            init()
            print("Migrations initialized!")
        
        # Create initial migration
        migrate(message="Initial migration with User and Entry models")
        print("Migration created!")
        
        # Apply migration
        upgrade()
        print("Migration applied!")
        
        # Create default users
        admin_user = User.query.filter_by(email='dmr@asr.com').first()
        if not admin_user:
            admin = User(email='dmr@asr.com', role='admin')
            admin.set_password('azeedmr123')
            db.session.add(admin)
            
            staff = User(email='staff1@asr.com', role='staff')
            staff.set_password('staff1@54321')
            db.session.add(staff)
            
            db.session.commit()
            print("Default users created:")
            print("Admin: dmr@asr.com / azeedmr123")
            print("Staff: staff1@asr.com / staff1@54321")

if __name__ == '__main__':
    setup_migrations() 