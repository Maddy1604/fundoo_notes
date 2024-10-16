from .route import app
from fastapi.testclient import TestClient
from .models import get_db, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pytest 

engine = create_engine("postgresql+psycopg2://postgres:123456@localhost:5432/test")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def over_write_get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

@pytest.fixture
def db_setup():
    Base.metadata.create_all(bind = engine)
    yield 
    Base.metadata.drop_all(bind = engine)

app.dependency_overrides[get_db] = over_write_get_db

# 1. Testing for successfull registration
def test_user_registration_successfull(db_setup):
    data = {
    "email": "akki@gmail.com",
    "password": "akki@gmail.com",
    "first_name": "Akki",
    "last_name": "Narale"
    }
    response = client.post("/register", json = data)
    assert response.status_code == 201

# 2. Testing for invalid email 
def test_user_registration_invalid_email(db_setup):
    data = {
        "email": "akkigmail.com",  # Invalid email format
        "password": "akki@gmail.com",
        "first_name": "Akki",
        "last_name": "Narale"
    }
    response = client.post("/register", json=data)
    assert response.status_code == 422

# 3. Testing for invalid details
def test_user_registration_invalid_password(db_setup):
    data = {
        "email": "akki@gmail.com", 
        "password": "akkigmail.com", #Invalid password
        "first_name": "Akash",
        "last_name": "Narale"
    }
    response = client.post("/register", json=data)
    assert response.status_code == 201

# 4. Testing for missing details
def test_user_registration_missing_fields(db_setup):
    data = {
        "email": "akki@gmail.com",
        "password": "akki@gmail.com",
        "last_name": "Narale"
    }
    response = client.post("/register", json=data)
    assert response.status_code == 422    

# Problem
# def test_user_login_invalid_password(db_setup):
#     data = {
#         "email": "akki@gmail.com",
#         "password": "wrongpassword"
#     }
#     response = client.post("/login", json=data)
#     assert response.status_code == 401

# 5. Register and Login user
def test_user_login_success(db_setup):
    # Register the user
    registration_data = {
        "email": "akki2@gmail.com",
        "password": "akki2@gmail.com",
        "first_name": "Akki",
        "last_name": "Narale"
    }
    register_response = client.post("/register", json=registration_data)
    assert register_response.status_code == 201

    # login with the plain password
    login_data = {
        "email": "akki2@gmail.com",
        "password": "akki2@gmail.com"
    }
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == 201

# 6. Register user and login with wrong password
def test_user_login_wrong_pass(db_setup):
    # Register the user
    registration_data = {
        "email": "akki3@gmail.com",
        "password": "akki3@gmail.com",
        "first_name": "Akki",
        "last_name": "Narale"
    }
    register_response = client.post("/register", json=registration_data)
    assert register_response.status_code == 201

    # login with the wrong password
    login_data = {
        "email": "akki2@gmail.com",
        "password": "Unwanted@text"
    }
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == 400

# 7. Register user and login with email password
def test_user_login_wrong_email(db_setup):
    # Register the user
    registration_data = {
        "email": "akki4@gmail.com",
        "password": "akki4@gmail.com",
        "first_name": "Akki",
        "last_name": "Narale"
    }
    register_response = client.post("/register", json=registration_data)
    assert register_response.status_code == 201

    # login with the wrong password
    login_data = {
        "email": "akki2@gmail.com",
        "password": "akki4@gmail.com"
    }
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == 400

# Verifiying user email by sending token as query parameter to endpoint
def test_user_fetch_user(db_setup):
    # Register the user
    registration_data = {
        "email": "akki5@gmail.com",
        "password": "akki5@gmail.com",
        "first_name": "Akki",
        "last_name": "Narale"
    }
    register_response = client.post("/register", json=registration_data)
    assert register_response.status_code == 201

    # login with the plain password
    login_data = {
        "email": "akki5@gmail.com",
        "password": "akki5@gmail.com"
    }
    login_response = client.post("/login", json=login_data)
    token = login_response.json()["access_token"]
    
    # # Fetch profile with the token
    response = client.get(f"/user/{token}")
    assert response.status_code == 200

# Getting user by their user_ids as query parameter
def test_get_users(db_setup):
    # Register two users
    user_1 = {
        "email": "user1@example.com",
        "password": "password@1",
        "first_name": "First",
        "last_name": "User"
    }
    user_2 = {
        "email": "user2@example.com",
        "password": "password@2",
        "first_name": "Second",
        "last_name": "User"
    }
    response_1 = client.post("/register", json=user_1)
    response_2 = client.post("/register", json=user_2)

    # Extract user IDs from the registration responses
    user_id_1 = response_1.json()["data"]["id"]
    user_id_2 = response_2.json()["data"]["id"]

   
    # Make the GET request with user IDs in the query string
    response = client.get(f"/users?user_ids={user_id_1}&user_ids={user_id_2}")
    
    # Ensure response status code is 200
    assert response.status_code == 200
    
    # Parse response data
    response_data = response.json()["data"]

    # Check if 2 users are returned
    assert len(response_data) == 2
