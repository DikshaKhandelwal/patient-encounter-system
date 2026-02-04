from pydantic import BaseModel, PositiveInt, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    created_at: datetime
