#!/usr/bin/env python3
"""
Script to initialize the Railway database with admin user and sample data.
This should be run after the Railway deployment is complete.
"""

import requests
import json
from datetime import datetime, timedelta

# Railway backend URL
RAILWAY_URL = "https://web-production-055e.up.railway.app"

def create_admin_user():
    """Create the admin user in the Railway database."""
    admin_data = {
        "username": "admin",
        "email": "admin@sar-system.com",
        "full_name": "System Administrator",
        "password": "admin123",
        "is_admin": True
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/auth/register", json=admin_data)
        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            return True
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("ℹ️  Admin user already exists")
            return True
        else:
            print(f"❌ Failed to create admin user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def test_login():
    """Test the admin login."""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{RAILWAY_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   Access token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   User: {data.get('user', {}).get('username', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def create_sample_case():
    """Create a sample SAR case for testing."""
    # First login to get token
    login_data = {"username": "admin", "password": "admin123"}
    try:
        login_response = requests.post(f"{RAILWAY_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print("❌ Cannot create sample case - login failed")
            return False
        
        token = login_response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create sample case
        case_data = {
            "case_reference": "SAR-2024-001",
            "organization_name": "Tech Corp Ltd",
            "organization_address": "123 Tech Street, London, UK",
            "organization_email": "dpo@techcorp.com",
            "organization_phone": "+44 20 1234 5678",
            "data_administrator_name": "John Smith",
            "data_controller_name": "Jane Doe",
            "request_type": "SAR",
            "request_description": "Request for all personal data held by Tech Corp Ltd",
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "submission_method": "Email",
            "statutory_deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "Pending",
            "response_received": False,
            "data_provided": False,
            "data_complete": False
        }
        
        response = requests.post(f"{RAILWAY_URL}/sar/", json=case_data, headers=headers)
        if response.status_code == 200:
            print("✅ Sample case created successfully!")
            return True
        else:
            print(f"❌ Failed to create sample case: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating sample case: {e}")
        return False

def main():
    """Main function to initialize the Railway database."""
    print("🚀 Initializing Railway Database...")
    print("=" * 50)
    
    # Test backend connection
    try:
        health_response = requests.get(f"{RAILWAY_URL}/health")
        if health_response.status_code == 200:
            print("✅ Backend is healthy and responding")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print()
    
    # Create admin user
    if create_admin_user():
        print()
        
        # Test login
        if test_login():
            print()
            
            # Create sample case
            create_sample_case()
        else:
            print("❌ Cannot proceed - login test failed")
    else:
        print("❌ Cannot proceed - admin user creation failed")
    
    print()
    print("=" * 50)
    print("🎯 Railway database initialization complete!")
    print(f"🌐 Your SAR system is now live at: https://jannerap.github.io/SAR")
    print(f"🔗 Backend API: {RAILWAY_URL}")

if __name__ == "__main__":
    main()
