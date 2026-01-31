"""
Unit tests for models and schemas - focused on core business logic
Run with: pytest tests/unit/ -v --cov=src
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.schemas.appointment import AppointmentCreate
from src.services.patient_service import create_patient
from src.services.doctor_service import create_doctor
from src.services.appointment_service import create_appointment
from src.schemas.patient import PatientCreate
from src.schemas.doctor import DoctorCreate


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


# ========== Core Model Tests ==========


def test_patient_model_table_name(test_db):
    """Test patient model table configuration"""
    assert Patient.__tablename__ == "diksha-patients1"


def test_doctor_model_table_name(test_db):
    """Test doctor model table configuration"""
    assert Doctor.__tablename__ == "diksha-doctors1"


# ========== DateTime Edge Cases ==========


def test_appointment_timezone_aware(test_db):
    """Test appointment with timezone-aware datetime"""
    patient_data = PatientCreate(
        first_name="Timezone",
        last_name="Aware",
        email="timezone@example.com",
        phone="4444444444",
        age=40,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Timezone", specialization="Timing")
    doctor = create_doctor(test_db, doctor_data)

    # Create appointment with specific timezone
    tz_aware_time = datetime(2026, 2, 15, 14, 30, 0, tzinfo=timezone.utc)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=tz_aware_time,
        duration_minutes=30,
    )
    appointment = create_appointment(test_db, appt_data)

    assert appointment.start_datetime.tzinfo is not None
    assert appointment.start_datetime == tz_aware_time


def test_multiple_appointments_same_patient(test_db):
    """Test patient can have multiple appointments"""
    patient_data = PatientCreate(
        first_name="Multiple",
        last_name="Appointments",
        email="multiple@example.com",
        phone="5555555555",
        age=38,
    )
    patient = create_patient(test_db, patient_data)

    doctor1_data = DoctorCreate(full_name="Dr. First", specialization="Cardiology")
    doctor1 = create_doctor(test_db, doctor1_data)

    doctor2_data = DoctorCreate(full_name="Dr. Second", specialization="Neurology")
    doctor2 = create_doctor(test_db, doctor2_data)

    # Create multiple appointments
    start_time = datetime.now(timezone.utc) + timedelta(days=7)

    appt1_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor1.id,
        start_datetime=start_time,
        duration_minutes=30,
    )
    appt1 = create_appointment(test_db, appt1_data)

    appt2_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor2.id,
        start_datetime=start_time + timedelta(days=1),
        duration_minutes=45,
    )
    appt2 = create_appointment(test_db, appt2_data)

    assert appt1.id != appt2.id
    assert appt1.patient_id == appt2.patient_id


def test_multiple_appointments_same_doctor(test_db):
    """Test doctor can have appointments with different patients"""
    patient1_data = PatientCreate(
        first_name="Patient",
        last_name="One",
        email="patient1.multi@example.com",
        phone="6666666666",
        age=30,
    )
    patient1 = create_patient(test_db, patient1_data)

    patient2_data = PatientCreate(
        first_name="Patient",
        last_name="Two",
        email="patient2.multi@example.com",
        phone="7777777777",
        age=35,
    )
    patient2 = create_patient(test_db, patient2_data)

    doctor_data = DoctorCreate(
        full_name="Dr. Popular", specialization="General Practice"
    )
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=8)

    appt1_data = AppointmentCreate(
        patient_id=patient1.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=30,
    )
    appt1 = create_appointment(test_db, appt1_data)

    appt2_data = AppointmentCreate(
        patient_id=patient2.id,
        doctor_id=doctor.id,
        start_datetime=start_time + timedelta(hours=1),
        duration_minutes=30,
    )
    appt2 = create_appointment(test_db, appt2_data)

    assert appt1.id != appt2.id
    assert appt1.doctor_id == appt2.doctor_id
    assert appt1.patient_id != appt2.patient_id


def test_appointment_end_datetime_property(test_db):
    """Test appointment end_datetime calculated property"""
    patient_data = PatientCreate(
        first_name="Property",
        last_name="Test",
        email="property@example.com",
        phone="3334445555",
        age=45,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Property", specialization="Oncology")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime(2026, 6, 10, 9, 0, 0, tzinfo=timezone.utc)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=45,
    )
    appointment = create_appointment(test_db, appt_data)

    # Test end_datetime property
    expected_end = start_time + timedelta(minutes=45)
    assert appointment.end_datetime == expected_end
    assert appointment.end_datetime.tzinfo is not None
