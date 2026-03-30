from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.timetable_schema import TimetableWeekOut
from app.services.timetable_service import TimetableService

router = APIRouter()


@router.get("/timetable", response_model=TimetableWeekOut)
async def get_current_week_timetable(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = TimetableService(db)
    try:
        return service.get_current_week_for_employee(employee)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
