#!/usr/bin/env python3
"""
Database Migration Script
Adds new columns to existing SAR database
"""

import sqlite3
import os

def migrate_database():
    """Migrate the existing database to add new columns."""
    
    db_path = "sar_tracking.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run init_db_standalone.py first.")
        return False
    
    print("🔧 Starting database migration...")
    
    try:
        # Connect to existing database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(sar_cases)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Existing columns: {columns}")
        
        # Add missing columns if they don't exist
        if 'data_administrator_name' not in columns:
            print("➕ Adding data_administrator_name column...")
            cursor.execute("ALTER TABLE sar_cases ADD COLUMN data_administrator_name TEXT")
        
        if 'data_controller_name' not in columns:
            print("➕ Adding data_controller_name column...")
            cursor.execute("ALTER TABLE sar_cases ADD COLUMN data_controller_name TEXT")
        
        # Commit changes
        conn.commit()
        
        # Verify the new columns exist
        cursor.execute("PRAGMA table_info(sar_cases)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"✅ Updated columns: {new_columns}")
        
        # Check if there are any existing cases
        cursor.execute("SELECT COUNT(*) FROM sar_cases")
        case_count = cursor.fetchone()[0]
        print(f"📊 Found {case_count} existing cases")
        
        conn.close()
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_database()
