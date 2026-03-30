from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.swap_repo import SwapRepository
from app.services.timetable_service import TimetableService
from datetime import date as date_type
from datetime import datetime

from app.utils.shift_matcher import is_reciprocal_daily


class MatchingEngine:
    def __init__(self, db: Session):
        self.db = db
        self.swap_repo = SwapRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.timetable_service = TimetableService(db)

    def build_and_match(self, employee, payload):
        swap_type = payload.swap_type

        if swap_type == "HOLIDAY":
            self._ensure_date_in_current_week(employee, payload.target_date)
            return self._build_holiday(employee, payload.target_date)

        if payload.daily_mode == "SINGLE_DAY":
            self._ensure_date_in_current_week(employee, payload.target_date)
            return self._build_single_day(
                employee,
                payload.target_date,
                payload.wanted_hour,
                payload.wanted_meridiem,
            )

        return self._build_multi_day(employee, payload.multi_day_requests)

    def _format_shift(self, hour: int, meridiem: str) -> str:
        return f"{int(hour)}:00 {meridiem.upper()}"

    def _current_week_dates(self, employee) -> list[date_type]:
        week = self.timetable_service.get_current_week_for_employee(employee)
        return [row["date"] for row in week["rows"]]

    def _ensure_date_in_current_week(self, employee, target_date: date_type):
        week_dates = self._current_week_dates(employee)
        if target_date not in week_dates:
            raise ValidationException("Selected date is not in the current timetable week")
        today = datetime.utcnow().date()
        if target_date < today:
            raise ValidationException("Selected date must be today or later")

    def _remaining_days(self, week_dates: list[date_type]) -> int:
        today = datetime.utcnow().date()
        if not week_dates:
            return 0
        week_start, week_end = min(week_dates), max(week_dates)
        if today > week_end:
            return 0
        if today < week_start:
            return len(week_dates)
        return len([d for d in week_dates if d >= today])

    def _collect_matches(self, employee, swap_type: str, target_date: date_type, wanted_shift: str):
        current_shift = self.timetable_service.get_shift_or_raise(employee.id, target_date)
        my_current = {"date": str(target_date), "shift": current_shift}
        my_wanted = {"date": str(target_date), "shift": wanted_shift}
        my_intent = self.swap_repo.create_or_replace_intent(
            employee_pk=employee.id,
            swap_type=swap_type,
            current_payload=my_current,
            wanted_payload=my_wanted,
            target_date=target_date,
            week_start=None,
        )
        candidates = self.swap_repo.list_open_by_scope(swap_type, target_date, None, employee.id)
        matches = [
            c
            for c in candidates
            if is_reciprocal_daily(my_current, my_wanted, c.current_payload, c.wanted_payload)
        ]

        out = []
        for m in matches:
            emp = self.employee_repo.get_by_pk(m.employee_id)
            if emp is None:
                continue
            out.append(
                {
                    "employee_id": emp.employee_id,
                    "contact_number": emp.contact_number,
                    "my_current_payload": my_current,
                    "my_wanted_payload": my_wanted,
                    "other_current_payload": m.current_payload,
                    "other_wanted_payload": m.wanted_payload,
                    "other_intent_id": m.id,
                }
            )

        return my_intent, my_current, my_wanted, out

    def _build_single_day(self, employee, target_date: date_type, wanted_hour: int, wanted_meridiem: str):
        wanted_shift = self._format_shift(wanted_hour, wanted_meridiem)
        my_intent, _, _, matches = self._collect_matches(employee, "DAILY", target_date, wanted_shift)
        self.db.commit()
        return {"my_intent_id": my_intent.id, "matches": matches}

    def _build_holiday(self, employee, target_date: date_type):
        current_shift = self.timetable_service.get_shift_or_raise(employee.id, target_date)
        wanted_shift = "WORKING" if current_shift.upper() == "HOLIDAY" else "HOLIDAY"
        my_intent, _, _, matches = self._collect_matches(employee, "HOLIDAY", target_date, wanted_shift)
        self.db.commit()
        return {"my_intent_id": my_intent.id, "matches": matches}

    def _build_multi_day(self, employee, day_requests):
        week_dates = self._current_week_dates(employee)
        remaining = self._remaining_days(week_dates)
        if len(day_requests) > remaining:
            raise ValidationException(f"Timetable remaining for only {remaining} days")

        groups = []
        for item in day_requests:
            if item.date not in week_dates:
                raise ValidationException("Selected date is not in the current timetable week")
            today = datetime.utcnow().date()
            if item.date < today:
                raise ValidationException("Selected date must be today or later")
            wanted_shift = self._format_shift(item.wanted_hour, item.wanted_meridiem)
            my_intent, my_current, my_wanted, matches = self._collect_matches(
                employee, "DAILY", item.date, wanted_shift
            )
            groups.append(
                {
                    "date": item.date,
                    "my_intent_id": my_intent.id,
                    "my_current_shift": my_current["shift"],
                    "my_wanted_shift": my_wanted["shift"],
                    "matches": matches,
                }
            )

        self.db.commit()
        return {"matches_by_date": groups}
