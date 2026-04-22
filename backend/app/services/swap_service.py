import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.exceptions import ValidationException
from app.database.session import SessionLocal
from app.models.swap_history import SwapHistory
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.request_repo import RequestRepository
from app.repositories.swap_repo import SwapRepository
from app.repositories.timetable_repo import TimetableRepository
from app.services.notification_service import NotificationService
from app.utils.whatsapp_redirect import build_whatsapp_link

logger = logging.getLogger(__name__)


class SwapService:
    def __init__(self, db: Session):
        self.db = db
        self.swap_repo = SwapRepository(db)
        self.request_repo = RequestRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.timetable_repo = TimetableRepository(db)
        self.notification = NotificationService()

    def create_request(self, requester, my_intent_id: int, other_intent_id: int, expires_in_minutes: int):
        my_intent = self.swap_repo.get_by_id(my_intent_id)
        other_intent = self.swap_repo.get_by_id(other_intent_id)
        
        if not my_intent:
            raise ValidationException("Your swap request is no longer valid. Please search again.")
        if not other_intent:
            raise ValidationException("The other person is no longer available for swap. They may have accepted another request.")
        
        if my_intent.employee_id != requester.id:
            raise ValidationException("my_intent_id does not belong to current employee")
        if other_intent.employee_id == requester.id:
            raise ValidationException("Cannot send request to self")
        
        if my_intent.status != "OPEN":
            raise ValidationException("Your swap request is no longer active. Please search again.")
        if other_intent.status != "OPEN":
            raise ValidationException("The other person is no longer available. They may have accepted another swap.")

        if my_intent.swap_type != other_intent.swap_type:
            raise ValidationException("Intent swap types do not match")
        if self.request_repo.has_active_pair(my_intent.id, other_intent.id):
            raise ValidationException("A pending request already exists for this swap pair")
        if self.request_repo.has_active_for_intent(my_intent.id):
            raise ValidationException("Your slot already has a pending swap request")
        if self.request_repo.has_active_for_intent(other_intent.id):
            raise ValidationException("The other person's slot already has a pending swap request")

        start_date, end_date = self._derive_date_range(my_intent)

        req = self.request_repo.create(
            requester_id=requester.id,
            receiver_id=other_intent.employee_id,
            requester_intent_id=my_intent.id,
            receiver_intent_id=other_intent.id,
            swap_type=my_intent.swap_type,
            start_date=start_date,
            end_date=end_date,
            status="PENDING",
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(minutes=expires_in_minutes),
        )

        receiver = self.employee_repo.get_by_pk(other_intent.employee_id)
        if receiver:
            self.notification.notify_swap_request(receiver, req.id)

        self.db.commit()
        self.db.refresh(req)
        return req

    def decide_request(self, current_employee, request_id: int, decision: str):
        req = self.request_repo.get_by_id(request_id)
        if req is None:
            raise ValidationException("Request not found")
        if req.receiver_id != current_employee.id:
            raise ValidationException("Only receiver can decide this request")
        if req.status != "PENDING":
            raise ValidationException("Request is already closed")

        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        if req.expires_at <= now_utc:
            req.status = "EXPIRED"
            self.db.add(req)
            self.db.commit()
            raise ValidationException("Request expired")

        normalized = decision.strip().upper()
        if normalized == "REJECT":
            req.status = "REJECTED"
            req.responded_at = now_utc
            self.db.add(req)
            self.db.commit()
            return {"status": "REJECTED"}

        if normalized != "ACCEPT":
            raise ValidationException("Decision must be ACCEPT or REJECT")

        requester_intent = self.swap_repo.get_by_id(req.requester_intent_id)
        receiver_intent = self.swap_repo.get_by_id(req.receiver_intent_id)
        if requester_intent is None or receiver_intent is None:
            raise ValidationException("Intents not found for request")
        if requester_intent.status != "OPEN" or receiver_intent.status != "OPEN":
            raise ValidationException("One of the swap slots is no longer available")

        self._apply_schedule_swap(req, requester_intent, receiver_intent)

        req.status = "ACCEPTED"
        req.responded_at = now_utc
        self.db.add(req)

        self.swap_repo.close_intent(requester_intent)
        self.swap_repo.close_intent(receiver_intent)

        history = SwapHistory(
            request_id=req.id,
            requester_id=req.requester_id,
            receiver_id=req.receiver_id,
            swap_type=req.swap_type,
            start_date=req.start_date,
            end_date=req.end_date,
        )
        self.db.add(history)

        self.db.commit()

        requester = self.employee_repo.get_by_pk(req.requester_id)
        receiver = self.employee_repo.get_by_pk(req.receiver_id)

        return {
            "status": "ACCEPTED",
            "requester_contact": requester.contact_number if requester else None,
            "receiver_contact": receiver.contact_number if receiver else None,
            "requester_whatsapp": build_whatsapp_link(requester.contact_number) if requester else None,
            "receiver_whatsapp": build_whatsapp_link(receiver.contact_number) if receiver else None,
        }

    def list_history(self, employee_pk: int):
        requests = self.request_repo.list_for_employee(employee_pk)
        return requests

    def list_inbox(self, employee_pk: int):
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.request_repo.list_pending_inbox(employee_pk, now_utc)

    def _derive_date_range(self, intent):
        if intent.swap_type in {"DAILY", "HOLIDAY"}:
            date_obj = intent.target_date
            return date_obj, date_obj

        dates = sorted(intent.current_payload.get("days", {}).keys())
        return datetime.fromisoformat(dates[0]).date(), datetime.fromisoformat(dates[-1]).date()

    def _apply_schedule_swap(self, req, requester_intent, receiver_intent):
        if req.swap_type in {"DAILY", "HOLIDAY"}:
            d = req.start_date
            requester_row = self.timetable_repo.get_shift(req.requester_id, d)
            receiver_row = self.timetable_repo.get_shift(req.receiver_id, d)
            if requester_row is None or receiver_row is None:
                raise ValidationException("Shift row missing for one employee")
            requester_row.shift_name, receiver_row.shift_name = (
                receiver_row.shift_name,
                requester_row.shift_name,
            )
            self.db.add(requester_row)
            self.db.add(receiver_row)
            return

        requester_days = requester_intent.current_payload.get("days", {})
        receiver_days = receiver_intent.current_payload.get("days", {})

        for day in sorted(requester_days.keys()):
            date_obj = datetime.fromisoformat(day).date()
            requester_row = self.timetable_repo.get_shift(req.requester_id, date_obj)
            receiver_row = self.timetable_repo.get_shift(req.receiver_id, date_obj)
            if requester_row is None or receiver_row is None:
                raise ValidationException(f"Missing timetable row on {day}")
            requester_row.shift_name, receiver_row.shift_name = (
                receiver_row.shift_name,
                requester_row.shift_name,
            )
            self.db.add(requester_row)
            self.db.add(receiver_row)


def expire_pending_requests_job() -> None:
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    settings = get_settings()
    db = SessionLocal()
    try:
        repo = RequestRepository(db)
        expired_count = repo.expire_due_requests(now_utc)
        if expired_count:
            logger.info(
                "expired_pending_requests",
                extra={
                    "expired_count": expired_count,
                    "cleanup_interval_seconds": settings.request_cleanup_interval_seconds,
                },
            )
        db.commit()
    finally:
        db.close()
