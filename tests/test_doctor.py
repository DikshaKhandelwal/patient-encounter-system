import requests

BASE_URL = "http://127.0.0.1:8000"


def test_create_doctor_success():
    """Test creating a doctor successfully"""
    payload = {
        "full_name": "Dr. Diksha K",
        "specialization": "Cardiology",
        "is_active": True,
    }
    response = requests.post(f"{BASE_URL}/doctors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Dr. Diksha K"
    assert data["specialization"] == "Cardiology"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_doctor_inactive():
    """Test creating an inactive doctor"""
    payload = {
        "full_name": "Dr. c",
        "specialization": "Neurology",
        "is_active": False,
    }
    response = requests.post(f"{BASE_URL}/doctors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Dr. c"
    assert data["is_active"] is False


def test_create_doctor_default_active():
    """Test creating a doctor defaults to active"""
    payload = {"full_name": "Dr. E", "specialization": "General Practice"}
    response = requests.post(f"{BASE_URL}/doctors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is True


def test_get_doctor_success():
    """Test retrieving a doctor by ID"""
    # Create doctor first
    create_payload = {"full_name": "Dr. Robert Smith", "specialization": "Dermatology"}
    create_response = requests.post(f"{BASE_URL}/doctors", json=create_payload)
    assert create_response.status_code == 201
    doctor_id = create_response.json()["id"]

    # Get doctor
    get_response = requests.get(f"{BASE_URL}/doctors/{doctor_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["full_name"] == "Dr. Robert Smith"
    assert data["specialization"] == "Dermatology"
    assert data["id"] == doctor_id
    assert data["is_active"] is True


def test_get_doctor_not_found():
    """Test getting non-existent doctor returns 404"""
    non_existent_id = 99999
    response = requests.get(f"{BASE_URL}/doctors/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Doctor not found"


def test_create_doctor_missing_fields():
    """Test creating doctor with missing required fields"""
    payload = {"full_name": "Dr. Incomplete"}
    response = requests.post(f"{BASE_URL}/doctors", json=payload)
    assert response.status_code == 422


def test_update_doctor_is_active():
    """Test deactivating/reactivating a doctor"""
    # Create doctor
    create_payload = {"full_name": "Dr. John Doe", "specialization": "Surgery"}
    create_response = requests.post(f"{BASE_URL}/doctors", json=create_payload)
    doctor_id = create_response.json()["id"]

    # Deactivate doctor
    update_payload = {"is_active": False}
    update_response = requests.put(
        f"{BASE_URL}/doctors/{doctor_id}", json=update_payload
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["is_active"] is False

    # Verify deactivation
    get_response = requests.get(f"{BASE_URL}/doctors/{doctor_id}")
    assert get_response.json()["is_active"] is False
