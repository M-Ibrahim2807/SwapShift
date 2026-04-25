from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.request_repo import RequestRepository
from app.services.timetable_service import TimetableService
from datetime import date as date_type
from datetime import datetime

from app.utils.validators import canonicalize_shift_name


class MatchingEngine:
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = RequestRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.timetable_service = TimetableService(db)

    def build_and_match(self, employee, payload):
        self.timetable_service.ensure_timetable_exists(employee)
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
        if meridiem.upper() == "OFF":
            return "OFF"
        return canonicalize_shift_name(f"{int(hour)}:00 {meridiem.upper()}")

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
        matches = self._collect_slot_candidates(
            requester=employee,
            swap_type=swap_type,
            target_date=target_date,
            requester_current_shift=current_shift,
            wanted_shift=wanted_shift,
        )
        return current_shift, wanted_shift, matches

    def _collect_slot_candidates(
        self,
        requester,
        swap_type: str,
        target_date: date_type,
        requester_current_shift: str,
        wanted_shift: str,
    ) -> list[dict]:
        out = []
        seen_employee_ids = set()

        def matches_wanted_shift(candidate_shift: str) -> bool:
            normalized = canonicalize_shift_name(candidate_shift)
            if wanted_shift == "WORKING":
                return normalized.upper() not in {"OFF", "HOLIDAY"}
            return normalized == wanted_shift

        for row in self.timetable_service.timetable_repo.get_all_shifts_for_date(target_date):
            if row.employee_id == requester.id or row.employee_id in seen_employee_ids:
                continue
            if not matches_wanted_shift(row.shift_name):
                continue

            emp = self.employee_repo.get_by_pk(row.employee_id)
            if emp is None or not emp.is_active:
                continue

            if self.request_repo.has_active_for_employee_on_date(emp.id, target_date):
                continue

            seen_employee_ids.add(emp.id)
            out.append(
                {
                    "employee_id": emp.employee_id,
                    "name": emp.name,
                    "contact_number": emp.contact_number,
                    "target_date": target_date,
                    "swap_type": swap_type,
                    "requester_current_shift": requester_current_shift,
                    "requester_wanted_shift": wanted_shift,
                    "candidate_current_shift": canonicalize_shift_name(row.shift_name),
                }
            )

        return out

    def _build_single_day(self, employee, target_date: date_type, wanted_hour: int, wanted_meridiem: str):
        wanted_shift = self._format_shift(wanted_hour, wanted_meridiem)
        _, _, matches = self._collect_matches(employee, "DAILY", target_date, wanted_shift)
        return {"matches": matches}

    def _build_holiday(self, employee, target_date: date_type):
        current_shift = self.timetable_service.get_shift_or_raise(employee.id, target_date)
        wanted_shift = "WORKING" if current_shift.upper() == "HOLIDAY" else "HOLIDAY"
        _, _, matches = self._collect_matches(employee, "HOLIDAY", target_date, wanted_shift)
        return {"matches": matches}

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
            my_current_shift, my_wanted_shift, matches = self._collect_matches(
                employee, "DAILY", item.date, wanted_shift
            )
            groups.append(
                {
                    "date": item.date,
                    "my_current_shift": my_current_shift,
                    "my_wanted_shift": my_wanted_shift,
                    "matches": matches,
                }
            )

        return {"matches_by_date": groups}
