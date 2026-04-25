from datetime import date, datetime

from pydantic import BaseModel


class CreateCoverbackIn(BaseModel):
    coverback_type: str
    target_date: date


class CoverbackOut(BaseModel):
    id: int
    employee_id: str
    name: str | None = None
    contact_number: str
    whatsapp_link: str
    coverback_type: str
    target_date: date
    employee_shift: str
    status: str
    created_at: datetime


class CancelCoverbackOut(BaseModel):
    id: int
    status: str
    whatsapp_link: str
    message: str
