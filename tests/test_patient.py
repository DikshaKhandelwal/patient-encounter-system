import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


def test_create_patient_success():
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.{datetime.now().timestamp()}@example.com",
        "phone": "1234567890",
        "age": 35,
    }
    response = requests.post(f"{BASE_URL}/patients", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data


def test_create_patient_missing_fields():
    payload = {
        "first_name": "Jane",
        "email": f"jane.{datetime.now().timestamp()}@example.com",
    }
    response = requests.post(f"{BASE_URL}/patients", json=payload)
    assert response.status_code == 422


def test_get_patient_success():
    payload = {
        "first_name": "Diksha",
        "last_name": "Khandelwal",
        "email": f"diksha.{datetime.now().timestamp()}@example.com",
        "phone": "9876543210",
        "age": 28,
    }
    create_response = requests.post(f"{BASE_URL}/patients", json=payload)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]

    get_response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["first_name"] == "Diksha"
    assert data["last_name"] == "Khandelwal"
    assert data["id"] == patient_id


def test_get_patient_not_found():
    non_existent_id = 99999
    response = requests.get(f"{BASE_URL}/patients/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Patient not found"


def test_create_patient_duplicate_email():
    email = f"duplicate.{datetime.now().timestamp()}@example.com"
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": email,
        "phone": "5551234567",
        "age": 40,
    }
    response1 = requests.post(f"{BASE_URL}/patients", json=payload)
    assert response1.status_code == 201

    response2 = requests.post(f"{BASE_URL}/patients", json=payload)
    assert response2.status_code == 400
    data = response2.json()
    assert "already exists" in data["detail"] or "Duplicate" in data["detail"]


def test_create_patient_invalid_email():
    payload = {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "invalid-email-format",
        "phone": "5559876543",
        "age": 50,
    }
    response = requests.post(f"{BASE_URL}/patients", json=payload)
    assert response.status_code == 422
