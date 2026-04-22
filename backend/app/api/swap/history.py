from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_employee, get_db
from app.models.employee import Employee
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.swap_repo import SwapRepository
from app.repositories.timetable_repo import TimetableRepository
from app.services.swap_service import SwapService

router = APIRouter()


def serialize_request(row, viewer, employee_repo, timetable_repo, swap_repo):
    requester_info = {
        "requester_employee_id": "Unknown",
        "requester_contact": "N/A",
    }
    
    # Fetch requester details
    try:
        requester = employee_repo.get_by_pk(row.requester_id)
        if requester:
            requester_info["requester_employee_id"] = requester.employee_id or "Unknown"
            requester_info["requester_contact"] = requester.contact_number or "N/A"
    except Exception:
        pass

    requester_shift = None
    receiver_shift = None
    try:
        requester_intent = swap_repo.get_by_id(row.requester_intent_id)
        if requester_intent:
            requester_shift = requester_intent.current_payload.get("shift")
    except Exception:
        pass

    try:
        receiver_intent = swap_repo.get_by_id(row.receiver_intent_id)
        if receiver_intent:
            receiver_shift = receiver_intent.current_payload.get("shift")
    except Exception:
        pass

    # Fallback to timetable rows if intent payloads are unavailable.
    if requester_shift is None:
        try:
            shift = timetable_repo.get_shift(row.requester_id, row.start_date)
            if shift:
                requester_shift = shift.shift_name
        except Exception:
            pass

    if receiver_shift is None:
        try:
            shift = timetable_repo.get_shift(row.receiver_id, row.start_date)
            if shift:
                receiver_shift = shift.shift_name
        except Exception:
            pass

    viewer_current_shift = None
    other_person_shift = None
    if viewer.id == row.requester_id:
        viewer_current_shift = requester_shift
        other_person_shift = receiver_shift
    elif viewer.id == row.receiver_id:
        viewer_current_shift = receiver_shift
        other_person_shift = requester_shift

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
        "requester_shift": requester_shift,
        "receiver_shift": receiver_shift,
        "viewer_current_shift": viewer_current_shift,
        "other_person_shift": other_person_shift,
        **requester_info,
    }


@router.get("/history")
async def swap_history(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    employee_repo = EmployeeRepository(db)
    timetable_repo = TimetableRepository(db)
    swap_repo = SwapRepository(db)
    rows = service.list_history(employee.id)
    return [serialize_request(row, employee, employee_repo, timetable_repo, swap_repo) for row in rows]


@router.get("/inbox")
async def swap_inbox(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee),
):
    service = SwapService(db)
    employee_repo = EmployeeRepository(db)
    timetable_repo = TimetableRepository(db)
    swap_repo = SwapRepository(db)
    rows = service.list_inbox(employee.id)
    return [serialize_request(row, employee, employee_repo, timetable_repo, swap_repo) for row in rows]
