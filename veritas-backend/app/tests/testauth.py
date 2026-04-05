import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup():
    response = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "author"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"

def test_login():
    # First signup
    client.post("/auth/signup", json={
        "name": "Test User 2",
        "email": "test2@example.com",
        "password": "password123",
        "role": "author"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "email": "test2@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"