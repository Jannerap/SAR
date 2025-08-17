#!/usr/bin/env python3
"""
Database Initialization Script for SAR Tracking System
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User
from app.auth import get_password_hash

def init_database():
    """Initialize the database and create tables."""
    print("🗄️  Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Check if we need to create a default user
    db = SessionLocal()
    try:
        # Check if any users exist
        existing_user = db.query(User).first()
        
        if not existing_user:
            print("👤 Creating default user...")
            
            # Create default admin user
            default_user = User(
                username="admin",
                email="admin@sartracker.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True
            )
            
            db.add(default_user)
            db.commit()
            
            print("✅ Default user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change this password after first login!")
        else:
            print("ℹ️  Users already exist, skipping default user creation.")
            
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function to initialize the database."""
    print("🚀 SAR Tracking System - Database Initialization")
    print("=" * 50)
    
    try:
        init_database()
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend: python run.py")
        print("2. Install frontend dependencies: cd frontend && npm install")
        print("3. Start the frontend: cd frontend && npm start")
        print("4. Login with admin/admin123")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
