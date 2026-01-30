from pydantic import BaseModel, PositiveInt
from datetime import datetime


class DoctorCreate(BaseModel):
    full_name: str
    specialization: str
    is_active: bool = True  # Defaults to active when creating


class DoctorUpdate(BaseModel):
    full_name: str | None = None
    specialization: str | None = None
    is_active: bool | None = None


class DoctorRead(DoctorCreate):
    id: PositiveInt
    created_at: datetime

    class Config:
        from_attributes = True
