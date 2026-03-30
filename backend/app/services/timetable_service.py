from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationException
from app.repositories.employee_repo import EmployeeRepository
from app.repositories.timetable_repo import TimetableRepository
from app.utils.validators import normalize_shift_name
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
        return row.shift_name
