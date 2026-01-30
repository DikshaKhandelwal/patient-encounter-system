"""
Unit tests for services - tests the code directly without HTTP
Run these with: pytest tests/unit/ -v --cov=src --cov-report=html
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.schemas.patient import PatientCreate
from src.schemas.doctor import DoctorCreate
from src.schemas.appointment import AppointmentCreate
from src.services.patient_service import create_patient, get_patient_by_id
from src.services.doctor_service import create_doctor, get_doctor_by_id
from src.services.appointment_service import create_appointment, get_appointment_by_id


# Use in-memory SQLite database for testing
@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


# ========== Patient Service Tests ==========


def test_create_patient_success(test_db):
    """Test creating a patient"""
    patient_data = PatientCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        age=35,
    )
    patient = create_patient(test_db, patient_data)

    assert patient.id is not None
    assert patient.first_name == "John"
    assert patient.last_name == "Doe"
    assert patient.email == "john@example.com"
    assert patient.age == 35


def test_get_patient_by_id_success(test_db):
    """Test retrieving patient by ID"""
    patient_data = PatientCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="9876543210",
        age=28,
    )
    created = create_patient(test_db, patient_data)
    retrieved = get_patient_by_id(test_db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.first_name == "Jane"


def test_get_patient_by_id_not_found(test_db):
    """Test getting non-existent patient"""
    result = get_patient_by_id(test_db, 99999)
    assert result is None


def test_create_patient_duplicate_email(test_db):
    """Test duplicate email handling"""
    patient_data = PatientCreate(
        first_name="Test",
        last_name="User",
        email="duplicate@example.com",
        phone="5555555555",
        age=40,
    )
    create_patient(test_db, patient_data)

    with pytest.raises(ValueError) as excinfo:
        create_patient(test_db, patient_data)
    assert "already exists" in str(excinfo.value)


# ========== Doctor Service Tests ==========


def test_create_doctor_success(test_db):
    """Test creating a doctor"""
    doctor_data = DoctorCreate(
        full_name="Dr. Sarah Johnson", specialization="Cardiology"
    )
    doctor = create_doctor(test_db, doctor_data)

    assert doctor.id is not None
    assert doctor.full_name == "Dr. Sarah Johnson"
    assert doctor.specialization == "Cardiology"
    assert doctor.is_active is True


def test_create_doctor_inactive(test_db):
    """Test creating inactive doctor"""
    doctor_data = DoctorCreate(
        full_name="Dr. Michael Chen", specialization="Neurology", is_active=False
    )
    doctor = create_doctor(test_db, doctor_data)

    assert doctor.is_active is False


def test_get_doctor_by_id_success(test_db):
    """Test retrieving doctor by ID"""
    doctor_data = DoctorCreate(
        full_name="Dr. Emily White", specialization="General Practice"
    )
    created = create_doctor(test_db, doctor_data)
    retrieved = get_doctor_by_id(test_db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.full_name == "Dr. Emily White"


def test_get_doctor_by_id_not_found(test_db):
    """Test getting non-existent doctor"""
    result = get_doctor_by_id(test_db, 99999)
    assert result is None


# ========== Appointment Service Tests ==========


def test_create_appointment_success(test_db):
    """Test creating an appointment"""
    # Create patient and doctor
    patient_data = PatientCreate(
        first_name="John",
        last_name="Doe",
        email="john.appt@example.com",
        phone="1234567890",
        age=35,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(
        full_name="Dr. Sarah Johnson", specialization="Cardiology"
    )
    doctor = create_doctor(test_db, doctor_data)

    # Create appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=30,
        reason="Checkup",
    )
    appointment = create_appointment(test_db, appt_data)

    assert appointment.id is not None
    assert appointment.patient_id == patient.id
    assert appointment.doctor_id == doctor.id
    assert appointment.duration_minutes == 30


def test_create_appointment_nonexistent_doctor(test_db):
    """Test appointment with non-existent doctor"""
    patient_data = PatientCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.appt@example.com",
        phone="9876543210",
        age=28,
    )
    patient = create_patient(test_db, patient_data)

    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=99999,
        start_datetime=appt_time,
        duration_minutes=30,
    )

    with pytest.raises(ValueError) as excinfo:
        create_appointment(test_db, appt_data)
    assert "Doctor does not exist" in str(excinfo.value)


def test_create_appointment_inactive_doctor(test_db):
    """Test appointment with inactive doctor"""
    patient_data = PatientCreate(
        first_name="Test",
        last_name="Patient",
        email="test.patient@example.com",
        phone="5555555555",
        age=40,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(
        full_name="Dr. Inactive", specialization="Surgery", is_active=False
    )
    doctor = create_doctor(test_db, doctor_data)

    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=30,
    )

    with pytest.raises(ValueError) as excinfo:
        create_appointment(test_db, appt_data)
    assert "not active" in str(excinfo.value)


def test_appointment_conflict_detection(test_db):
    """Test overlapping appointment detection"""
    patient_data = PatientCreate(
        first_name="Conflict",
        last_name="Test",
        email="conflict@example.com",
        phone="5551234567",
        age=45,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Busy", specialization="Emergency")
    doctor = create_doctor(test_db, doctor_data)

    # First appointment
    appt_time = datetime.now(timezone.utc) + timedelta(days=1)
    appt1_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=60,
    )
    create_appointment(test_db, appt1_data)

    # Overlapping appointment (30 min after first starts)
    overlapping_time = appt_time + timedelta(minutes=30)
    appt2_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=overlapping_time,
        duration_minutes=30,
    )

    with pytest.raises(ValueError) as excinfo:
        create_appointment(test_db, appt2_data)
    assert "conflicting" in str(excinfo.value).lower()


def test_non_overlapping_appointments(test_db):
    """Test that non-overlapping appointments are allowed"""
    patient_data = PatientCreate(
        first_name="Sequential",
        last_name="Appointments",
        email="sequential@example.com",
        phone="5559876543",
        age=50,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Sequential", specialization="Pediatrics")
    doctor = create_doctor(test_db, doctor_data)

    # First appointment: 1:00 PM - 1:30 PM
    appt_time = datetime.now(timezone.utc) + timedelta(days=1, hours=1)
    appt1_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=30,
    )
    create_appointment(test_db, appt1_data)

    # Second appointment: 2:00 PM - 2:30 PM (after first ends)
    appt2_time = appt_time + timedelta(minutes=60)
    appt2_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt2_time,
        duration_minutes=30,
    )
    appointment2 = create_appointment(test_db, appt2_data)

    assert appointment2.id is not None


def test_get_appointment_by_id(test_db):
    """Test retrieving appointment by ID"""
    patient_data = PatientCreate(
        first_name="Get",
        last_name="Appointment",
        email="getappt@example.com",
        phone="5551111111",
        age=35,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Get", specialization="Dentistry")
    doctor = create_doctor(test_db, doctor_data)

    appt_time = datetime.now(timezone.utc) + timedelta(days=2)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=45,
        reason="Cleaning",
    )
    created = create_appointment(test_db, appt_data)
    retrieved = get_appointment_by_id(test_db, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.reason == "Cleaning"


def test_get_appointment_by_id_not_found(test_db):
    """Test getting non-existent appointment"""
    result = get_appointment_by_id(test_db, 99999)
    assert result is None


def test_appointment_with_min_duration(test_db):
    """Test appointment with minimum duration (15 minutes)"""
    patient_data = PatientCreate(
        first_name="Min",
        last_name="Duration",
        email="minduration@example.com",
        phone="5552222222",
        age=30,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Quick", specialization="Vaccines")
    doctor = create_doctor(test_db, doctor_data)

    appt_time = datetime.now(timezone.utc) + timedelta(days=3)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=15,  # Minimum
    )
    appointment = create_appointment(test_db, appt_data)

    assert appointment.duration_minutes == 15


def test_appointment_with_max_duration(test_db):
    """Test appointment with maximum duration (180 minutes)"""
    patient_data = PatientCreate(
        first_name="Max",
        last_name="Duration",
        email="maxduration@example.com",
        phone="5553333333",
        age=55,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Long", specialization="Surgery")
    doctor = create_doctor(test_db, doctor_data)

    appt_time = datetime.now(timezone.utc) + timedelta(days=4)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=appt_time,
        duration_minutes=180,  # Maximum
    )
    appointment = create_appointment(test_db, appt_data)

    assert appointment.duration_minutes == 180
