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

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

from src.main import app  # noqa: E402
from src.database import Base, engine  # noqa: E402

# Initialize test client
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create fresh SQLite database for tests"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ========== Patient Tests ==========


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
    # Create patient
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

    # Get patient
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["id"] == patient_id


def test_patient_not_found():
    """Test 404 for non-existent patient"""
    response = client.get("/patients/99999")
    assert response.status_code == 404


def test_invalid_email():
    """Test email validation"""
    response = client.post(
        "/patients",
        json={
            "first_name": "Invalid",
            "last_name": "Email",
            "email": "not-an-email",
            "phone": "1111111111",
            "age": 30,
        },
    )
    assert response.status_code == 422


# ========== Doctor Tests ==========


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
    assert data["is_active"] is True


def test_get_doctor():
    """Test retrieving a doctor"""
    # Create doctor
    create_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. Johnson", "specialization": "Neurology"},
    )
    doctor_id = create_resp.json()["id"]

    # Get doctor
    response = client.get(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Dr. Johnson"
    assert data["id"] == doctor_id


def test_update_doctor():
    """Test updating doctor information"""
    # Create doctor
    create_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. Update", "specialization": "Surgery"},
    )
    doctor_id = create_resp.json()["id"]

    # Update doctor
    response = client.put(
        f"/doctors/{doctor_id}",
        json={"specialization": "Advanced Surgery"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["specialization"] == "Advanced Surgery"


def test_doctor_not_found():
    """Test 404 for non-existent doctor"""
    response = client.get("/doctors/99999")
    assert response.status_code == 404


# ========== Appointment Tests ==========


def test_create_appointment():
    """Test creating an appointment with SQLite datetime"""
    # Create patient
    patient_resp = client.post(
        "/patients",
        json={
            "first_name": "Appointment",
            "last_name": "Test",
            "email": "appt@example.com",
            "phone": "5555555555",
            "age": 40,
        },
    )
    patient_id = patient_resp.json()["id"]

    # Create doctor
    doctor_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. Appt", "specialization": "General Practice"},
    )
    doctor_id = doctor_resp.json()["id"]

    # Create appointment (timezone-aware datetime for SQLite)
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
    assert data["duration_minutes"] == 30


def test_appointment_conflict():
    """Test appointment conflict detection with SQLite"""
    # Create patient and doctor
    patient_resp = client.post(
        "/patients",
        json={
            "first_name": "Conflict",
            "last_name": "Test",
            "email": "conflict@example.com",
            "phone": "3333333333",
            "age": 45,
        },
    )
    patient_id = patient_resp.json()["id"]

    doctor_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. Conflict", "specialization": "Surgery"},
    )
    doctor_id = doctor_resp.json()["id"]

    # Create first appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=2)
    client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_datetime": appt_time.isoformat(),
            "duration_minutes": 60,
        },
    )

    # Try to create conflicting appointment
    conflicting_time = appt_time + timedelta(minutes=30)
    response = client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_datetime": conflicting_time.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert response.status_code == 409  # Conflict


def test_list_appointments_by_date():
    """Test listing appointments by date with SQLite"""
    # Create patient and doctor
    patient_resp = client.post(
        "/patients",
        json={
            "first_name": "List",
            "last_name": "Test",
            "email": "list@example.com",
            "phone": "4444444444",
            "age": 50,
        },
    )
    patient_id = patient_resp.json()["id"]

    doctor_resp = client.post(
        "/doctors",
        json={"full_name": "Dr. List", "specialization": "Dermatology"},
    )
    doctor_id = doctor_resp.json()["id"]

    # Create appointment for specific date
    target_date = datetime.now(timezone.utc) + timedelta(days=5)
    target_date = target_date.replace(hour=10, minute=0, second=0, microsecond=0)
    client.post(
        "/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_datetime": target_date.isoformat(),
            "duration_minutes": 45,
        },
    )

    # List appointments for that date
    date_str = target_date.strftime("%Y-%m-%d")
    response = client.get(f"/appointments?date={date_str}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_missing_required_fields():
    """Test validation for missing fields"""
    response = client.post(
        "/doctors",
        json={"full_name": "Dr. Missing"},
        # Missing specialization
    )
    assert response.status_code == 422
