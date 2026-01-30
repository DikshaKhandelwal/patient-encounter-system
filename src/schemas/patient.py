from datetime import datetime

from pydantic import BaseModel, EmailStr, PositiveInt


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    age: int


class PatientRead(PatientCreate):
    id: PositiveInt
    created_at: datetime
    updated_at: datetime | None
