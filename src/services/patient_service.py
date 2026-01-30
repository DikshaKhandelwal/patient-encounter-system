from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.patient import Patient
from src.schemas.patient import PatientCreate


def create_patient(db: Session, data: PatientCreate) -> Patient:
    """
    Create a new patient record.
    """
    patient = Patient(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        age=data.age,
    )

    db.add(patient)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("A patient with this email already exists.")

    db.refresh(patient)
    return patient


def get_patient_by_id(db: Session, patient_id: int) -> Patient | None:
    """
    Retrieve a patient by their unique ID.
    """
    return db.query(Patient).filter(Patient.id == patient_id).first()
