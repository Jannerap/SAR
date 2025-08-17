#!/usr/bin/env python3
"""
Standalone Database Initialization Script for SAR Tracking System
"""

import os
import sys
import sqlite3
from datetime import datetime
import hashlib
import secrets

def create_database():
    """Create the database and tables directly with SQL."""
    print("🗄️  Creating database tables...")
    
    # Create database file
    db_path = "sar_tracking.db"
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sar_cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sar_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            case_reference TEXT UNIQUE NOT NULL,
            organization_name TEXT NOT NULL,
            organization_address TEXT,
            organization_email TEXT,
            organization_phone TEXT,
            request_type TEXT NOT NULL,
            request_description TEXT NOT NULL,
            submission_date DATE NOT NULL,
            submission_method TEXT NOT NULL,
            statutory_deadline DATE NOT NULL,
            extended_deadline DATE,
            custom_deadline DATE,
            status TEXT DEFAULT 'Pending',
            response_received BOOLEAN DEFAULT 0,
            response_date DATE,
            response_summary TEXT,
            data_provided BOOLEAN,
            data_complete BOOLEAN,
            data_format TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create case_updates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sar_case_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            update_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            correspondence_date TIMESTAMP,
            correspondence_method TEXT,
            correspondence_summary TEXT,
            call_duration INTEGER,
            call_participants TEXT,
            call_transcript TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sar_case_id) REFERENCES sar_cases (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create case_files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sar_case_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            file_category TEXT NOT NULL,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sar_case_id) REFERENCES sar_cases (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create ico_escalations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ico_escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sar_case_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            escalation_date DATE NOT NULL,
            escalation_reason TEXT NOT NULL,
            escalation_method TEXT NOT NULL,
            ico_reference TEXT UNIQUE,
            ico_acknowledgment_received BOOLEAN DEFAULT 0,
            ico_acknowledgment_date DATE,
            ico_investigation_started BOOLEAN DEFAULT 0,
            ico_investigation_date DATE,
            ico_investigation_deadline DATE,
            ico_decision_deadline DATE,
            status TEXT DEFAULT 'Submitted',
            ico_decision TEXT,
            ico_decision_date DATE,
            ico_decision_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sar_case_id) REFERENCES sar_cases (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sar_case_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            reminder_date TIMESTAMP NOT NULL,
            reminder_type TEXT NOT NULL,
            is_recurring BOOLEAN DEFAULT 0,
            recurrence_pattern TEXT,
            is_completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (sar_case_id) REFERENCES sar_cases (id)
        )
    ''')
    
    # Create organizations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT,
            website TEXT,
            total_sars_received INTEGER DEFAULT 0,
            sars_responded_on_time INTEGER DEFAULT 0,
            sars_responded_late INTEGER DEFAULT 0,
            sars_ignored INTEGER DEFAULT 0,
            average_response_time REAL,
            compliance_rating REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Database tables created successfully!")
    
    # Check if we need to create a default user
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        print("👤 Creating default user...")
        
        # Import bcrypt for proper password hashing
        try:
            import bcrypt
            password = "admin123"
            # Hash password with bcrypt (same as auth system)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            stored_hash = password_hash.decode('utf-8')
            print("✅ Using bcrypt for password hashing")
        except ImportError:
            print("⚠️  bcrypt not available, using fallback method")
            # Fallback to simple hash if bcrypt not available
            password = "admin123"
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            stored_hash = f"{salt}${password_hash}"
        
        # Create default admin user
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, full_name, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin", "admin@sartracker.com", stored_hash, "System Administrator", True))
        
        print("✅ Default user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  Please change this password after first login!")
    else:
        print("ℹ️  Users already exist, skipping default user creation.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at: {os.path.abspath(db_path)}")

def main():
    """Main function to initialize the database."""
    print("🚀 SAR Tracking System - Standalone Database Initialization")
    print("=" * 60)
    
    try:
        create_database()
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend: python run_simple.py")
        print("2. Install frontend dependencies: cd frontend && npm install")
        print("3. Start the frontend: cd frontend && npm start")
        print("4. Login with admin/admin123")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
