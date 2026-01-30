import requests
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"


# ========== Patient Additional Coverage Tests ==========


def test_get_patient_with_created_at():
    """Test that patient response includes created_at timestamp"""
    payload = {
        "first_name": "Test",
        "last_name": "Coverage",
        "email": f"coverage.{datetime.now().timestamp()}@example.com",
        "phone": "5555555555",
        "age": 45,
    }
    create_response = requests.post(f"{BASE_URL}/patients", json=payload)
    patient_id = create_response.json()["id"]

    get_response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    data = get_response.json()
    assert "created_at" in data
    assert data["created_at"] is not None


def test_create_multiple_patients():
    """Test creating multiple patients with different ages"""
    for age in [20, 30, 40, 50, 60]:
        payload = {
            "first_name": f"Patient{age}",
            "last_name": "Multiple",
            "email": f"patient{age}.{datetime.now().timestamp()}@example.com",
            "phone": f"555000{age}",
            "age": age,
        }
        response = requests.post(f"{BASE_URL}/patients", json=payload)
        assert response.status_code == 201
        assert response.json()["age"] == age


# ========== Doctor Additional Coverage Tests ==========


def test_doctor_defaults_to_active():
    """Verify doctor is active by default when not specified"""
    payload = {
        "full_name": "Dr. Default Active",
        "specialization": "Emergency Medicine",
    }
    response = requests.post(f"{BASE_URL}/doctors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is True


def test_deactivate_doctor_prevents_appointments():
    """Test that appointments cannot be scheduled with inactive doctor"""
    # Create and deactivate doctor
    doctor_payload = {"full_name": "Dr. Soon Inactive", "specialization": "Psychiatry"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Deactivate
    deactivate_payload = {"is_active": False}
    requests.put(f"{BASE_URL}/doctors/{doctor_id}", json=deactivate_payload)

    # Try to create appointment with inactive doctor
    patient_payload = {
        "first_name": "Test",
        "last_name": "Appointment",
        "email": f"test.appt.{datetime.now().timestamp()}@example.com",
        "phone": "5551112222",
        "age": 35,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 30,
        "reason": "Should fail",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]


def test_reactivate_doctor():
    """Test reactivating a deactivated doctor"""
    doctor_payload = {"full_name": "Dr. Reactivate", "specialization": "Urology"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    # Deactivate
    requests.put(f"{BASE_URL}/doctors/{doctor_id}", json={"is_active": False})

    # Reactivate
    reactivate_response = requests.put(
        f"{BASE_URL}/doctors/{doctor_id}", json={"is_active": True}
    )
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["is_active"] is True


# ========== Appointment Additional Coverage Tests ==========


def test_appointment_with_reason():
    """Test creating appointment with reason field"""
    patient_payload = {
        "first_name": "Reason",
        "last_name": "Test",
        "email": f"reason.{datetime.now().timestamp()}@example.com",
        "phone": "5556667777",
        "age": 42,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    doctor_payload = {"full_name": "Dr. Reason Tester", "specialization": "Oncology"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=7)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 45,
        "reason": "Comprehensive cancer screening",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reason"] == "Comprehensive cancer screening"


def test_appointment_without_reason():
    """Test creating appointment without optional reason field"""
    patient_payload = {
        "first_name": "No",
        "last_name": "Reason",
        "email": f"noreason.{datetime.now().timestamp()}@example.com",
        "phone": "5558889999",
        "age": 33,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    doctor_payload = {"full_name": "Dr. No Reason", "specialization": "Podiatry"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=2)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 20,
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 201
    assert response.json()["reason"] is None


def test_appointment_nonexistent_doctor():
    """Test creating appointment with non-existent doctor"""
    appointment_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_payload = {
        "patient_id": 1,
        "doctor_id": 99999,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 30,
        "reason": "Should fail",
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 400
    assert "Doctor does not exist" in response.json()["detail"]


def test_appointment_nonexistent_patient():
    """Test creating appointment with non-existent patient"""
    doctor_payload = {
        "full_name": "Dr. Nonexistent Patient Test",
        "specialization": "Radiology",
    }
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=1)
    # Note: This may not fail at appointment creation, but would fail at DB constraint
    appointment_payload = {
        "patient_id": 99999,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 30,
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    # Database foreign key constraint should catch this
    assert response.status_code in [400, 500]


def test_list_appointments_with_doctor_filter():
    """Test listing appointments filtered by doctor"""
    # Create doctor and appointment
    doctor_payload = {"full_name": "Dr. Filter Test", "specialization": "Rheumatology"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    patient_payload = {
        "first_name": "Filter",
        "last_name": "Test",
        "email": f"filter.{datetime.now().timestamp()}@example.com",
        "phone": "5559990000",
        "age": 55,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=10)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 60,
    }
    requests.post(f"{BASE_URL}/appointments", json=appointment_payload)

    # Query with doctor filter
    date_str = appointment_time.strftime("%Y-%m-%d")
    response = requests.get(
        f"{BASE_URL}/appointments?date={date_str}&doctor_id={doctor_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_max_duration_appointment():
    """Test creating appointment with maximum allowed duration (180 minutes)"""
    doctor_payload = {"full_name": "Dr. Long Duration", "specialization": "Surgery"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    patient_payload = {
        "first_name": "Long",
        "last_name": "Appointment",
        "email": f"long.{datetime.now().timestamp()}@example.com",
        "phone": "5551231234",
        "age": 60,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=8)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 180,  # Maximum
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 201


def test_min_duration_appointment():
    """Test creating appointment with minimum allowed duration (15 minutes)"""
    doctor_payload = {"full_name": "Dr. Quick Visit", "specialization": "Vaccination"}
    doctor_response = requests.post(f"{BASE_URL}/doctors", json=doctor_payload)
    doctor_id = doctor_response.json()["id"]

    patient_payload = {
        "first_name": "Quick",
        "last_name": "Visit",
        "email": f"quick.{datetime.now().timestamp()}@example.com",
        "phone": "5554445555",
        "age": 25,
    }
    patient_response = requests.post(f"{BASE_URL}/patients", json=patient_payload)
    patient_id = patient_response.json()["id"]

    appointment_time = datetime.now(timezone.utc) + timedelta(days=12)
    appointment_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_datetime": appointment_time.isoformat(),
        "duration_minutes": 15,  # Minimum
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_payload)
    assert response.status_code == 201
