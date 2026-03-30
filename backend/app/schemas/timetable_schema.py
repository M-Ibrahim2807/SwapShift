from datetime import date

from pydantic import BaseModel


class TimetableRowOut(BaseModel):
    date: date
    shift_name: str


class TimetableWeekOut(BaseModel):
    employee_id: str
    week_start: date
    week_end: date
    rows: list[TimetableRowOut]


class UploadResultOut(BaseModel):
    inserted_rows: int
    updated_rows: int
    employees_created: int
