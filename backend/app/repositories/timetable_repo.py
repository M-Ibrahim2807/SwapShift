from datetime import date

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from app.models.timetable import Timetable


class TimetableRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_shift(self, employee_pk: int, work_date: date) -> Timetable | None:
        return self.db.scalar(
            select(Timetable).where(
                and_(Timetable.employee_id == employee_pk, Timetable.work_date == work_date)
            )
        )

    def upsert_shift(self, employee_pk: int, work_date: date, shift_name: str) -> tuple[Timetable, bool]:
        row = self.get_shift(employee_pk, work_date)
        created = False
        if row is None:
            row = Timetable(employee_id=employee_pk, work_date=work_date, shift_name=shift_name)
            self.db.add(row)
            created = True
        else:
            row.shift_name = shift_name
            self.db.add(row)
        self.db.flush()
        return row, created

    def delete_all(self) -> None:
        self.db.execute(delete(Timetable))
        self.db.flush()

    def get_all_for_employee(self, employee_pk: int) -> list[Timetable]:
        stmt = (
            select(Timetable)
            .where(Timetable.employee_id == employee_pk)
            .order_by(Timetable.work_date.asc())
        )
        return list(self.db.scalars(stmt))

    def get_range(self, employee_pk: int, start_date: date, end_date: date) -> list[Timetable]:
        stmt = (
            select(Timetable)
            .where(
                and_(
                    Timetable.employee_id == employee_pk,
                    Timetable.work_date >= start_date,
                    Timetable.work_date <= end_date,
                )
            )
            .order_by(Timetable.work_date.asc())
        )
        return list(self.db.scalars(stmt))

    def get_all_shifts_for_date(self, work_date: date) -> list[Timetable]:
        """Get all timetable rows for a specific date across all employees."""
        stmt = select(Timetable).where(Timetable.work_date == work_date)
        return list(self.db.scalars(stmt))
