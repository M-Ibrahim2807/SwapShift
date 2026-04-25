from datetime import date

from tests.conftest import admin_token, build_schedule_workbook, employee_token, register_and_approve_employee


def test_employee_registration_auto_approves_when_employee_id_exists_in_timetable(client):
    upload_token = admin_token(client)
    workbook = build_schedule_workbook({"EMP001": ["SHIFT_A"] * 7}, start_date=date(2026, 3, 20))
    upload_response = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
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


def test_admin_can_list_all_employees(client):
    register_and_approve_employee(client, "EMP010", "923001110010")
    register_and_approve_employee(client, "EMP011", "923001110011")

    token = admin_token(client)
    response = client.get(
        "/api/v1/admin/employees",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    employee_ids = {row["employee_id"] for row in response.json()}
    assert {"EMP010", "EMP011"}.issubset(employee_ids)


def test_admin_can_deregister_employee_and_remove_database_record(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP020": ["10:00 AM"] * 7,
            "EMP021": ["11:00 AM"] * 7,
        },
        start_date=date(2026, 4, 25),
    )
    upload_response = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload_response.status_code == 200

    register_and_approve_employee(client, "EMP020", "923001110020")
    register_and_approve_employee(client, "EMP021", "923001110021")
    emp020_token = employee_token(client, "EMP020")
    emp021_token = employee_token(client, "EMP021")

    find_response = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": "2026-04-25",
            "wanted_hour": 11,
            "wanted_meridiem": "AM",
        },
        headers={"Authorization": f"Bearer {emp020_token}"},
    )
    assert find_response.status_code == 200
    candidate = find_response.json()["matches"][0]

    request_response = client.post(
        "/api/v1/swap/request",
        json={
            "receiver_employee_id": candidate["employee_id"],
            "swap_type": "DAILY",
            "target_date": "2026-04-25",
            "requester_current_shift": candidate["requester_current_shift"],
            "receiver_current_shift": candidate["candidate_current_shift"],
            "expires_in_minutes": 60,
        },
        headers={"Authorization": f"Bearer {emp020_token}"},
    )
    assert request_response.status_code == 200

    delete_response = client.delete(
        "/api/v1/admin/employees/EMP020",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["employee_id"] == "EMP020"

    login_after_delete = client.post(
        "/api/v1/employee/login",
        json={"employee_id": "EMP020", "password": "Pass@1234"},
    )
    assert login_after_delete.status_code == 401

    list_response = client.get(
        "/api/v1/admin/employees",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    employee_ids = {row["employee_id"] for row in list_response.json()}
    assert "EMP020" not in employee_ids

    inbox_response = client.get(
        "/api/v1/swap/inbox",
        headers={"Authorization": f"Bearer {emp021_token}"},
    )
    assert inbox_response.status_code == 200
    assert inbox_response.json() == []
