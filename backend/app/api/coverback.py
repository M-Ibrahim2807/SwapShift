from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.coverback_schema import CancelCoverbackOut, CoverbackOut, CreateCoverbackIn
from app.services.coverback_service import CoverbackService

router = APIRouter()


@router.post("", response_model=CoverbackOut, status_code=status.HTTP_201_CREATED)
async def create_coverback_post(
    payload: CreateCoverbackIn,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = CoverbackService(db)
    try:
        return service.create_coverback_post(employee, payload.coverback_type, payload.target_date)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/alerts", response_model=list[CoverbackOut])
async def list_coverback_alerts(
    target_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_employee),
):
    service = CoverbackService(db)
    return service.list_open_alerts(target_date=target_date)


@router.get("/mine", response_model=list[CoverbackOut])
async def list_my_coverback_posts(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = CoverbackService(db)
    return service.list_employee_posts(employee)


@router.post("/{post_id}/cancel", response_model=CancelCoverbackOut)
async def cancel_coverback_post(
    post_id: int,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = CoverbackService(db)
    try:
        return service.cancel_coverback_post(employee, post_id)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
