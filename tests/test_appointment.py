import requests
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"


def test_create_appointment_success():
    """Test creating an appointment successfully"""
    # Create patient
    patient_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.{datetime.now().timestamp()}@example.com",
        "phone": "1234567890",
        "age": 35,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    # Create doctor
    doctor_payload = {
        "full_name": "Dr. Emily White",
        "specialization": "General Practice",
    }
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Create appointment
    appointment_time = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 30,
        "reason": "Annual checkup",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == patient_id
    assert data["doctor_id"] == doctor_id
    assert data["duration_minutes"] == 30
    assert "id" in data


'''def test_create_appointment_conflict():
    """Test creating conflicting appointments returns 409"""
    # Create patient and doctor
    patient_payload = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": f"jane.{datetime.now().timestamp()}@example.com",
        "phone": "9876543210",
        "age": 28,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    doctor_payload = {"full_name": "Dr. Busy Doctor", "specialization": "Dermatology"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Create first appointment
    appointment_time = datetime.now(timezone.utc) + timedelta(days=3)
    appointment1_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 60,
        "reason": "First appointment",
    }
    response1 = requests.post(f"{BASE_URL}/appointments", json=appointment1_payload)
    assert response1.status_code == 201

    # Try to create overlapping appointment - should return 409
    overlapping_time = appointment_time + timedelta(minutes=30)
    appointment2_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": overlapping_time.isoformat(),
        "duration_minutes": 30,
        "reason": "Conflicting appointment",
    }
    response2 = requests.post(f"{BASE_URL}/appointments", json=appointment2_payload)
    assert response2.status_code == 409
'''


def test_create_appointment_invalid_duration():
    """Test creating appointment with invalid duration"""
    appointment_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 10,  # Too short (minimum 15)
        "reason": "Quick visit",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 422


def test_create_appointment_past_datetime():
    """Test creating appointment in the past fails"""
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    appointment_payload = {
        "patient_id": 1,
        "doctor_id": 1,
        "start_datetime": past_time.isoformat(),
        "duration_minutes": 30,
        "reason": "Past appointment",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 422


def test_list_appointments_by_date():
    """Test listing appointments for a specific date"""
    target_date = datetime.now(timezone.utc) + timedelta(days=5)
    date_str = target_date.strftime("%Y-%m-%d")

    response = requests.get(f"{BASE_URL}/appointments?date={date_str}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_appointments_invalid_date_format():
    """Test listing appointments with invalid date format"""
    response = requests.get(f"{BASE_URL}/appointments?date=invalid-date")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid date format" in data["detail"]
