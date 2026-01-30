from sqlalchemy.orm import Session

from src.models.doctor import Doctor
from src.schemas.doctor import DoctorCreate


def create_doctor(db: Session, data: DoctorCreate) -> Doctor:
    """
    Create a new doctor record.
    """
    doctor = Doctor(
        full_name=data.full_name,
        specialization=data.specialization,
        is_active=data.is_active,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor | None:
    """
    Retrieve a doctor by their unique ID.
    """
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()
