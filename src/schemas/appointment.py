from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., description="ID of the patient")
    doctor_id: int = Field(..., description="ID of the doctor")
    start_datetime: datetime = Field(
        ..., description="Start date and time of the appointment"
    )
    duration_minutes: int = Field(
        ..., description="Duration of the appointment in minutes"
    )
    reason: str | None = Field(None, description="Reason for the appointment")

    @field_validator("duration_minutes")
    def validate_duration(cls, v):
        if not 15 <= v <= 180:
            raise ValueError("Duration must be between 15 and 180 minutes")
        return v

    @field_validator("start_datetime")
    def validate_start_datetime(cls, v):
        # Rule 3: All datetime values must be timezone-aware
        if v.tzinfo is None:
            raise ValueError("start_datetime must be timezone-aware")

        # Rule 2: Appointments must be scheduled in the future
        if v <= datetime.now(timezone.utc):
            raise ValueError("Appointment must be scheduled in the future")

        return v


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_datetime: datetime
    duration_minutes: int
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True
