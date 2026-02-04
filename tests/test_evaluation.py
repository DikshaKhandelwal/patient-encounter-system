"""
Test Suite for Patient Encounter System
Uses SQLite database (test.db) for all tests
Run with: pytest tests/test_evaluation.py -v
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

from src.main import app  # noqa: E402
from src.database import Base, engine  # noqa: E402

# Ensure a clean DB for these API tests
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_patient():
    """Test creating a patient"""
    response = client.post(
        "/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "age": 35,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data


def test_get_patient():
    """Test retrieving a patient"""
    create_resp = client.post(
        "/patients",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "9876543210",
            "age": 28,
        },
    )
    patient_id = create_resp.json()["id"]

    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["id"] == patient_id


def test_create_doctor():
    """Test creating a doctor"""
    response = client.post(
        "/doctors",
        json={"full_name": "Dr. Smith", "specialization": "Cardiology"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Dr. Smith"
    assert data["specialization"] == "Cardiology"


def test_create_appointment():
    """Test creating an appointment"""
    patient_resp = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Wonder",
            "email": "alice@example.com",
            "phone": "5555555555",
            "age": 40,
        },
    )
    patient_id = patient_resp.json()["id"]

    doctor_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. Brown", "specialization": "General Practice"},
    )
    doctor_id = doctor_resp.json()["id"]

    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_datetime": appt_time.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == patient_id
    assert data["doctor_id"] == doctor_id


def test_patient_not_found():
    """Test 404 for non-existent patient"""
    response = client.get("/patients/99999")
    assert response.status_code == 404
