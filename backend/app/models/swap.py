from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SwapIntent(Base):
    __tablename__ = "swap_intents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    swap_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    week_start: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    current_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    wanted_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="intents")
