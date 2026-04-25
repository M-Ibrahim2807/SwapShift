from datetime import date

from tests.conftest import admin_token, build_schedule_workbook, employee_token, register_and_approve_employee


def test_employee_can_offer_coverback_only_on_off_day(client):
    token = admin_token(client)
    workbook = build_schedule_workbook({"EMP301": ["OFF"] * 7}, start_date=date(2026, 4, 25))
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP301", "923001113301")
    emp_token = employee_token(client, "EMP301")

    response = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "OFFER", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["coverback_type"] == "OFFER"
    assert body["employee_shift"] == "OFF"
    assert body["whatsapp_link"].endswith("923001113301")


def test_employee_cannot_offer_coverback_on_working_day(client):
    token = admin_token(client)
    workbook = build_schedule_workbook({"EMP302": ["10:00 AM"] * 7}, start_date=date(2026, 4, 25))
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP302", "923001113302")
    emp_token = employee_token(client, "EMP302")

    response = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "OFFER", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert response.status_code == 400


def test_employee_can_find_coverback_only_on_working_day(client):
    token = admin_token(client)
    workbook = build_schedule_workbook({"EMP303": ["11:00 AM"] * 7}, start_date=date(2026, 4, 25))
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP303", "923001113303")
    emp_token = employee_token(client, "EMP303")

    response = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "FIND", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["coverback_type"] == "FIND"
    assert body["employee_shift"] == "11:00 AM"
    assert body["whatsapp_link"].endswith("923001113303")


def test_coverback_alerts_return_offer_and_find_posts_with_whatsapp_links(client):
    token = admin_token(client)
    workbook = build_schedule_workbook(
        {
            "EMP304": ["OFF"] * 7,
            "EMP305": ["9:00 AM"] * 7,
        },
        start_date=date(2026, 4, 25),
    )
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP304", "923001113304")
    register_and_approve_employee(client, "EMP305", "923001113305")
    offer_token = employee_token(client, "EMP304")
    find_token = employee_token(client, "EMP305")

    offer_post = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "OFFER", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {offer_token}"},
    )
    assert offer_post.status_code == 201

    find_post = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "FIND", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {find_token}"},
    )
    assert find_post.status_code == 201

    alerts = client.get(
        "/api/v1/coverback/alerts?target_date=2026-04-25",
        headers={"Authorization": f"Bearer {offer_token}"},
    )
    assert alerts.status_code == 200
    body = alerts.json()
    assert len(body) == 2
    assert {row["coverback_type"] for row in body} == {"OFFER", "FIND"}
    assert all("https://wa.me/" in row["whatsapp_link"] for row in body)


def test_employee_can_cancel_own_coverback_post(client):
    token = admin_token(client)
    workbook = build_schedule_workbook({"EMP306": ["OFF"] * 7}, start_date=date(2026, 4, 25))
    upload = client.post(
        "/api/v1/admin/timetable/upload",
        files={"file": ("week.csv", workbook, "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    register_and_approve_employee(client, "EMP306", "923001113306")
    emp_token = employee_token(client, "EMP306")

    create_response = client.post(
        "/api/v1/coverback",
        json={"coverback_type": "OFFER", "target_date": "2026-04-25"},
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    cancel_response = client.post(
        f"/api/v1/coverback/{post_id}/cancel",
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
    assert "https://wa.me/" in cancel_response.json()["whatsapp_link"]

    mine_response = client.get(
        "/api/v1/coverback/mine",
        headers={"Authorization": f"Bearer {emp_token}"},
    )
    assert mine_response.status_code == 200
    assert mine_response.json()[0]["status"] == "CANCELLED"
