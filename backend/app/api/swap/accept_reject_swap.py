from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.request_schema import RequestDecisionIn
from app.services.swap_service import SwapService

router = APIRouter()


@router.post("/requests/{request_id}/decision")
async def decide_swap_request(
    request_id: int,
    payload: RequestDecisionIn,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    try:
        return service.decide_request(employee, request_id, payload.decision)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
