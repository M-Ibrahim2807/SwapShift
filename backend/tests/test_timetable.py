from datetime import date

from tests.conftest import admin_token, build_schedule_workbook, employee_token, register_and_approve_employee


def test_timetable_upload_replaces_previous_week_and_returns_current_week(client):
    token = admin_token(client)
    week_one = build_schedule_workbook({"EMP001": ["SHIFT_A"] * 7}, start_date=date(2026, 3, 20))
    upload_one = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week1.csv", week_one, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload_one.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001112233")
    employee_auth = employee_token(client, "EMP001")

    first_timetable = client.get(
        "/api/v1/employee/timetable",
        headers={"Authorization": f"Bearer {employee_auth}"},
    )
    assert first_timetable.status_code == 200
    assert len(first_timetable.json()["rows"]) == 7
    assert first_timetable.json()["week_start"] == "2026-03-20"

    week_two = build_schedule_workbook({"EMP001": ["SHIFT_B"] * 7}, start_date=date(2026, 3, 27))
    upload_two = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week2.csv", week_two, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload_two.status_code == 200

    second_timetable = client.get(
        "/api/v1/employee/timetable",
        headers={"Authorization": f"Bearer {employee_auth}"},
    )
    assert second_timetable.status_code == 200
    assert second_timetable.json()["week_start"] == "2026-03-27"
    assert second_timetable.json()["week_end"] == "2026-04-02"
    assert {row["shift_name"] for row in second_timetable.json()["rows"]} == {"SHIFT_B"}


def test_available_shifts_keeps_same_shift_if_other_employees_also_have_it(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP001": ["1:00 PM"] * 7,
            "EMP002": ["1:00 PM"] * 7,
            "EMP003": ["2:00 PM"] * 7,
        },
        start_date=date(2026, 4, 21),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP001", "923001110101")
    emp1_token = employee_token(client, "EMP001")

    response = client.get(
        "/api/v1/employee/timetable/available-shifts/2026-04-21",
        headers={"Authorization": f"Bearer {emp1_token}"},
    )
    assert response.status_code == 200

    shifts = {item["shift"]: item["count"] for item in response.json()["shifts"]}
    assert shifts["1:00 PM"] == 1
    assert shifts["2:00 PM"] == 1


def test_employee_without_timetable_gets_manual_setup_state(client):
    register_and_approve_employee(client, "EMP999", "923001110999")
    emp_token = employee_token(client, "EMP999")

    response = client.get(
        "/api/v1/employee/timetable",
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["has_timetable"] is False
    assert body["requires_manual_setup"] is True
    assert body["rows"] == []


def test_employee_can_create_and_edit_manual_timetable(client):
    register_and_approve_employee(client, "EMP777", "923001117777")
    emp_token = employee_token(client, "EMP777")

    create_response = client.put(
        "/api/v1/employee/timetable",
        json={
            "rows": [
                {"date": "2026-04-24", "shift_name": "9 AM"},
                {"date": "2026-04-25", "shift_name": "10 AM"},
                {"date": "2026-04-26", "shift_name": "OFF"},
                {"date": "2026-04-27", "shift_name": "11 AM"},
                {"date": "2026-04-28", "shift_name": "1 PM"},
                {"date": "2026-04-29", "shift_name": "2 PM"},
                {"date": "2026-04-30", "shift_name": "3 PM"},
            ]
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert create_response.status_code == 200
    create_body = create_response.json()
    assert create_body["has_timetable"] is True
    assert create_body["week_start"] == "2026-04-24"
    assert {row["source"] for row in create_body["rows"]} == {"MANUAL"}

    edit_response = client.put(
        "/api/v1/employee/timetable",
        json={
            "rows": [
                {"date": "2026-04-24", "shift_name": "8 PM"},
                {"date": "2026-04-25", "shift_name": "8 PM"},
                {"date": "2026-04-26", "shift_name": "OFF"},
                {"date": "2026-04-27", "shift_name": "8 PM"},
                {"date": "2026-04-28", "shift_name": "8 PM"},
                {"date": "2026-04-29", "shift_name": "8 PM"},
                {"date": "2026-04-30", "shift_name": "8 PM"},
            ]
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert edit_response.status_code == 200
    rows = edit_response.json()["rows"]
    assert rows[0]["shift_name"] == "8:00 PM"


def test_manual_timetable_rejects_non_week_payloads(client):
    register_and_approve_employee(client, "EMP778", "923001117778")
    emp_token = employee_token(client, "EMP778")

    too_short = client.put(
        "/api/v1/employee/timetable",
        json={
            "rows": [
                {"date": "2026-04-24", "shift_name": "9 AM"},
                {"date": "2026-04-25", "shift_name": "10 AM"},
                {"date": "2026-04-26", "shift_name": "OFF"},
                {"date": "2026-04-27", "shift_name": "11 AM"},
                {"date": "2026-04-28", "shift_name": "1 PM"},
                {"date": "2026-04-29", "shift_name": "2 PM"},
            ]
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert too_short.status_code == 400

    duplicate_dates = client.put(
        "/api/v1/employee/timetable",
        json={
            "rows": [
                {"date": "2026-04-24", "shift_name": "9 AM"},
                {"date": "2026-04-24", "shift_name": "10 AM"},
                {"date": "2026-04-26", "shift_name": "OFF"},
                {"date": "2026-04-27", "shift_name": "11 AM"},
                {"date": "2026-04-28", "shift_name": "1 PM"},
                {"date": "2026-04-29", "shift_name": "2 PM"},
                {"date": "2026-04-30", "shift_name": "3 PM"},
            ]
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert duplicate_dates.status_code == 400


def test_admin_upload_preserves_manual_timetable_rows(client):
    register_and_approve_employee(client, "EMP888", "923001118888")
    emp_token = employee_token(client, "EMP888")

    manual_response = client.put(
        "/api/v1/employee/timetable",
        json={
            "rows": [
                {"date": "2026-04-24", "shift_name": "9 AM"},
                {"date": "2026-04-25", "shift_name": "10 AM"},
                {"date": "2026-04-26", "shift_name": "OFF"},
                {"date": "2026-04-27", "shift_name": "11 AM"},
                {"date": "2026-04-28", "shift_name": "1 PM"},
                {"date": "2026-04-29", "shift_name": "2 PM"},
                {"date": "2026-04-30", "shift_name": "3 PM"},
            ]
        },
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert manual_response.status_code == 200

    token = admin_token(client)
    week_csv = build_schedule_workbook({"EMP888": ["SHIFT_A"] * 7}, start_date=date(2026, 4, 24))
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", week_csv, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200
    assert upload.json()["skipped_manual_rows"] == 7

    timetable = client.get(
        "/api/v1/employee/timetable",
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert timetable.status_code == 200
    assert {row["source"] for row in timetable.json()["rows"]} == {"MANUAL"}
