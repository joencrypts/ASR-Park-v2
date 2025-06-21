#!/usr/bin/env python3
"""
Database initialization script for Render deployment
This script creates the database tables and adds initial admin user
"""

import os
import sys
import time
from app import create_app, db
from app.models import User, Entry

def wait_for_database(max_retries=5, delay=2):
    """Wait for database to be ready with retry logic"""
    app = create_app()
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                print(f"Attempt {attempt + 1}/{max_retries}: Testing database connection...")
                db.session.execute('SELECT 1')
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            print(f"❌ Database connection failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print("❌ Max retries reached. Database connection failed.")
                return False
    return False

def init_database():
    """Initialize the database with tables and initial data"""
    print("🚀 Starting database initialization...")
    
    # Wait for database to be ready
    if not wait_for_database():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@asrparking.com',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Please change this password after first login!")
            else:
                print("✅ Admin user already exists")
            
            # Check if staff user exists
            staff_user = User.query.filter_by(username='staff').first()
            if not staff_user:
                print("Creating default staff user...")
                staff_user = User(
                    username='staff',
                    email='staff@asrparking.com',
                    role='staff'
                )
                staff_user.set_password('staff123')
                db.session.add(staff_user)
                db.session.commit()
                print("✅ Default staff user created!")
                print("   Username: staff")
                print("   Password: staff123")
                print("   ⚠️  Please change this password after first login!")
            else:
                print("✅ Staff user already exists")
            
            print("\n🎉 Database initialization completed successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    init_database() 