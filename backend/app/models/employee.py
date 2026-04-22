from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import RegistrationStatus
from app.database.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_number: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    registration_status: Mapped[str] = mapped_column(String(20), default=RegistrationStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    timetables = relationship("Timetable", back_populates="employee", cascade="all, delete-orphan")
    intents = relationship("SwapIntent", back_populates="employee", cascade="all, delete-orphan")
