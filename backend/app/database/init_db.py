from app.database.base import Base
from app.database.session import engine
from app.models import coverback, employee, shift_request, swap, swap_history, timetable  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
