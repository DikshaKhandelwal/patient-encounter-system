"""
Minimal test suite for external evaluation
Run with: pytest test_evaluation.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

from src.main import app
from src.database import Base, engine

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ========== Basic Structure Tests ==========


def test_app_exists():
    """Test that FastAPI app exists"""
    assert app is not None
    assert app.title == "Patient Encounter System"


# ========== Patient Tests ==========


def test_create_patient():
    """Test creating a patient"""
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.eval@example.com",
        "phone": "1234567890",
        "age": 35,
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert "id" in data


def test_get_patient():
    """Test getting patient by ID"""
    # Create patient first
    payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.eval@example.com",
        "phone": "9876543210",
        "age": 28,
    }
    create_response = client.post("/patients", json=payload)
    patient_id = create_response.json()["id"]

    # Get patient
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"


# ========== Doctor Tests ==========


def test_create_doctor():
    """Test creating a doctor"""
    payload = {"full_name": "Dr. Smith", "specialization": "Cardiology"}
    response = client.post("/doctors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Dr. Smith"
    assert data["is_active"] is True


def test_get_doctor():
    """Test getting doctor by ID"""
    # Create doctor first
    payload = {"full_name": "Dr. Johnson", "specialization": "Neurology"}
    create_response = client.post("/doctors", json=payload)
    doctor_id = create_response.json()["id"]

    # Get doctor
    response = client.get(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Dr. Johnson"


# ========== Appointment Tests ==========


def test_create_appointment():
    """Test creating an appointment"""
    # Create patient
    patient_payload = {
        "first_name": "Test",
        "last_name": "Patient",
        "email": "test.appt@example.com",
        "phone": "5555555555",
        "age": 40,
    }
    patient_response = client.post("/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    # Create doctor
    doctor_payload = {"full_name": "Dr. Test", "specialization": "General Practice"}
    doctor_response = client.post("/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Create appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 30,
    }
    response = client.post("/appointments", json=appointment_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == patient_id
    assert data["doctor_id"] == doctor_id


def test_appointment_conflict():
    """Test appointment conflict detection"""
    # Create patient and doctor
    patient_payload = {
        "first_name": "Conflict",
        "last_name": "Test",
        "email": "conflict.test@example.com",
        "phone": "3333333333",
        "age": 45,
    }
    patient_response = client.post("/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    doctor_payload = {"full_name": "Dr. Conflict", "specialization": "Surgery"}
    doctor_response = client.post("/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Create first appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=2)
    appointment1 = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 60,
    }
    client.post("/appointments", json=appointment1)

    # Try conflicting appointment
    conflicting_time = appt_time + timedelta(minutes=30)
    appointment2 = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": conflicting_time.isoformat(),
        "duration_minutes": 30,
    }
    response = client.post("/appointments", json=appointment2)
    assert response.status_code == 409  # Conflict


# ========== Validation Tests ==========


def test_invalid_email():
    """Test email validation"""
    payload = {
        "first_name": "Invalid",
        "last_name": "Email",
        "email": "not-an-email",
        "phone": "1111111111",
        "age": 30,
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 422


def test_missing_required_fields():
    """Test missing required fields"""
    payload = {
        "full_name": "Dr. Missing"
        # Missing specialization
    }
    response = client.post("/doctors", json=payload)
    assert response.status_code == 422
