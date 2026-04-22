from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.timetable_repo import TimetableRepository
from app.utils.validators import canonicalize_shift_name, normalize_shift_name
from app.utils.xls_parser import parse_timetable_xls


class TimetableService:
    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
        self.timetable_repo = TimetableRepository(db)

    def upload_weekly_timetable(self, file_content: bytes) -> dict:
        rows = parse_timetable_xls(file_content)
        unique_dates = sorted({row["date"] for row in rows})
        if len(unique_dates) != 7:
            raise ValidationException("Uploaded timetable must contain exactly 7 schedule dates")

        self.timetable_repo.delete_all()

        inserted_rows = 0
        employees_created = 0

        for row in rows:
            emp = self.employee_repo.get_by_employee_id(row["employee_id"])
            if emp is None:
                emp = self.employee_repo.create(
                    employee_id=row["employee_id"],
                    name=row.get("name") or None,
                    contact_number=row["contact_number"] or "PENDING_FROM_TIMETABLE",
                    contact_hash="TEMP_UNREGISTERED",
                )
                employees_created += 1

            _, created = self.timetable_repo.upsert_shift(
                employee_pk=emp.id,
                work_date=row["date"],
                shift_name=normalize_shift_name(row["shift_name"]),
            )
            if created:
                inserted_rows += 1

        self.db.commit()
        return {
            "inserted_rows": inserted_rows,
            "updated_rows": 0,
            "employees_created": employees_created,
        }

    def get_current_week_by_employee_id(self, employee_id: str):
        employee = self.employee_repo.get_by_employee_id(employee_id)
        if employee is None:
            raise ValidationException("Employee not found")

        rows = self.timetable_repo.get_all_for_employee(employee.id)
        if not rows:
            raise ValidationException("No current timetable found for employee")

        return {
            "employee_id": employee.employee_id,
            "week_start": rows[0].work_date,
            "week_end": rows[-1].work_date,
            "rows": [{"date": r.work_date, "shift_name": r.shift_name} for r in rows],
        }

    def get_current_week_for_employee(self, employee):
        rows = self.timetable_repo.get_all_for_employee(employee.id)
        if not rows:
            raise ValidationException("No current timetable found for employee")

        return {
            "employee_id": employee.employee_id,
            "week_start": rows[0].work_date,
            "week_end": rows[-1].work_date,
            "rows": [{"date": r.work_date, "shift_name": r.shift_name} for r in rows],
        }

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
            raise ValidationException("No current timetable found for employee")
        
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
