"""
Integration tests for Doctor API endpoints using TestClient
Run with: pytest tests/test_doctor.py -v -s
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import Base, engine

DOCTORS_ENDPOINT = "/doctors"


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
def doctor_id(client):
    """Create test doctor and return ID"""
    payload = {"full_name": "Dr. John Smith", "specialization": "Cardiology"}

    response = client.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to add doctor: {response.text}"
    doctor_data = response.json()
    return doctor_data["id"]


def test_create_doctor(client):
    """Test creating a new doctor"""
    payload = {"full_name": "Dr. Jane Wilson", "specialization": "Neurology"}

    response = client.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to create doctor: {response.text}"
    data = response.json()

    assert data["full_name"] == "Dr. Jane Wilson"
    assert data["specialization"] == "Neurology"
    assert data["is_active"] is True
    assert "id" in data


def test_create_doctor_inactive(client):
    """Test creating an inactive doctor"""
    payload = {
        "full_name": "Dr. Retired Doctor",
        "specialization": "General Practice",
        "is_active": False,
    }

    response = client.post(DOCTORS_ENDPOINT, json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is False


def test_get_doctor(client, doctor_id):
    """Test retrieving a doctor by ID"""
    response = client.get(f"{DOCTORS_ENDPOINT}/{doctor_id}")

    assert response.status_code == 200, f"Doctor not found: {response.text}"
    data = response.json()

    assert "full_name" in data
    assert "specialization" in data
    assert "is_active" in data
    assert data["id"] == doctor_id


def test_get_doctor_not_found(client):
    """Test 404 for non-existent doctor"""
    response = client.get(f"{DOCTORS_ENDPOINT}/99999")
    assert response.status_code == 404


def test_update_doctor(client, doctor_id):
    """Test updating a doctor's information"""
    payload = {"specialization": "Advanced Cardiology"}

    response = client.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["specialization"] == "Advanced Cardiology"


def test_update_doctor_deactivate(client, doctor_id):
    """Test deactivating a doctor"""
    # First activate
    client.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": True})

    # Then deactivate
    response = client.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": False})

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    client.put(f"{DOCTORS_ENDPOINT}/{doctor_id}", json={"is_active": True})


def test_update_doctor_not_found(client):
    """Test 404 when updating non-existent doctor"""
    payload = {"specialization": "Surgery"}
    response = client.put(f"{DOCTORS_ENDPOINT}/99999", json=payload)
    assert response.status_code == 404


def test_create_doctor_missing_fields(client):
    """Test validation for missing required fields"""
    payload = {
        "full_name": "Dr. Missing Fields"
        # Missing specialization
    }

    response = client.post(DOCTORS_ENDPOINT, json=payload)
    assert response.status_code == 422
