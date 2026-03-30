from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.swap import SwapIntent


class SwapRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_replace_intent(
        self,
        employee_pk: int,
        swap_type: str,
        current_payload: dict,
        wanted_payload: dict,
        target_date: date | None,
        week_start: date | None,
    ) -> SwapIntent:
        existing = self.db.scalar(
            select(SwapIntent).where(
                and_(
                    SwapIntent.employee_id == employee_pk,
                    SwapIntent.swap_type == swap_type,
                    SwapIntent.status == "OPEN",
                    SwapIntent.target_date == target_date,
                    SwapIntent.week_start == week_start,
                )
            )
        )
        if existing:
            existing.current_payload = current_payload
            existing.wanted_payload = wanted_payload
            self.db.add(existing)
            self.db.flush()
            return existing

        intent = SwapIntent(
            employee_id=employee_pk,
            swap_type=swap_type,
            target_date=target_date,
            week_start=week_start,
            current_payload=current_payload,
            wanted_payload=wanted_payload,
            status="OPEN",
        )
        self.db.add(intent)
        self.db.flush()
        return intent

    def list_open_by_scope(
        self, swap_type: str, target_date: date | None, week_start: date | None, exclude_employee_pk: int
    ) -> list[SwapIntent]:
        stmt = select(SwapIntent).where(
            and_(
                SwapIntent.swap_type == swap_type,
                SwapIntent.status == "OPEN",
                SwapIntent.target_date == target_date,
                SwapIntent.week_start == week_start,
                SwapIntent.employee_id != exclude_employee_pk,
            )
        )
        return list(self.db.scalars(stmt))

    def get_by_id(self, intent_id: int) -> SwapIntent | None:
        return self.db.scalar(select(SwapIntent).where(SwapIntent.id == intent_id))

    def close_intent(self, intent: SwapIntent) -> None:
        intent.status = "CLOSED"
        self.db.add(intent)
        self.db.flush()
