from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_db
from app.schemas.employee_schema import RegisterIn, RegisterOut
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.post("/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED)
async def register_employee(payload: RegisterIn, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    try:
        employee, message = service.register(payload)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return RegisterOut(
        employee_id=employee.employee_id,
        is_active=employee.is_active,
        registration_status=employee.registration_status,
        message=message,
    )
