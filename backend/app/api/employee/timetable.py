from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.timetable_schema import ManualTimetableUpsertIn, TimetableStateOut
from app.services.timetable_service import TimetableService
from pydantic import BaseModel

router = APIRouter()


class AvailableShiftsOut(BaseModel):
    date: date
    shifts: list[dict]  # List of available shifts with count


class EmployeeSummaryOut(BaseModel):
    employee_id: str
    name: str
    morning_shifts: int
    evening_shifts: int
    off_days: int


@router.get("/timetable", response_model=TimetableStateOut)
async def get_current_week_timetable(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = TimetableService(db)
    return service.get_current_week_for_employee(employee)


@router.put("/timetable", response_model=TimetableStateOut)
async def upsert_manual_timetable(
    payload: ManualTimetableUpsertIn,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = TimetableService(db)
    try:
        return service.upsert_manual_timetable_for_employee(employee, payload)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/timetable/available-shifts/{work_date}", response_model=AvailableShiftsOut)
async def get_available_shifts_for_date(
    work_date: date,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    """
    Get all available shift times for a specific date, excluding the current employee's shift
    """
    service = TimetableService(db)
    try:
        service.ensure_timetable_exists(employee)
        available_shifts = service.get_available_shifts_for_date(employee, work_date)
        return AvailableShiftsOut(date=work_date, shifts=available_shifts)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/summary", response_model=EmployeeSummaryOut)
async def get_employee_summary(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    """
    Get employee summary with name and shift counts for the current week
    """
    service = TimetableService(db)
    try:
        return service.get_employee_summary(employee)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
