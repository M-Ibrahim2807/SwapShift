from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import AuthException
from app.dependencies import get_db
from app.schemas.employee_schema import LoginIn, TokenOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.login(payload)
    except AuthException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
