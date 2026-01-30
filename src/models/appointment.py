from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from src.database import Base

if TYPE_CHECKING:
    from src.models.patient import Patient
    from src.models.doctor import Doctor


class Appointment(Base):
    """
    Represents a scheduled medical encounter.

    """

    __tablename__ = "diksha-appointments1"

    # Unique identifier
    id: Mapped[int] = mapped_column(primary_key=True)

    # Patient reference
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("diksha-patients1.id", ondelete="RESTRICT"), nullable=False
    )

    # Doctor reference
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("diksha-doctors1.id", ondelete="RESTRICT"), nullable=False
    )
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(nullable=False)

    # Reason for appointment
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")

    # Derived property - Appointment end time (not stored in database)
    @property
    def end_datetime(self) -> datetime:
        """Calculate appointment end time = start time + duration"""
        return self.start_datetime + timedelta(minutes=self.duration_minutes)
