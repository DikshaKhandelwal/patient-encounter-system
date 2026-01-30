from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.models.appointment import Appointment
from src.models.doctor import Doctor
from src.schemas.appointment import AppointmentCreate


def create_appointment(db: Session, data: AppointmentCreate) -> Appointment:
    """
    Create a new appointment with all validation rules enforced.
    """
    # Check if doctor exists and is active
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise ValueError("Doctor does not exist")
    if not doctor.is_active:
        raise ValueError("Doctor is not active")

    appointment_end = data.start_datetime + timedelta(minutes=data.duration_minutes)

    # Check for overlapping appointments
    # Get all appointments for this doctor on the same day (to reduce queries)
    # Two appointments overlap if: appointment1.start < appointment2.end AND appointment2.start < appointment1.end
    existing_appointments = (
        db.query(Appointment).filter(Appointment.doctor_id == data.doctor_id).all()
    )

    # Check each appointment to see if it overlaps
    for existing in existing_appointments:
        existing_end = existing.start_datetime + timedelta(
            minutes=existing.duration_minutes
        )
        # Overlap if: new starts before existing ends AND new ends after existing starts
        if (
            data.start_datetime < existing_end
            and appointment_end > existing.start_datetime
        ):
            raise ValueError("Doctor has a conflicting appointment at this time")

    appointment = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        start_datetime=data.start_datetime,
        duration_minutes=data.duration_minutes,
        reason=data.reason,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def get_appointment_by_id(db: Session, appointment_id: int) -> Appointment | None:
    """
    Retrieve an appointment by its unique ID.
    """
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def get_appointments_by_doctor_and_date(
    db: Session, doctor_id: int, date: datetime
) -> list[Appointment]:
    """
    Retrieve all appointments for a doctor on a specific date.

    """
    from datetime import timedelta

    # Ensure the date is timezone-aware
    if date.tzinfo is None:
        raise ValueError("Date must be timezone-aware")

    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_datetime >= day_start,
            Appointment.start_datetime < day_end,
        )
        .order_by(Appointment.start_datetime)
        .all()
    )

    return appointments
