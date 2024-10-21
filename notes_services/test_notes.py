from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base, get_db
from .route import app
import pytest
import responses

# Set up the test database
engine = create_engine("postgresql+psycopg2://postgres:123456@localhost:5432/test")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a TestClient instance
client = TestClient(app)

# Overwrite the get_db dependency
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

@pytest.fixture
def auth_user_mock():
    responses.add(
        responses.GET,
        "http://127.0.0.1:8000/user/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI",
        json = {
            "message" : "Authorization Successful",
            "status" : "success",
            "data" : {
                    "id": 1,
                    "email": "akki@gmail.com",
                    "first_name": "Akki",
                    "last_name": "Narale",
                    "is_verified": True
            }
        },
        status = 200
        )

@pytest.fixture
def get_user_mock():
    responses.add(
        responses.GET,
        "http://127.0.0.1:8000/users?user_ids=2",
        json = {
            "message" : "User found successfully",
            "status" : "success",
            "data" : [
                {
                "id": 2,
                "email": "mahesh@gmail.com",
                "first_name": "Mahesh",
                "last_name": "Lavadne",
                "is_verified": False,
                "created_at": "2024-09-26T12:38:17.482027",
                "updated_at": "2024-09-26T12:38:17.482027"
            }
            ]
        },
        status = 200
        )

