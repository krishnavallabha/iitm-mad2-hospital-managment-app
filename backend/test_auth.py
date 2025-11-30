"""
Simple test script to verify authentication endpoints
Run this after starting the Flask server to test authentication
"""
import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

def test_register():
    """Test patient registration"""
    print("\n" + "="*50)
    print("Testing Patient Registration")
    print("="*50)
    
    data = {
        "username": "testpatient",
        "email": "testpatient@example.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "Patient",
        "phone": "1234567890",
        "gender": "Male"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json() if response.status_code in [200, 201] else None

def test_login(username, password):
    """Test login"""
    print("\n" + "="*50)
    print(f"Testing Login for: {username}")
    print("="*50)
    
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("\n" + "="*50)
    print("Testing Get Current User")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Hospital Management System - Authentication Test")
    print("="*60)
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("Run: python app.py")
    
    # Test patient registration
    register_result = test_register()
    
    # Test patient login
    patient_token = test_login("testpatient", "test123")
    
    if patient_token:
        test_get_current_user(patient_token)
    
    # Test admin login
    print("\n" + "="*50)
    print("Testing Admin Login")
    print("="*50)
    admin_token = test_login("admin", "admin123")
    
    if admin_token:
        test_get_current_user(admin_token)
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

