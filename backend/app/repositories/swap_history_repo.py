from sqlalchemy import delete, or_
from sqlalchemy.orm import Session

from app.models.swap_history import SwapHistory


class SwapHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def delete_all_for_employee(self, employee_pk: int) -> None:
        self.db.execute(
            delete(SwapHistory).where(
                or_(SwapHistory.requester_id == employee_pk, SwapHistory.receiver_id == employee_pk)
            )
        )
        self.db.flush()
