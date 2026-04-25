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
        files={"file": ("week.csv", workbook, "text/csv")},
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
    matches = emp1_find.json()["matches"]
    assert len(matches) == 1
    candidate = matches[0]
    assert candidate["employee_id"] == "EMP002"
    assert candidate["requester_current_shift"] == "10:00 AM"
    assert candidate["candidate_current_shift"] == "11:00 AM"

    create_request = client.post(
        "/api/v1/swap/request",
        json={
            "receiver_employee_id": candidate["employee_id"],
            "swap_type": "DAILY",
            "target_date": target_date,
            "requester_current_shift": candidate["requester_current_shift"],
            "receiver_current_shift": candidate["candidate_current_shift"],
            "expires_in_minutes": 60,
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert create_request.status_code == 200
    request_id = create_request.json()["id"]

    duplicate_request = client.post(
        "/api/v1/swap/request",
        json={
            "receiver_employee_id": candidate["employee_id"],
            "swap_type": "DAILY",
            "target_date": target_date,
            "requester_current_shift": candidate["requester_current_shift"],
            "receiver_current_shift": candidate["candidate_current_shift"],
            "expires_in_minutes": 60,
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert duplicate_request.status_code == 400

    inbox = client.get("/api/v1/swap/inbox", headers={"Authorization": f"Bearer {emp2_token}"})
    assert inbox.status_code == 200
    assert len(inbox.json()) == 1
    assert inbox.json()[0]["viewer_current_shift"] == "11:00 AM"
    assert inbox.json()[0]["other_person_shift"] == "10:00 AM"

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


def test_daily_swap_matches_even_when_timetable_uses_variant_time_formats(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP001": ["8PM"] * 7,
            "EMP002": ["1 PM"] * 7,
        },
        start_date=date(2026, 4, 21),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001110011")
    register_and_approve_employee(client, "EMP002", "923001110012")
    emp1_token = employee_token(client, "EMP001")
    emp2_token = employee_token(client, "EMP002")

    target_date = "2026-04-21"
    emp1_find = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": target_date,
            "wanted_hour": 1,
            "wanted_meridiem": "PM",
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert emp1_find.status_code == 200
    assert len(emp1_find.json()["matches"]) == 1
    assert emp1_find.json()["matches"][0]["employee_id"] == "EMP002"

    emp2_find = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": target_date,
            "wanted_hour": 8,
            "wanted_meridiem": "PM",
        },
        headers={"Authorization": f"Bearer {emp2_token}"},
    )
    assert emp2_find.status_code == 200
    assert len(emp2_find.json()["matches"]) == 1
    assert emp2_find.json()["matches"][0]["employee_id"] == "EMP001"


def test_find_swap_returns_slot_candidates_and_request_alerts_receiver_without_prior_intent(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP001": ["8:00 PM"] * 7,
            "EMP002": ["1:00 PM"] * 7,
        },
        start_date=date(2026, 4, 21),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001110021")
    register_and_approve_employee(client, "EMP002", "923001110022")
    emp1_token = employee_token(client, "EMP001")
    emp2_token = employee_token(client, "EMP002")

    target_date = "2026-04-21"
    emp1_find = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": target_date,
            "wanted_hour": 1,
            "wanted_meridiem": "PM",
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert emp1_find.status_code == 200
    assert len(emp1_find.json()["matches"]) == 1
    candidate = emp1_find.json()["matches"][0]
    assert candidate["employee_id"] == "EMP002"

    create_request = client.post(
        "/api/v1/swap/request",
        json={
            "receiver_employee_id": candidate["employee_id"],
            "swap_type": "DAILY",
            "target_date": target_date,
            "requester_current_shift": candidate["requester_current_shift"],
            "receiver_current_shift": candidate["candidate_current_shift"],
            "expires_in_minutes": 60,
        },
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert create_request.status_code == 200

    inbox = client.get("/api/v1/swap/inbox", headers={"Authorization": f"Bearer {emp2_token}"})
    assert inbox.status_code == 200
    assert len(inbox.json()) == 1


def test_find_swap_requires_employee_timetable(client):
    register_and_approve_employee(client, "EMP404", "923001114040")
    emp_token = employee_token(client, "EMP404")

    response = client.post(
        "/api/v1/swap/find",
        json={
            "swap_type": "DAILY",
            "daily_mode": "SINGLE_DAY",
            "target_date": "2026-04-24",
            "wanted_hour": 11,
            "wanted_meridiem": "AM",
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert response.status_code == 400
    assert "create your weekly timetable" in response.json()["detail"].lower()


def test_holiday_swap_finds_any_working_candidate(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP001": ["HOLIDAY"] * 7,
            "EMP002": ["9:00 AM"] * 7,
        },
        start_date=date(2026, 4, 24),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001114041")
    register_and_approve_employee(client, "EMP002", "923001114042")
    emp1_token = employee_token(client, "EMP001")

    response = client.post(
        "/api/v1/swap/find",
        json={"swap_type": "HOLIDAY", "target_date": "2026-04-24"},
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["matches"]) == 1
    assert response.json()["matches"][0]["candidate_current_shift"] == "9:00 AM"
