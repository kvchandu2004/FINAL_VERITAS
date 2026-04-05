# integration_test.py
import requests
import time

def full_workflow_test():
    base_url = "http://localhost:8000"
    
    print("1. Testing signup...")
    signup_response = requests.post(f"{base_url}/auth/signup", json={
        "name": "Integration Test User",
        "email": "integration@test.com",
        "password": "test123",
        "role": "author"
    })
    print(f"Signup status: {signup_response.status_code}")
    
    print("2. Testing login...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "integration@test.com",
        "password": "test123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login status: {login_response.status_code}")
    
    print("3. Testing file upload...")
    # You would need a test PDF file
    # with open("test.pdf", "rb") as f:
    #     files = {"file": f}
    #     data = {"title": "Test Paper", "abstract": "Test abstract"}
    #     upload_response = requests.post(f"{base_url}/manuscripts/upload", 
    #                                   files=files, data=data, headers=headers)
    #     print(f"Upload status: {upload_response.status_code}")
    
    print("4. Testing manuscript list...")
    manuscripts_response = requests.get(f"{base_url}/manuscripts/", headers=headers)
    print(f"Manuscripts status: {manuscripts_response.status_code}")
    
    print("Integration test completed!")

if __name__ == "__main__":
    full_workflow_test()