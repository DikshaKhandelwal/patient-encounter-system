from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    DateTime,
    func,
    Boolean,
)
from src.database import Base

if TYPE_CHECKING:
    from src.models.appointment import Appointment


class Doctor(Base):
    """
    Represents a healthcare provider who can be scheduled.

    """

    __tablename__ = "diksha-doctors1"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    # Full name
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Medical specialization
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)

    # Active status (boolean) - for soft delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Created timestamp (Rule 6: All records must include creation timestamps)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    # Rule 5: ondelete='RESTRICT' prevents deletion of doctors with existing appointments
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="doctor"
    )
