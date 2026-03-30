from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.shift_request import ShiftRequest


class RequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> ShiftRequest:
        req = ShiftRequest(**kwargs)
        self.db.add(req)
        self.db.flush()
        return req

    def get_by_id(self, request_id: int) -> ShiftRequest | None:
        return self.db.scalar(select(ShiftRequest).where(ShiftRequest.id == request_id))

    def list_for_employee(self, employee_pk: int) -> list[ShiftRequest]:
        stmt = select(ShiftRequest).where(
            or_(ShiftRequest.requester_id == employee_pk, ShiftRequest.receiver_id == employee_pk)
        )
        return list(self.db.scalars(stmt))

    def list_pending_inbox(self, employee_pk: int, now_utc: datetime) -> list[ShiftRequest]:
        stmt = select(ShiftRequest).where(
            and_(
                ShiftRequest.receiver_id == employee_pk,
                ShiftRequest.status == "PENDING",
                ShiftRequest.expires_at > now_utc,
            )
        )
        return list(self.db.scalars(stmt))

    def has_active_pair(self, requester_intent_id: int, receiver_intent_id: int) -> bool:
        stmt = select(ShiftRequest).where(
            and_(
                ShiftRequest.requester_intent_id == requester_intent_id,
                ShiftRequest.receiver_intent_id == receiver_intent_id,
                ShiftRequest.status == "PENDING",
            )
        )
        return self.db.scalar(stmt) is not None

    def expire_due_requests(self, now_utc: datetime) -> int:
        stmt = select(ShiftRequest).where(
            and_(ShiftRequest.status == "PENDING", ShiftRequest.expires_at <= now_utc)
        )
        rows = list(self.db.scalars(stmt))
        for row in rows:
            row.status = "EXPIRED"
            row.responded_at = now_utc
            self.db.add(row)
        self.db.flush()
        return len(rows)
