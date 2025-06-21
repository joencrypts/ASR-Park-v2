#!/usr/bin/env python3
"""
Database test script to verify connection and tables
"""

import os
from app import create_app, db
from app.models import User, Entry

def test_database():
    """Test database connection and basic operations"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Testing database connection...")
            
            # Test if tables exist
            print("Checking if tables exist...")
            tables = db.engine.table_names()
            print(f"Found tables: {tables}")
            
            # Test User table
            print("\nTesting User table...")
            user_count = User.query.count()
            print(f"Total users: {user_count}")
            
            # Test Entry table
            print("\nTesting Entry table...")
            entry_count = Entry.query.count()
            print(f"Total entries: {entry_count}")
            
            # Test creating a user
            print("\nTesting user creation...")
            test_user = User.query.filter_by(username='test_user').first()
            if not test_user:
                test_user = User(
                    username='test_user',
                    email='test@example.com',
                    role='staff'
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created successfully")
            else:
                print("✅ Test user already exists")
            
            # Test querying the user
            found_user = User.query.filter_by(username='test_user').first()
            if found_user:
                print(f"✅ Found user: {found_user.username} ({found_user.role})")
            else:
                print("❌ Could not find test user")
            
            print("\n🎉 Database test completed successfully!")
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_database() 