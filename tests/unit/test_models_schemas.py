"""
Additional unit tests for schemas and models to increase coverage
Run with: pytest tests/unit/test_models_schemas.py -v --cov=src --cov-report=html
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from src.schemas.patient import PatientCreate, PatientRead
from src.schemas.doctor import DoctorCreate, DoctorRead, DoctorUpdate
from src.schemas.appointment import AppointmentCreate, AppointmentRead
from src.services.patient_service import create_patient
from src.services.doctor_service import create_doctor
from src.services.appointment_service import create_appointment


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


# ========== Schema Validation Tests ==========


def test_patient_schema_read_model():
    """Test PatientRead schema"""
    now = datetime.now(timezone.utc)
    patient_read = PatientRead(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        age=35,
        created_at=now,
        updated_at=None,
    )
    assert patient_read.id == 1
    assert patient_read.first_name == "John"


def test_doctor_schema_read_model():
    """Test DoctorRead schema"""
    now = datetime.now(timezone.utc)
    doctor_read = DoctorRead(
        id=1,
        full_name="Dr. Smith",
        specialization="Cardiology",
        is_active=True,
        created_at=now,
    )
    assert doctor_read.id == 1
    assert doctor_read.is_active is True


def test_doctor_schema_update():
    """Test DoctorUpdate schema"""
    update = DoctorUpdate(full_name="Dr. Updated", is_active=False)
    assert update.full_name == "Dr. Updated"
    assert update.is_active is False


def test_doctor_update_partial():
    """Test partial DoctorUpdate"""
    update = DoctorUpdate(full_name="Dr. New Name")
    assert update.full_name == "Dr. New Name"
    assert update.specialization is None
    assert update.is_active is None


def test_appointment_schema_read():
    """Test AppointmentRead schema"""
    now = datetime.now(timezone.utc)
    appt_read = AppointmentRead(
        id=1,
        patient_id=1,
        doctor_id=1,
        start_datetime=now,
        duration_minutes=30,
        reason="Checkup",
        created_at=now,
    )
    assert appt_read.duration_minutes == 30
    assert appt_read.reason == "Checkup"


# ========== Model Tests ==========


def test_patient_model_table_name(test_db):
    """Test patient model table configuration"""
    assert Patient.__tablename__ == "diksha-patients1"


def test_doctor_model_table_name(test_db):
    """Test doctor model table configuration"""
    assert Doctor.__tablename__ == "diksha-doctors1"


def test_appointment_model_table_name(test_db):
    """Test appointment model table configuration"""
    assert Appointment.__tablename__ == "diksha-appointments1"


'''def test_appointment_end_datetime_property(test_db):
    """Test appointment end_datetime derived property"""
    patient_data = PatientCreate(
        first_name="John",
        last_name="Doe",
        email="john.property@example.com",
        phone="1234567890",
        age=35,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Test", specialization="General")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=1)
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


def test_appointment_end_datetime_with_different_durations(test_db):
    """Test end_datetime with various durations"""
    patient_data = PatientCreate(
        first_name="Jane",
        last_name="Duration",
        email="jane.duration@example.com",
        phone="9876543210",
        age=28,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Duration", specialization="Pediatrics")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=2)

    # Test with 15 minutes (min)
    appt1_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=15,
    )
    appt1 = create_appointment(test_db, appt1_data)
    assert appt1.end_datetime == start_time + timedelta(minutes=15)

    # Test with 180 minutes (max)
    start_time2 = start_time + timedelta(hours=3)
    appt2_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time2,
        duration_minutes=180,
    )
    appt2 = create_appointment(test_db, appt2_data)
    assert appt2.end_datetime == start_time2 + timedelta(minutes=180)
'''


def test_appointment_string_representation(test_db):
    """Test appointment __repr__ method if it exists"""
    patient_data = PatientCreate(
        first_name="Repr",
        last_name="Test",
        email="repr@example.com",
        phone="5555555555",
        age=40,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Repr", specialization="Testing")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=3)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=30,
    )
    appointment = create_appointment(test_db, appt_data)

    # Test if __repr__ exists and works
    repr_str = repr(appointment)
    assert "Appointment" in repr_str


# ========== Relationship Tests ==========


def test_patient_appointments_relationship(test_db):
    """Test patient-appointment relationship"""
    patient_data = PatientCreate(
        first_name="Relation",
        last_name="Test",
        email="relation@example.com",
        phone="1111111111",
        age=45,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. Relation", specialization="Relationships")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=5)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=30,
    )
    create_appointment(test_db, appt_data)

    # Check relationship
    test_db.refresh(patient)
    assert hasattr(patient, "appointments")


def test_doctor_appointments_relationship(test_db):
    """Test doctor-appointment relationship"""
    patient_data = PatientCreate(
        first_name="Doctor",
        last_name="Relation",
        email="docrelation@example.com",
        phone="2222222222",
        age=35,
    )
    patient = create_patient(test_db, patient_data)

    doctor_data = DoctorCreate(full_name="Dr. DocRelation", specialization="Testing")
    doctor = create_doctor(test_db, doctor_data)

    start_time = datetime.now(timezone.utc) + timedelta(days=6)
    appt_data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_datetime=start_time,
        duration_minutes=45,
    )
    create_appointment(test_db, appt_data)

    # Check relationship
    test_db.refresh(doctor)
    assert hasattr(doctor, "appointments")


# ========== Edge Case Tests ==========


def test_patient_with_special_characters_in_name(test_db):
    """Test patient with special characters"""
    patient_data = PatientCreate(
        first_name="Jean-Pierre",
        last_name="O'Brien",
        email="special@example.com",
        phone="3333333333",
        age=50,
    )
    patient = create_patient(test_db, patient_data)
    assert patient.first_name == "Jean-Pierre"
    assert patient.last_name == "O'Brien"


def test_doctor_with_special_characters_in_name(test_db):
    """Test doctor with special characters"""
    doctor_data = DoctorCreate(
        full_name="Dr. María García", specialization="Ophthalmology"
    )
    doctor = create_doctor(test_db, doctor_data)
    assert "María" in doctor.full_name


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
        start_datetime=start_time + timedelta(hours=2),
        duration_minutes=30,
    )
    appt2 = create_appointment(test_db, appt2_data)

    assert appt1.doctor_id == appt2.doctor_id
    assert appt1.patient_id != appt2.patient_id
