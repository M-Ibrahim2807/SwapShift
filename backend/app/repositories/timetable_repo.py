from datetime import date

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from app.core.constants import TimetableSource
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

    def upsert_shift(
        self,
        employee_pk: int,
        work_date: date,
        shift_name: str,
        source: str,
        preserve_manual: bool = False,
    ) -> tuple[Timetable, str]:
        row = self.get_shift(employee_pk, work_date)
        if row is None:
            row = Timetable(employee_id=employee_pk, work_date=work_date, shift_name=shift_name, source=source)
            self.db.add(row)
            self.db.flush()
            return row, "created"

        if preserve_manual and row.source == TimetableSource.MANUAL.value and source == TimetableSource.ADMIN.value:
            return row, "skipped"

        row.shift_name = shift_name
        row.source = source
        self.db.add(row)
        self.db.flush()
        return row, "updated"

    def delete_all_by_source(self, source: str) -> None:
        self.db.execute(delete(Timetable).where(Timetable.source == source))
        self.db.flush()

    def delete_all_for_employee(self, employee_pk: int) -> None:
        self.db.execute(delete(Timetable).where(Timetable.employee_id == employee_pk))
        self.db.flush()

    def get_all_for_employee(self, employee_pk: int) -> list[Timetable]:
        stmt = (
            select(Timetable)
            .where(Timetable.employee_id == employee_pk)
            .order_by(Timetable.work_date.asc())
        )
        return list(self.db.scalars(stmt))

    def has_rows_with_source(self, employee_pk: int, source: str) -> bool:
        stmt = select(Timetable.id).where(
            and_(Timetable.employee_id == employee_pk, Timetable.source == source)
        )
        return self.db.scalar(stmt) is not None

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
