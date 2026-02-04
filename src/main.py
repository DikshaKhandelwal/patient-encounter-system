# Main application entry point
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.schemas.appointment import AppointmentCreate, AppointmentRead
from src.database import SessionLocal, engine, Base
from src.services.patient_service import create_patient, get_patient_by_id
from src.services.doctor_service import create_doctor, get_doctor_by_id
from src.services.appointment_service import (
    create_appointment,
    get_appointments_by_doctor_and_date,
)
from src.schemas.patient import PatientCreate, PatientRead
from src.schemas.doctor import DoctorCreate, DoctorRead, DoctorUpdate

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Encounter System", version="1.0.0")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint for API validation"""
    return {
        "status": "healthy",
        "service": "Patient Encounter System",
        "version": "1.0.0",
    }


# Patient APIs
@app.post("/patients", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient"""
    try:
        return create_patient(db, patient)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient_endpoint(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve a patient by ID"""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


# Doctor APIs
@app.post("/doctors", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor_endpoint(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """Create a new doctor"""
    try:
        return create_doctor(db, doctor)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    """Retrieve a doctor by ID"""
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )
    return doctor


@app.put("/doctors/{doctor_id}", response_model=DoctorRead)
def update_doctor_endpoint(
    doctor_id: int, doctor_update: DoctorUpdate, db: Session = Depends(get_db)
):
    """Update a doctor's information"""
    doctor = get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
        )

    # Update only provided fields
    if doctor_update.full_name is not None:
        doctor.full_name = doctor_update.full_name
    if doctor_update.specialization is not None:
        doctor.specialization = doctor_update.specialization
    if doctor_update.is_active is not None:
        doctor.is_active = doctor_update.is_active

    db.commit()
    db.refresh(doctor)
    return doctor


# Appointment APIs
@app.post(
    "/appointments", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED
)
def create_appointment_endpoint(
    appointment: AppointmentCreate, db: Session = Depends(get_db)
):
    """Schedule a new appointment"""
    try:
        return create_appointment(db, appointment)
    except ValueError as e:
        error_msg = str(e)
        if "conflicting" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/appointments", response_model=list[AppointmentRead])
def list_appointments_endpoint(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    doctor_id: int | None = Query(None, description="Optional doctor ID to filter"),
    db: Session = Depends(get_db),
):
    """List appointments for a specific date"""
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        parsed_date = parsed_date.replace(tzinfo=timezone.utc)

        if doctor_id:
            # Get appointments for specific doctor on that date
            appointments = get_appointments_by_doctor_and_date(
                db, doctor_id, parsed_date
            )
        else:
            # Get all appointments for that date
            from datetime import timedelta

            from sqlalchemy import and_

            from src.models.appointment import Appointment

            day_start = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            appointments = (
                db.query(Appointment)
                .filter(
                    and_(
                        Appointment.start_datetime >= day_start,
                        Appointment.start_datetime < day_end,
                    )
                )
                .order_by(Appointment.start_datetime)
                .all()
            )

        return appointments
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD (e.g., 2026-01-30)",
        )
