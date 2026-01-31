"""
Integration tests for Doctor API endpoints
Requires server to be running: uvicorn src.main:app --reload
Run with: pytest tests/test_doctor.py -v -s
"""

import requests
import pytest
from requests.exceptions import ConnectionError, Timeout

BASE_URL = "http://127.0.0.1:8000"
DOCTORS_ENDPOINT = f"{BASE_URL}/doctors"


def test_server_is_reachable():
    """
    Explicitly checks whether the server is ON or NOT reachable.
    """
    try:
        response = requests.get(DOCTORS_ENDPOINT, timeout=3)
        assert response.status_code in [
            200,
            404,
            405,
        ], "Server responded but is unhealthy"
        print("✔ The server is ON and reachable")
    except (ConnectionError, Timeout):
        pytest.fail(
            "✘ The server is NOT reachable - "
            "Start server with: uvicorn src.main:app --reload"
        )


@pytest.fixture(scope="module")
def doctor_id():
    """Create test doctor and return ID"""
    payload = {"full_name": "Dr. John Smith", "specialization": "Cardiology"}

    response = requests.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to add doctor: {response.text}"
    doctor_data = response.json()
    return doctor_data["id"]


def test_create_doctor():
    """Test creating a new doctor"""
    payload = {"full_name": "Dr. Jane Wilson", "specialization": "Neurology"}

    response = requests.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to create doctor: {response.text}"
    data = response.json()

    assert data["full_name"] == "Dr. Jane Wilson"
    assert data["specialization"] == "Neurology"
    assert data["is_active"] is True
    assert "id" in data


def test_create_doctor_inactive():
    """Test creating an inactive doctor"""
    payload = {
        "full_name": "Dr. Retired Doctor",
        "specialization": "General Practice",
        "is_active": False,
    }

    response = requests.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is False


def test_get_doctor(doctor_id):
    """Test retrieving a doctor by ID"""
    response = requests.get(f"{DOCTORS_ENDPOINT}/{doctor_id}")

    assert response.status_code == 200, f"Doctor not found: {response.text}"
    data = response.json()

    assert "full_name" in data
    assert "specialization" in data
    assert "is_active" in data
    assert data["id"] == doctor_id


def test_get_doctor_not_found():
    """Test 404 for non-existent doctor"""
    response = requests.get(f"{DOCTORS_ENDPOINT}/99999")
    assert response.status_code == 404


def test_update_doctor(doctor_id):
    """Test updating a doctor's information"""
    payload = {"specialization": "Advanced Cardiology"}

    response = requests.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["specialization"] == "Advanced Cardiology"


def test_update_doctor_deactivate(doctor_id):
    """Test deactivating a doctor"""
    # First activate
    requests.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": True})

    # Then deactivate
    response = requests.put(
        f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    requests.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": True})


def test_update_doctor_not_found():
    """Test 404 when updating non-existent doctor"""
    payload = {"specialization": "Surgery"}
    response = requests.put(f"{DOCTORS_ENDPOINT}/99999", json=payload)
    assert response.status_code == 404


def test_create_doctor_missing_fields():
    """Test validation for missing required fields"""
    payload = {
        "full_name": "Dr. Missing Fields"
        # Missing specialization
    }

    response = requests.post(DOCTORS_ENDPOINT, json=payload)
    assert response.status_code == 422
