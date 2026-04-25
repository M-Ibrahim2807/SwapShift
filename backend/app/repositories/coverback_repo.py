from datetime import date

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from app.models.coverback import Coverback


class CoverbackRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Coverback:
        post = Coverback(**kwargs)
        self.db.add(post)
        self.db.flush()
        return post

    def list_open(self, target_date: date | None = None) -> list[Coverback]:
        stmt = select(Coverback).where(Coverback.status == "OPEN")
        if target_date is not None:
            stmt = stmt.where(Coverback.target_date == target_date)
        stmt = stmt.order_by(Coverback.target_date.asc(), Coverback.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_for_employee(self, employee_pk: int) -> list[Coverback]:
        stmt = (
            select(Coverback)
            .where(Coverback.employee_id == employee_pk)
            .order_by(Coverback.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_by_id(self, post_id: int) -> Coverback | None:
        return self.db.scalar(select(Coverback).where(Coverback.id == post_id))

    def has_open_post(self, employee_pk: int, target_date: date, coverback_type: str) -> bool:
        stmt = select(Coverback.id).where(
            and_(
                Coverback.employee_id == employee_pk,
                Coverback.target_date == target_date,
                Coverback.coverback_type == coverback_type,
                Coverback.status == "OPEN",
            )
        )
        return self.db.scalar(stmt) is not None

    def save(self, post: Coverback) -> Coverback:
        self.db.add(post)
        self.db.flush()
        return post

    def delete_all_for_employee(self, employee_pk: int) -> None:
        self.db.execute(delete(Coverback).where(Coverback.employee_id == employee_pk))
        self.db.flush()
