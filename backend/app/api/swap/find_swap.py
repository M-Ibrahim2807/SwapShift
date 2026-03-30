from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.schemas.swap_schema import FindSwapIn, FindSwapOut
from app.services.matching_engine import MatchingEngine

router = APIRouter()


@router.post("/find", response_model=FindSwapOut)
async def find_swap(
    payload: FindSwapIn,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    engine = MatchingEngine(db)
    try:
        return engine.build_and_match(employee, payload)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
