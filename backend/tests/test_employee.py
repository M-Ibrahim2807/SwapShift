from datetime import date

from tests.conftest import admin_token, build_schedule_workbook


def test_employee_registration_auto_approves_when_employee_id_exists_in_timetable(client):
    upload_token = admin_token(client)
    workbook = build_schedule_workbook({"EMP001": ["SHIFT_A"] * 7}, start_date=date(2026, 3, 20))
    upload_response = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.xlsx", workbook, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"Authorization": f"Bearer {upload_token}"},
    )
    assert upload_response.status_code == 200

    register_response = client.post(
        "/api/v1/employee/register",
        json={"employee_id": "EMP001", "contact_number": "+92-300-1112233", "password": "Pass@1234"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["registration_status"] == "APPROVED"
    assert register_response.json()["is_active"] is True

    login_after_register = client.post(
        "/api/v1/employee/login",
        json={"employee_id": "EMP001", "password": "Pass@1234"},
    )
    assert login_after_register.status_code == 200
    assert "access_token" in login_after_register.json()


def test_employee_registration_is_pending_when_employee_id_not_in_timetable(client):
    register_response = client.post(
        "/api/v1/employee/register",
        json={"employee_id": "EMP999", "contact_number": "+92-300-9999999", "password": "Pass@9999"},
    )
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["registration_status"] == "PENDING"
    assert body["is_active"] is False
    assert "timetable does not exist" in body["message"].lower()

    login_before_approval = client.post(
        "/api/v1/employee/login",
        json={"employee_id": "EMP999", "password": "Pass@9999"},
    )
    assert login_before_approval.status_code == 401
