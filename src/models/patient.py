from sqlalchemy import (
    String,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from src.database import Base

if TYPE_CHECKING:
    from src.models.appointment import Appointment


class Patient(Base):
    __tablename__ = "diksha-patients1"
    __table_args__ = {"mysql_engine": "InnoDB", "extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    age: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="patient"
    )
