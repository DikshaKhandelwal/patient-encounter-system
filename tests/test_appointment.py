"""
Integration tests for Appointment API endpoints
Requires server to be running: uvicorn src.main:app --reload
Run with: pytest tests/test_appointment.py -v -s
"""

import requests
import pytest
from datetime import datetime, timezone, timedelta
from requests.exceptions import ConnectionError, Timeout

BASE_URL = "http://127.0.0.1:8000"
APPOINTMENTS_ENDPOINT = f"{BASE_URL}/appointments"
PATIENTS_ENDPOINT = f"{BASE_URL}/patients"
DOCTORS_ENDPOINT = f"{BASE_URL}/doctors"


def test_server_is_reachable():
    """Check if server is reachable"""
    try:
        response = requests.get(f"{DOCTORS_ENDPOINT}/1", timeout=3)
        assert response.status_code in [200, 404]
    except (ConnectionError, Timeout):
        pytest.fail(
            "Server is not reachable. Start with: uvicorn src.main:app --reload"
        )


@pytest.fixture(scope="module")
def test_patient():
    """Create test patient"""
    import time

    timestamp = int(time.time() * 1000)
    payload = {
        "first_name": "Appointment",
        "last_name": "Tester",
        "email": f"appt.tester.{timestamp}@example.com",
        "phone": "5555555555",
        "age": 40,
    }
    response = requests.post(PATIENTS_ENDPOINT, json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="module")
def test_doctor():
    """Create test doctor"""
    payload = {
        "full_name": "Dr. Appointment Tester",
        "specialization": "General Practice",
    }
    response = requests.post(DOCTORS_ENDPOINT, json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_appointment_success(test_patient, test_doctor):
    """Test creating a new appointment"""
    # Schedule appointment for tomorrow
    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt_time = appt_time.replace(hour=10, minute=0, second=0, microsecond=0)

    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 30,
    }

    response = requests.post(APPOINTMENTS_ENDPOINT, json=payload)

    assert response.status_code == 201, f"Failed to create appointment: {response.text}"
    data = response.json()

    assert data["patient_id"] == test_patient["id"]
    assert data["doctor_id"] == test_doctor["id"]
    assert data["duration_minutes"] == 30
    assert "id" in data


def test_create_appointment_conflict(test_patient, test_doctor):
    """Test appointment conflict detection"""
    # Schedule first appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=2)
    appt_time = appt_time.replace(hour=14, minute=0, second=0, microsecond=0)

    payload1 = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 60,
    }

    response1 = requests.post(APPOINTMENTS_ENDPOINT, json=payload1)
    assert response1.status_code == 201

    # Try to schedule conflicting appointment (15 minutes later, overlaps)
    conflicting_time = appt_time + timedelta(minutes=15)
    payload2 = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        "start_datetime": conflicting_time.isoformat(),
        "duration_minutes": 30,
    }

    response2 = requests.post(APPOINTMENTS_ENDPOINT, json=payload2)
    assert response2.status_code == 409
    assert "conflict" in response2.text.lower()


def test_create_appointment_nonexistent_doctor(test_patient):
    """Test appointment with non-existent doctor"""
    appt_time = datetime.now(timezone.utc) + timedelta(days=3)

    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": 99999,  # Non-existent
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 30,
    }

    response = requests.post(APPOINTMENTS_ENDPOINT, json=payload)
    assert response.status_code == 400
    assert "doctor" in response.text.lower()


def test_create_appointment_nonexistent_patient(test_doctor):
    """Test appointment with non-existent patient"""
    appt_time = datetime.now(timezone.utc) + timedelta(days=3)

    payload = {
        "patient_id": 99999,  # Non-existent
        "doctor_id": test_doctor["id"],
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 30,
    }

    response = requests.post(APPOINTMENTS_ENDPOINT, json=payload)
    assert response.status_code == 400


def test_create_appointment_inactive_doctor(test_patient):
    """Test appointment with inactive doctor"""
    import time

    # Create inactive doctor
    doctor_payload = {
        "full_name": f"Dr. Inactive Test {int(time.time())}",
        "specialization": "Surgery",
        "is_active": False,
    }
    doctor_response = requests.post(DOCTORS_ENDPOINT, json=doctor_payload)
    inactive_doctor = doctor_response.json()

    appt_time = datetime.now(timezone.utc) + timedelta(days=3)
    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": inactive_doctor["id"],
        "start_datetime": appt_time.isoformat(),
        "duration_minutes": 30,
    }

    response = requests.post(APPOINTMENTS_ENDPOINT, json=payload)
    assert response.status_code == 400
    assert "not active" in response.text.lower()


def test_list_appointments_by_date(test_patient, test_doctor):
    """Test listing appointments by date"""
    # Create appointment for specific date
    target_date = datetime.now(timezone.utc) + timedelta(days=5)
    target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)

    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        "start_datetime": target_date.isoformat(),
        "duration_minutes": 45,
    }

    requests.post(APPOINTMENTS_ENDPOINT, json=payload)

    # List appointments for that date
    date_str = target_date.strftime("%Y-%m-%d")
    response = requests.get(f"{APPOINTMENTS_ENDPOINT}?date={date_str}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_appointments_by_doctor_and_date(test_patient, test_doctor):
    """Test listing appointments filtered by doctor and date"""
    target_date = datetime.now(timezone.utc) + timedelta(days=6)
    target_date = target_date.replace(hour=11, minute=0, second=0, microsecond=0)

    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        "start_datetime": target_date.isoformat(),
        "duration_minutes": 30,
    }

    requests.post(APPOINTMENTS_ENDPOINT, json=payload)

    # List appointments for specific doctor and date
    date_str = target_date.strftime("%Y-%m-%d")
    response = requests.get(
        f"{APPOINTMENTS_ENDPOINT}?date={date_str}&doctor_id={test_doctor['id']}"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for appt in data:
        assert appt["doctor_id"] == test_doctor["id"]


def test_list_appointments_invalid_date():
    """Test invalid date format"""
    response = requests.get(f"{APPOINTMENTS_ENDPOINT}?date=invalid-date")
    assert response.status_code == 400


def test_create_appointment_missing_fields(test_patient, test_doctor):
    """Test validation for missing required fields"""
    payload = {
        "patient_id": test_patient["id"],
        "doctor_id": test_doctor["id"],
        # Missing start_datetime and duration_minutes
    }

    response = requests.post(APPOINTMENTS_ENDPOINT, json=payload)
    assert response.status_code == 422