# Test case for creating a successful note with mocked external API
@responses.activate
def test_create_note_successful(db_setup, auth_user_mock):
    
    # Payload for creating a note
    data = {
        "title": "Test market",
        "description": "market string",
        "color": "string",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
        }

    # Call the create note API
    response = client.post("/notes/", json=data, headers= {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 201

# Test case for getting all the notes.
@responses.activate
def test_get_all_notes(db_setup, auth_user_mock):

    # Payload for creating a note
    data1 = {
        "title": "Notes test cases 2",
        "description": "market string",
        "color": "string",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
        }
    
    # Payload for another note creation
    data2 = {
        "title": "Note test cases 3",
        "description": "market string",
        "color": "string",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
        }
  
    # Call the create note API twice for two data set
    response = client.post("/notes/", json=data1, headers= {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})

    response = client.post("/notes/", json=data2, headers= {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Mocked response for external user verification
    response = client.get("/notes/", headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 200

# Test case for fetching notes by note id
@responses.activate
def test_get_single_note(db_setup, auth_user_mock):
    # Create a note first
    data = {
        "title": "Test Note",
        "description": "Single note",
        "color": "blue",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call the create note API
    response = client.post("/notes/", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Extracting the note id from data
    note_id = response.json()["data"]["id"]

    # Fetch the created note with note id as path params
    response = client.get(f"/notes/{note_id}", headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 405

# Test case for creating note with invalid values
@responses.activate
def test_note_invalid_field(db_setup, auth_user_mock):
    # Creating the note with invalid data type and validation
    data = {
        "title": 16400,
        "description": "Single note",
        "color": "blue",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }
    
    # Call the creatne note API
    response = client.post("/notes/", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 422

# Test case for updating the existing note.
@responses.activate
def test_update_note_success(db_setup, auth_user_mock):
    # Create a note first
    data = {
        "title": "Test Note",
        "description": "Update this note",
        "color": "yellow",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call the create note API
    create_response = client.post("/notes/", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Extracting the note id from data
    note_id = create_response.json()["data"]["id"]

    # Update the note
    update_data = {
        "title": "Testing notes all world",
        "description": "Update this note",
        "color": "Green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call the update note API with note id as path parameter
    response = client.put(f"/notes/{note_id}", json=update_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 200

# Test case for updating non existing note (error == 400)
@responses.activate
def test_note_invalid_note(db_setup, auth_user_mock):

    update_data = {
        "title": "Testing notes all world",
        "description": "Update this note",
        "color": "Green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call out the update note API with non existing note id
    response = client.put(f"/notes/160", json=update_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 400

# Test case for deleting the note
@responses.activate
def test_note_delete_note(db_setup,auth_user_mock):

    data = {
        "title": "Testing notes all world",
        "description": "Update this note",
        "color": "Green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call out the create note API
    create_response = client.post("/notes/", json = data, headers={"Authorization" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Extracting the note id from data
    note_id = create_response.json()["data"]["id"]
    # Assert the response status code and content
    assert create_response.status_code == 201

    # Call out the delete note API with note id as path params
    response = client.delete(f"/notes/{note_id}", headers={"Authorization" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 200

# Test case for deleting non exisiting note
@responses.activate
def test_delete_non_exising_note(db_setup, auth_user_mock):
    # Creating the note first
    data = {
        "title": "Testing notes all world",
        "description": "Update this note",
        "color": "Green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T12:50:00"
    }

    # Call out the the create note API
    create_response = client.post("/notes/", json = data, headers={"Authorization" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Fetching the note id from data
    note_id = create_response.json()["data"]["id"]
    # Assert the response status code and content
    assert create_response.status_code == 201

    # Call the delete API with the invalid note id 
    response = client.delete(f"/notes/16400", headers={"Authorization" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    # Assert the response status code and content
    assert response.status_code == 400

# Test case for adding collaborator successfully
@responses.activate
def test_add_collaborators(db_setup, auth_user_mock, get_user_mock):
    initial_note = {
        "title": "Initial Note",
        "description": "Initial Description",
        "color": "yellow",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-16T21:15:38.710831"
    }
    
    # Insert the note via the API
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    
    note_id = create_response.json()["data"]["id"]
    print(f"Create Note Response: {create_response.json()}")

    # Payload for adding collaborators
    data = {
        "note_id": note_id,  
        "user_ids": [2],  
        "access": "readonly"
    }

    # Call the add collaborators API
    response = client.patch("/notes/add-collaborators", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    print(f"Response content: {response.text}")
    # print(f"Add Collaborators Response:{response.json()}")
    # Assert the response status code and content
    assert response.status_code == 200

# Test case for adding user itself as collaborator
@responses.activate
def test_add_self_as_collaborator(db_setup, auth_user_mock, get_user_mock):
    initial_note = {
        "title": "Initial Note",
        "description": "Initial Description",
        "color": "yellow",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-16T21:15:38.710831"
    }
    
    # Insert the note via the API
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    
    note_id = create_response.json()["data"]["id"]
    
    # Payload where user tries to add themselves as a collaborator
    data = {
        "note_id": note_id,  
        "user_ids": [1], 
        "access": "readonly"
    }

    # Call the add collaborators API
    response = client.patch("/notes/add-collaborators", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})

    # Assert the response status code and error message
    assert response.status_code == 400

# Test case for invalid user IDs (some users not found)
@responses.activate
def test_add_collaborators_invalid_users(db_setup, auth_user_mock, get_user_mock):
    
    initial_note = {
        "title": "Initial Note",
        "description": "Initial Description",
        "color": "yellow",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-16T21:15:38.710831"
    }
    
    # Insert the note via the API
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    
    note_id = create_response.json()["data"]["id"]
    
    # Payload for adding invalid user IDs as collaborators
    data = {
        "note_id": note_id,  
        "user_ids": [999, 1000],  # Non-existent user IDs
        "access": "readonly"
    }

    # Call the add collaborators API
    response = client.patch("/notes/add-collaborators", json=data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})

    # Assert the response status code and error message
    assert response.status_code == 400

# Test case for Successfully Remove Collaborators
@responses.activate
def test_remove_collaborators_success(db_setup, auth_user_mock, get_user_mock):
    # Initial note with collaborators
    initial_note = {
        "title": "Test Note",
        "description": "This is a test note.",
        "color": "blue",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T21:00:00"
    }

    # Create a note
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    note_id = create_response.json()["data"]["id"]

    # Add collaborators first
    add_collaborators_data = {
        "note_id": note_id,
        "user_ids": [2],
        "access": "readonly"
    }
    response = client.patch("/notes/add-collaborators", json=add_collaborators_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    print(f"Add Collaborators Response: {response.text}")

    # Remove collaborators from note
    remove_data = {
        "note_id": note_id,
        "user_ids": [2]
    }
    response = client.patch("/notes/remove-collaborators", json=remove_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})

    print(f"Remove Collaborators Response: {response.text}")
    # Assert success
    assert response.status_code == 200

# Test Case to Remove Collaborators When They Don’t Exist
@responses.activate
def test_remove_collaborators_not_found(db_setup, auth_user_mock, get_user_mock):
    # Initial note
    initial_note = {
        "title": "Test Note",
        "description": "This is a test note.",
        "color": "green",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T21:00:00"
    }

    # Create a note
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    note_id = create_response.json()["data"]["id"]

    # Remove non-existent collaborators from note
    remove_data = {
        "note_id": note_id,
        "user_ids": [999]  # User ID 999 doesn't exist
    }
    
    response = client.patch("/notes/remove-collaborators", json=remove_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    
    # Assert failure
    assert response.status_code == 400

#Test Case to Remove Collaborators With No Collaborators in Note
@responses.activate
def test_remove_collaborators_no_collaborators(db_setup, auth_user_mock):
    # Initial note without collaborators
    initial_note = {
        "title": "Test Note",
        "description": "This is a test note.",
        "color": "red",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-10-18T21:00:00"
    }

    # Create a note
    create_response = client.post("/notes/", json=initial_note, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    assert create_response.status_code == 201
    note_id = create_response.json()["data"]["id"]

    # Attempt to remove collaborators from a note without any collaborators
    remove_data = {
        "note_id": note_id,
        "user_ids": [2]
    }
    
    response = client.patch("/notes/remove-collaborators", json=remove_data, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2tpQGdtYWlsLmNvbSIsInVzZXJfaWQiOjk3LCJleHAiOjE3Mjk0NDY3NjJ9.y2qvjJd0METH-aXv-lh2CdSdEsBsGKP1Xk7zaNC_WnI"})
    
    # Assert failure
    assert response.status_code == 400