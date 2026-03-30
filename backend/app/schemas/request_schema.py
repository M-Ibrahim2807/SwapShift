from datetime import date, datetime

from pydantic import BaseModel


class RequestDecisionIn(BaseModel):
    decision: str  # ACCEPT or REJECT


class RequestDetailOut(BaseModel):
    request_id: int
    requester_employee_id: str
    requester_contact: str
    receiver_employee_id: str
    receiver_contact: str
    swap_type: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime
