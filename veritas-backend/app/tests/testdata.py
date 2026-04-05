import requests
import json

BASE_URL = "http://localhost:8000"

# Test user creation
def test_user_flow():
    # Signup
    signup_data = {
        "name": "Test Author",
        "email": "author@test.com",
        "password": "password123",
        "role": "author"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print("Signup:", response.status_code, response.json())
    
    # Login
    login_data = {
        "email": "author@test.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    token_data = response.json()
    print("Login:", response.status_code)
    
    return token_data["access_token"]

if __name__ == "__main__":
    token = test_user_flow()
    print(f"Auth token: {token}")