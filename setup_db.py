from app import create_app, db
from app.models import User, Entry
import os

def setup_database():
    app = create_app()
    with app.app_context():
        try:
            # Try the simple approach first
            print("Creating database tables...")
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
            else:
                print("Default users already exist!")
                
        except Exception as e:
            print(f"Database setup error: {e}")
            print("Trying alternative setup method...")
            
            # Fallback: try to create tables one by one
            try:
                db.engine.execute("""
                    CREATE TABLE IF NOT EXISTS "user" (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(256),
                        role VARCHAR(10) NOT NULL DEFAULT 'staff'
                    )
                """)
                
                db.engine.execute("""
                    CREATE TABLE IF NOT EXISTS entry (
                        id SERIAL PRIMARY KEY,
                        ticket_number VARCHAR(20) UNIQUE NOT NULL,
                        vehicle_type VARCHAR(50) NOT NULL,
                        vehicle_number VARCHAR(20) NOT NULL,
                        phone VARCHAR(15) NOT NULL,
                        device VARCHAR(50) NOT NULL,
                        entry_time TIMESTAMP NOT NULL,
                        exit_time TIMESTAMP,
                        paid BOOLEAN NOT NULL DEFAULT FALSE,
                        amount FLOAT
                    )
                """)
                
                print("Tables created using fallback method!")
                
                # Create default users
                from werkzeug.security import generate_password_hash
                
                # Check if admin exists
                result = db.engine.execute("SELECT id FROM \"user\" WHERE email = 'dmr@asr.com'")
                if not result.fetchone():
                    db.engine.execute("""
                        INSERT INTO "user" (username, email, password_hash, role)
                        VALUES ('admin', 'dmr@asr.com', %s, 'admin')
                    """, (generate_password_hash('azeedmr123'),))
                    
                    db.engine.execute("""
                        INSERT INTO "user" (username, email, password_hash, role)
                        VALUES ('staff', 'staff1@asr.com', %s, 'staff')
                    """, (generate_password_hash('staff1@54321'),))
                    
                    print("Default users created using fallback method!")
                else:
                    print("Default users already exist!")
                    
            except Exception as e2:
                print(f"Fallback setup also failed: {e2}")
                raise

if __name__ == '__main__':
    setup_database() 