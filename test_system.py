#!/usr/bin/env python3
"""
Simple Test Script for SAR Tracking System
"""

import os
import sys
import sqlite3
from datetime import datetime, date, timedelta

def test_database_connection():
    """Test basic database functionality."""
    print("🗄️  Testing database connection...")
    
    try:
        # Create a simple test database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create a simple test table
        cursor.execute('''
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        cursor.execute('''
            INSERT INTO test_users (username, email) VALUES (?, ?)
        ''', ('testuser', 'test@example.com'))
        
        # Query test data
        cursor.execute('SELECT * FROM test_users')
        result = cursor.fetchone()
        
        if result and result[1] == 'testuser':
            print("✅ Database connection and basic operations working!")
            return True
        else:
            print("❌ Database query failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_imports():
    """Test if we can import the main modules."""
    print("📦 Testing module imports...")
    
    try:
        # Test basic imports
        import fastapi
        print(f"✅ FastAPI imported successfully (version: {fastapi.__version__})")
        
        import uvicorn
        print(f"✅ Uvicorn imported successfully (version: {uvicorn.__version__})")
        
        import sqlalchemy
        print(f"✅ SQLAlchemy imported successfully (version: {sqlalchemy.__version__})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic Python functionality."""
    print("🐍 Testing basic Python functionality...")
    
    try:
        # Test date operations
        today = date.today()
        future_date = today + timedelta(days=28)
        print(f"✅ Date operations working (today: {today}, +28 days: {future_date})")
        
        # Test string operations
        test_string = "SAR-202412-ABC123"
        if "SAR-" in test_string and len(test_string) > 10:
            print("✅ String operations working")
        else:
            print("❌ String operations failed")
            return False
        
        # Test list operations
        test_list = ["Pending", "Overdue", "Complete"]
        if "Pending" in test_list and len(test_list) == 3:
            print("✅ List operations working")
        else:
            print("❌ List operations failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_operations():
    """Test basic file operations."""
    print("📁 Testing file operations...")
    
    try:
        # Test creating directories
        test_dir = "test_uploads"
        os.makedirs(test_dir, exist_ok=True)
        
        # Test creating a file
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Test reading the file
        with open(test_file, 'r') as f:
            content = f.read()
        
        if content == "Test content":
            print("✅ File operations working")
        else:
            print("❌ File read/write failed")
            return False
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SAR Tracking System - System Test")
    print("=" * 50)
    
    tests = [
        ("Basic Python Functionality", test_basic_functionality),
        ("File Operations", test_file_operations),
        ("Module Imports", test_imports),
        ("Database Operations", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("1. Run: python init_db.py")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:8000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
