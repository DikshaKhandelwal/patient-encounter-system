"""
Integration tests for Patient API endpoints
Requires server to be running: uvicorn src.main:app --reload
Run with: pytest tests/test_patient.py -v -s
"""

import requests
import pytest
from requests.exceptions import ConnectionError, Timeout

BASE_URL = "http://127.0.0.1:8000"
PATIENTS_ENDPOINT = f"{BASE_URL}/patients"


def test_server_is_reachable():
    """Check if server is reachable"""
    try:
        response = requests.get(PATIENTS_ENDPOINT, timeout=3)
        assert response.status_code in [200, 404]
    except (ConnectionError, Timeout):
        pytest.fail(
            "Server is not reachable. Start with: uvicorn src.main:app --reload"
        )


@pytest.fixture(scope="module")
def patient_id():
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

    response = requests.post(PATIENTS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to add patient: {response.text}"
    patient_data = response.json()
    return patient_data["id"]


def test_create_patient():
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

    response = requests.post(PATIENTS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to create patient: {response.text}"
    data = response.json()

    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith.test@example.com"
    assert data["age"] == 32
    assert "id" in data


def test_create_patient_duplicate_email():
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
    response1 = requests.post(PATIENTS_ENDPOINT, json=payload)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = requests.post(PATIENTS_ENDPOINT, json=payload)
    assert response2.status_code == 400
    assert "email" in response2.text.lower() or "exists" in response2.text.lower()


def test_get_patient(patient_id):
    """Test retrieving a patient by ID"""
    response = requests.get(f"{PATIENTS_ENDPOINT}/{patient_id}")

    assert response.status_code == 200, f"Patient not found: {response.text}"
    data = response.json()

    assert "first_name" in data
    assert "last_name" in data
    assert "email" in data
    assert "age" in data
    assert data["id"] == patient_id


def test_get_patient_not_found():
    """Test 404 for non-existent patient"""
    response = requests.get(f"{PATIENTS_ENDPOINT}/99999")
    assert response.status_code == 404


def test_create_patient_invalid_email():
    """Test validation for invalid email"""
    payload = {
        "first_name": "Invalid",
        "last_name": "Email",
        "email": "not-an-email",
        "phone": "2222222222",
        "age": 30,
    }

    response = requests.post(PATIENTS_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_create_patient_missing_fields():
    """Test validation for missing required fields"""
    payload = {
        "first_name": "Missing",
        "last_name": "Fields",
        # Missing email, phone, age
    }

    response = requests.post(PATIENTS_ENDPOINT, json=payload)
    assert response.status_code == 422
