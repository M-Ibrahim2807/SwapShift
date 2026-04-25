from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.constants import CoverbackStatus, CoverbackType
from app.core.exceptions import ValidationException
from app.repositories.coverback_repo import CoverbackRepository
from app.repositories.employee_repo import EmployeeRepository
from app.services.timetable_service import TimetableService
from app.utils.validators import canonicalize_shift_name
from app.utils.whatsapp_redirect import build_whatsapp_link


class CoverbackService:
    def __init__(self, db: Session):
        self.db = db
        self.coverback_repo = CoverbackRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.timetable_service = TimetableService(db)

    def create_coverback_post(self, employee, coverback_type: str, target_date: date):
        normalized_type = coverback_type.strip().upper()
        if normalized_type not in {CoverbackType.OFFER.value, CoverbackType.FIND.value}:
            raise ValidationException("coverback_type must be OFFER or FIND")

        self.timetable_service.ensure_timetable_exists(employee)
        if target_date < datetime.utcnow().date():
            raise ValidationException("Selected date must be today or later")

        employee_shift = self.timetable_service.get_shift_or_raise(employee.id, target_date)
        normalized_shift = canonicalize_shift_name(employee_shift)

        if normalized_type == CoverbackType.OFFER.value and normalized_shift != "OFF":
            raise ValidationException("You can offer coverback only on an OFF day")
        if normalized_type == CoverbackType.FIND.value and normalized_shift == "OFF":
            raise ValidationException("You can find coverback only on a working day")
        if self.coverback_repo.has_open_post(employee.id, target_date, normalized_type):
            raise ValidationException("You already have an open coverback post for this date")

        post = self.coverback_repo.create(
            employee_id=employee.id,
            coverback_type=normalized_type,
            target_date=target_date,
            employee_shift=normalized_shift,
            status=CoverbackStatus.OPEN.value,
        )
        self.db.commit()
        self.db.refresh(post)
        return self._serialize_post(post, employee)

    def list_open_alerts(self, target_date: date | None = None) -> list[dict]:
        posts = self.coverback_repo.list_open(target_date=target_date)
        return [self._serialize_post(post) for post in posts]

    def list_employee_posts(self, employee) -> list[dict]:
        posts = self.coverback_repo.list_for_employee(employee.id)
        return [self._serialize_post(post, employee) for post in posts]

    def cancel_coverback_post(self, employee, post_id: int) -> dict:
        post = self.coverback_repo.get_by_id(post_id)
        if post is None:
            raise ValidationException("Coverback post not found")
        if post.employee_id != employee.id:
            raise ValidationException("You can only cancel your own coverback post")
        if post.status != CoverbackStatus.OPEN.value:
            raise ValidationException("Coverback post is already closed")

        post.status = CoverbackStatus.CANCELLED.value
        self.coverback_repo.save(post)
        self.db.commit()
        self.db.refresh(post)
        return {
            "id": post.id,
            "status": post.status,
            "whatsapp_link": build_whatsapp_link(employee.contact_number),
            "message": "Coverback post cancelled successfully",
        }

    def _serialize_post(self, post, employee=None) -> dict:
        owner = employee if employee is not None and employee.id == post.employee_id else self.employee_repo.get_by_pk(post.employee_id)
        if owner is None:
            raise ValidationException("Coverback employee not found")
        return {
            "id": post.id,
            "employee_id": owner.employee_id,
            "name": owner.name,
            "contact_number": owner.contact_number,
            "whatsapp_link": build_whatsapp_link(owner.contact_number),
            "coverback_type": post.coverback_type,
            "target_date": post.target_date,
            "employee_shift": post.employee_shift,
            "status": post.status,
            "created_at": post.created_at,
        }
