import csv
import os
from contextlib import asynccontextmanager
from datetime import date, timedelta
from io import StringIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_PATH = Path(__file__).resolve().parent / "test_app.db"

os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["LOG_LEVEL"] = "INFO"

from app.database.base import Base
from app.dependencies import get_db
from app.main import app
from app.models import coverback, employee, shift_request, swap, swap_history, timetable  # noqa: F401

engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def build_schedule_workbook(employee_schedules: dict[str, list[str]], start_date: date) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["generated"])
    writer.writerow(
        [
            "EMP ID",
            "Site",
            "Name",
            "Queue",
            "Supervisor",
            "CT",
            "Batch",
            *[(start_date + timedelta(days=offset)).strftime("%d %b") for offset in range(7)],
        ]
    )

    for employee_id, shifts in employee_schedules.items():
        writer.writerow(
            [
                employee_id,
                "LHE",
                f"Employee {employee_id}",
                "GM Voice",
                "Supervisor",
                "YES",
                "Batch 1",
                *shifts,
            ]
        )

    return buffer.getvalue().encode("utf-8")


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def client():
    @asynccontextmanager
    async def no_op_lifespan(_):
        yield

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = no_op_lifespan
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()


def admin_token(client: TestClient) -> str:
    response = client.post("/api/v1/admin/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def register_and_approve_employee(
    client: TestClient, employee_id: str, contact_number: str, password: str = "Pass@1234"
) -> None:
    response = client.post(
        "/api/v1/employee/register",
        json={"employee_id": employee_id, "contact_number": contact_number, "password": password},
    )
    assert response.status_code == 201
    token = admin_token(client)
    approve = client.post(
        f"/api/v1/admin/registration-requests/{employee_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert approve.status_code == 200


def employee_token(client: TestClient, employee_id: str, password: str = "Pass@1234") -> str:
    response = client.post(
        "/api/v1/employee/login",
        json={"employee_id": employee_id, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
