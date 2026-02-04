"""
Integration tests for Patient API endpoints using TestClient
Run with: pytest tests/test_patient.py -v -s
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import Base, engine

PATIENTS_ENDPOINT = "/patients"


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create tables before tests and clean up after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Create TestClient instance"""
    return TestClient(app)


@pytest.fixture(scope="module")
def patient_id(client):
    """Create test patient and return ID"""
    import time

    timestamp = int(time.time() * 1000)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.{timestamp}@example.com",  # Unique email per run
        "phone": "1234567890",
        "age": 45,
    }

    response = client.post(PATIENTS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to add patient: {response.text}"
    patient_data = response.json()
    return patient_data["id"]


def test_create_patient(client):
    """Test creating a new patient"""
    import time

    timestamp = int(time.time() * 1000)
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": f"jane.smith.{timestamp}@example.com",
        "phone": "9876543210",
        "age": 32,
    }

    response = client.post(PATIENTS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to create patient: {response.text}"
    data = response.json()

    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == f"jane.smith.{timestamp}@example.com"
    assert data["age"] == 32
    assert "id" in data


def test_create_patient_duplicate_email(client):
    """Test that duplicate email is rejected"""
    import time

    timestamp = int(time.time() * 1000)
    payload = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": f"duplicate.{timestamp}@example.com",
        "phone": "1111111111",
        "age": 25,
    }

    # Create first patient
    response1 = client.post(PATIENTS_ENDPOINT, json=payload)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post(PATIENTS_ENDPOINT, json=payload)
    assert response2.status_code == 400
    assert "email" in response2.text.lower() or "exists" in response2.text.lower()


def test_get_patient(client, patient_id):
    """Test retrieving a patient by ID"""
    response = client.get(f"{PATIENTS_ENDPOINT}/{patient_id}")

    assert response.status_code == 200, f"Patient not found: {response.text}"
    data = response.json()

    assert "first_name" in data
    assert "last_name" in data
    assert "email" in data
    assert "age" in data
    assert data["id"] == patient_id


def test_get_patient_not_found(client):
    """Test 404 for non-existent patient"""
    response = client.get(f"{PATIENTS_ENDPOINT}/99999")
    assert response.status_code == 404


def test_create_patient_invalid_email(client):
    """Test validation for invalid email"""
    payload = {
        "first_name": "Invalid",
        "last_name": "Email",
        "email": "not-an-email",
        "phone": "2222222222",
        "age": 30,
    }

    response = client.post(PATIENTS_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_create_patient_missing_fields(client):
    """Test validation for missing required fields"""
    payload = {
        "first_name": "Missing",
        "last_name": "Fields",
        # Missing email, phone, age
    }

    response = client.post(PATIENTS_ENDPOINT, json=payload)
    assert response.status_code == 422
