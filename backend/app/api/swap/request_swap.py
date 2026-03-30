from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.swap_schema import CreateRequestIn, SwapRequestOut
from app.services.swap_service import SwapService

router = APIRouter()


@router.post("/request", response_model=SwapRequestOut)
async def request_swap(
    payload: CreateRequestIn,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    try:
        return service.create_request(
            requester=employee,
            my_intent_id=payload.my_intent_id,
            other_intent_id=payload.other_intent_id,
            expires_in_minutes=payload.expires_in_minutes,
        )
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
