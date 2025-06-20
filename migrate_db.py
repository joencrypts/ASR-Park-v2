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
        admin_user = User.query.filter_by(email='admin@asrparking.com').first()
        if not admin_user:
            admin = User(email='admin@asrparking.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            staff = User(email='staff@asrparking.com', role='staff')
            staff.set_password('staff123')
            db.session.add(staff)
            
            db.session.commit()
            print("Default users created:")
            print("Admin: admin@asrparking.com / admin123")
            print("Staff: staff@asrparking.com / staff123")

if __name__ == '__main__':
    setup_migrations() 