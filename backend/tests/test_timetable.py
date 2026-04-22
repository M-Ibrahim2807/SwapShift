from datetime import date

from tests.conftest import admin_token, build_schedule_workbook, employee_token, register_and_approve_employee


def test_timetable_upload_replaces_previous_week_and_returns_current_week(client):
    token = admin_token(client)
    week_one = build_schedule_workbook({"EMP001": ["SHIFT_A"] * 7}, start_date=date(2026, 3, 20))
    upload_one = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week1.xlsx", week_one, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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
        files={"file": ("week2.xlsx", week_two, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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
        files={"file": ("week.csv", workbook, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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
