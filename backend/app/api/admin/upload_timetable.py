from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_admin, get_db
from app.schemas.employee_schema import AdminLoginIn, EmployeeOut, TokenOut
from app.schemas.timetable_schema import UploadResultOut
from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService
from app.services.timetable_service import TimetableService

router = APIRouter()


@router.post("/login", response_model=TokenOut)
async def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.admin_login(payload)


@router.post("/timetable/upload", response_model=UploadResultOut)
async def upload_timetable(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV allowed")

    content = file.file.read()
    service = TimetableService(db)
    try:
        return service.upload_weekly_timetable(content)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/registration-requests", response_model=list[EmployeeOut])
async def list_pending_registrations(_: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.list_pending_registrations()


@router.post("/registration-requests/{employee_id}/approve", response_model=EmployeeOut)
async def approve_registration(employee_id: str, _: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    service = EmployeeService(db)
    try:
        return service.approve_registration(employee_id)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/registration-requests/{employee_id}/reject", response_model=EmployeeOut)
async def reject_registration(employee_id: str, _: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    service = EmployeeService(db)
    try:
        return service.reject_registration(employee_id)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
