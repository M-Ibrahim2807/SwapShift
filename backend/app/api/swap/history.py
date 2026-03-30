from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.services.swap_service import SwapService

router = APIRouter()


def serialize_request(row):
    return {
        "id": row.id,
        "requester_id": row.requester_id,
        "receiver_id": row.receiver_id,
        "swap_type": row.swap_type,
        "start_date": row.start_date,
        "end_date": row.end_date,
        "status": row.status,
        "created_at": row.created_at,
        "responded_at": row.responded_at,
    }


@router.get("/history")
async def swap_history(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    rows = service.list_history(employee.id)
    return [serialize_request(row) for row in rows]


@router.get("/inbox")
async def swap_inbox(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    rows = service.list_inbox(employee.id)
    return [serialize_request(row) for row in rows]
