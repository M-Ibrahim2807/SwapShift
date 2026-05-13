from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.constants import TimetableSource
from app.core.exceptions import ValidationException
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.timetable_repo import TimetableRepository
from app.schemas.timetable_schema import ManualTimetableUpsertIn
from app.utils.validators import canonicalize_shift_name, normalize_shift_name
from app.utils.xls_parser import parse_timetable_xls


class TimetableService:
    MISSING_TIMETABLE_MESSAGE = "No timetable found. Please create your weekly timetable manually."

    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.timetable_repo = TimetableRepository(db)

    def upload_weekly_timetable(self, file_content: bytes) -> dict:
        rows = parse_timetable_xls(file_content)
        unique_dates = sorted({row["date"] for row in rows})
        if len(unique_dates) != 7 or unique_dates[-1] - unique_dates[0] != timedelta(days=6):
            raise ValidationException("Uploaded timetable must contain exactly 7 schedule dates")

        self.timetable_repo.delete_all_by_source(TimetableSource.ADMIN.value)

        inserted_rows = 0
        updated_rows = 0
        employees_created = 0
        skipped_manual_rows = 0

        # Phase 1: Fetch/create employees in batch.
        employee_ids = sorted({row["employee_id"] for row in rows})
        existing_employees = self.employee_repo.get_by_employee_ids(employee_ids)
        employee_by_id = {emp.employee_id: emp for emp in existing_employees}

        missing_payloads: list[dict] = []
        for emp_id in employee_ids:
            if emp_id in employee_by_id:
                continue
            first_row = next((row for row in rows if row["employee_id"] == emp_id), None)
            if first_row is None:
                continue
            missing_payloads.append(
                {
                    "employee_id": emp_id,
                    "name": first_row.get("name") or None,
                    "supervisor_name": first_row.get("supervisor") or None,
                    "contact_number": first_row.get("contact_number") or "PENDING_FROM_TIMETABLE",
                    "contact_hash": "TEMP_UNREGISTERED",
                    "is_active": False,
                    "registration_status": "APPROVED",
                }
            )

        if missing_payloads:
            created = self.employee_repo.bulk_create(missing_payloads)
            for emp in created:
                employee_by_id[emp.employee_id] = emp
            employees_created = len(created)

        # Phase 2: Determine manual-owned employees in one query.
        employee_pks = [emp.id for emp in employee_by_id.values()]
        manual_employee_ids = self.timetable_repo.get_manual_employee_ids(employee_pks)

        # Phase 3: Build insert batch in memory while preserving existing behavior.
        insert_row_by_key: dict[tuple[int, date], dict] = {}
        for row in rows:
            emp = employee_by_id.get(row["employee_id"])
            if emp is None:
                continue

            if emp.id in manual_employee_ids:
                skipped_manual_rows += 1
                continue

            # Preserve old metadata update behavior for existing non-manual employees.
            emp.name = row.get("name") or emp.name
            emp.supervisor_name = row.get("supervisor") or emp.supervisor_name
            self.db.add(emp)

            key = (emp.id, row["date"])
            payload = {
                "employee_id": emp.id,
                "work_date": row["date"],
                "shift_name": normalize_shift_name(row["shift_name"]),
                "source": TimetableSource.ADMIN.value,
            }
            if key in insert_row_by_key:
                updated_rows += 1
            insert_row_by_key[key] = payload

        # Because ADMIN rows are deleted first, all surviving rows are inserts.
        insert_rows = list(insert_row_by_key.values())
        if insert_rows:
            self.timetable_repo.bulk_insert_rows(insert_rows)
            inserted_rows = len(insert_rows)

        self.db.commit()
        return {
            "inserted_rows": inserted_rows,
            "updated_rows": updated_rows,
            "employees_created": employees_created,
            "skipped_manual_rows": skipped_manual_rows,
        }

    def get_current_week_by_employee_id(self, employee_id: str):
        employee = self.employee_repo.get_by_employee_id(employee_id)
        if employee is None:
            raise ValidationException("Employee not found")

        return self.get_current_week_for_employee(employee)

    def get_current_week_for_employee(self, employee):
        rows = self.timetable_repo.get_all_for_employee(employee.id)
        if not rows:
            return self._build_empty_state(employee.employee_id)

        return self._serialize_week(employee.employee_id, rows)

    def upsert_manual_timetable_for_employee(self, employee, payload: ManualTimetableUpsertIn):
        rows = self._validate_manual_rows(payload.rows)
        self.timetable_repo.delete_all_for_employee(employee.id)
        for row in rows:
            self.timetable_repo.upsert_shift(
                employee_pk=employee.id,
                work_date=row.date,
                shift_name=normalize_shift_name(row.shift_name),
                source=TimetableSource.MANUAL.value,
            )
        self.db.commit()
        return self.get_current_week_for_employee(employee)

    def ensure_timetable_exists(self, employee) -> None:
        rows = self.timetable_repo.get_all_for_employee(employee.id)
        if not rows:
            raise ValidationException("Please enter your weekly timetable manually  before using this feature.")

    def get_shift_or_raise(self, employee_pk: int, work_date: date) -> str:
        row = self.timetable_repo.get_shift(employee_pk, work_date)
        if row is None:
            raise ValidationException(f"No shift assigned on date={work_date}")
        return canonicalize_shift_name(row.shift_name)

    def get_available_shifts_for_date(self, employee, work_date: date) -> list[dict]:
        """
        Get all available shift times for a specific date with count of available persons,
        excluding the current employee's shift
        """
        # Get all shifts for this date from all employees and exclude only the current
        # employee's own row. Excluding by shift text can hide valid options when
        # multiple employees share the same shift (for example, several people on 1:00 PM).
        all_shifts_for_date = self.timetable_repo.get_all_shifts_for_date(work_date)

        shift_count = {}
        for row in all_shifts_for_date:
            if row.employee_id == employee.id:
                continue
            shift_name = canonicalize_shift_name(row.shift_name)
            shift_count[shift_name] = shift_count.get(shift_name, 0) + 1

        # Convert to list of dicts with shift name and count, sorted
        shifts_with_count = [
            {"shift": shift, "count": count}
            for shift, count in sorted(shift_count.items())
        ]

        return shifts_with_count

    def get_employee_summary(self, employee):
        """
        Get employee summary with name and shift counts for the current week
        """
        rows = self.timetable_repo.get_all_for_employee(employee.id)
        if not rows:
            raise ValidationException(self.MISSING_TIMETABLE_MESSAGE)
        
        # Count morning, evening, and off shifts
        morning_count = 0
        evening_count = 0
        off_count = 0
        
        for row in rows:
            shift_name = row.shift_name.lower()
            if shift_name == "off" or shift_name == "leave":
                off_count += 1
            elif "morning" in shift_name or "early" in shift_name:
                morning_count += 1
            elif "evening" in shift_name or "night" in shift_name or "late" in shift_name:
                evening_count += 1
        
        return {
            "employee_id": employee.employee_id,
            "name": employee.name or employee.employee_id,
            "morning_shifts": morning_count,
            "evening_shifts": evening_count,
            "off_days": off_count,
        }

    def _build_empty_state(self, employee_id: str) -> dict:
        return {
            "employee_id": employee_id,
            "has_timetable": False,
            "requires_manual_setup": True,
            "week_start": None,
            "week_end": None,
            "rows": [],
            "message": self.MISSING_TIMETABLE_MESSAGE,
        }

    def _serialize_week(self, employee_id: str, rows: list) -> dict:
        ordered_rows = sorted(rows, key=lambda row: row.work_date)
        return {
            "employee_id": employee_id,
            "has_timetable": True,
            "requires_manual_setup": False,
            "week_start": ordered_rows[0].work_date,
            "week_end": ordered_rows[-1].work_date,
            "rows": [
                {"date": row.work_date, "shift_name": row.shift_name, "source": row.source}
                for row in ordered_rows
            ],
            "message": None,
        }

    def _validate_manual_rows(self, rows: list) -> list:
        if len(rows) != 7:
            raise ValidationException("Manual timetable must contain exactly 7 days")

        sorted_rows = sorted(rows, key=lambda row: row.date)
        unique_dates = {row.date for row in sorted_rows}
        if len(unique_dates) != 7:
            raise ValidationException("Manual timetable cannot contain duplicate dates")

        for index in range(1, len(sorted_rows)):
            if sorted_rows[index].date != sorted_rows[index - 1].date + timedelta(days=1):
                raise ValidationException("Manual timetable must contain 7 continuous dates")

        return sorted_rows
