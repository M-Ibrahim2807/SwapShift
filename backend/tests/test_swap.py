from datetime import date

from tests.conftest import admin_token, build_schedule_workbook, employee_token, register_and_approve_employee


def test_daily_swap_accepts_and_prevents_duplicate_pending_requests(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP001": ["10:00 AM"] * 7,
            "EMP002": ["11:00 AM"] * 7,
        },
        start_date=date(2026, 3, 20),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.xlsx", workbook, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001110001")
    register_and_approve_employee(client, "EMP002", "923001110002")
    emp1_token = employee_token(client, "EMP001")
    emp2_token = employee_token(client, "EMP002")

    target_date = "2026-03-20"
    emp1_find = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": target_date,
            "wanted_hour": 11,
            "wanted_meridiem": "AM",
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert emp1_find.status_code == 200
    my_intent_id = emp1_find.json()["my_intent_id"]

    emp2_find = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": target_date,
            "wanted_hour": 10,
            "wanted_meridiem": "AM",
        },
        headers={"Authorization": f"Bearer {emp2_token}"},
    )
    assert emp2_find.status_code == 200
    other_intent_id = emp2_find.json()["my_intent_id"]

    create_request = client.post(
        "/api/v1/swap/request",
        json={"my_intent_id": my_intent_id, "other_intent_id": other_intent_id, "expires_in_minutes": 60},
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert create_request.status_code == 200
    request_id = create_request.json()["id"]

    duplicate_request = client.post(
        "/api/v1/swap/request",
        json={"my_intent_id": my_intent_id, "other_intent_id": other_intent_id, "expires_in_minutes": 60},
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert duplicate_request.status_code == 400

    inbox = client.get("/api/v1/swap/inbox", headers={"Authorization": f"Bearer {emp2_token}"})
    assert inbox.status_code == 200
    assert len(inbox.json()) == 1

    accept = client.post(
        f"/api/v1/swap/requests/{request_id}/decision",
        json={"decision": "ACCEPT"},
        headers={"Authorization": f"Bearer {emp2_token}"},
    )
    assert accept.status_code == 200
    assert accept.json()["status"] == "ACCEPTED"

    emp1_timetable = client.get("/api/v1/employee/timetable", headers={"Authorization": f"Bearer {emp1_token}"})
    emp2_timetable = client.get("/api/v1/employee/timetable", headers={"Authorization": f"Bearer {emp2_token}"})
    assert emp1_timetable.status_code == 200
    assert emp2_timetable.status_code == 200

    emp1_day = next(row for row in emp1_timetable.json()["rows"] if row["date"] == target_date)
    emp2_day = next(row for row in emp2_timetable.json()["rows"] if row["date"] == target_date)
    assert emp1_day["shift_name"] == "11:00 AM"
    assert emp2_day["shift_name"] == "10:00 AM"
