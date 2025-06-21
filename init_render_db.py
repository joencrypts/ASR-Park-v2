#!/usr/bin/env python3
"""
Database initialization script for Render deployment
This script creates the database tables and adds initial admin user
"""

import os
import sys
from app import create_app, db
from app.models import User, Entry

def init_database():
    """Initialize the database with tables and initial data"""
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
            sys.exit(1)

if __name__ == '__main__':
    init_database() 