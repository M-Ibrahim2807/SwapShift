from datetime import date

from pydantic import BaseModel, Field


class TimetableRowOut(BaseModel):
    date: date
    shift_name: str
    source: str


class TimetableStateOut(BaseModel):
    employee_id: str
    has_timetable: bool
    requires_manual_setup: bool
    week_start: date | None
    week_end: date | None
    rows: list[TimetableRowOut]
    message: str | None = None


class ManualTimetableRowIn(BaseModel):
    date: date
    shift_name: str = Field(min_length=1, max_length=20)


class ManualTimetableUpsertIn(BaseModel):
    rows: list[ManualTimetableRowIn]


class UploadResultOut(BaseModel):
    inserted_rows: int
    updated_rows: int
    employees_created: int
    skipped_manual_rows: int
