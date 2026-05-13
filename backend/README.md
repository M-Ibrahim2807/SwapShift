# SwapShift Backend

FastAPI backend for registration, timetable management, swaps, and coverback posting.

## Stack
- FastAPI
- SQLAlchemy ORM
- Alembic
- Pydantic
- JWT auth (`python-jose`)

## Project Layers
- `app/api` HTTP routes
- `app/schemas` request/response models
- `app/services` business logic
- `app/repositories` data-access layer
- `app/models` DB models
- `app/database` session/base/init
- `app/utils` helpers (CSV parser, validators, matching, WhatsApp links)

## Run Locally
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs:
- `http://127.0.0.1:8000/docs`

Health:
- `GET /health`

## Auth Model
- Employee login: `POST /api/v1/employee/login`
- Admin login: `POST /api/v1/admin/login`
- Protected routes use Bearer JWT with role checks:
  - employee routes require role `employee`
  - admin routes require role `admin`

## Current API Surface

### Employee
- `POST /api/v1/employee/register`
- `POST /api/v1/employee/login`
- `GET /api/v1/employee/timetable`
- `PUT /api/v1/employee/timetable` (manual timetable upsert)
- `GET /api/v1/employee/timetable/available-shifts/{work_date}`
- `GET /api/v1/employee/summary`

### Admin
- `POST /api/v1/admin/login`
- `POST /api/v1/admin/timetable/upload` (CSV only)
- `GET /api/v1/admin/registration-requests`
- `POST /api/v1/admin/registration-requests/{employee_id}/approve`
- `POST /api/v1/admin/registration-requests/{employee_id}/reject`
- `GET /api/v1/admin/employees`
- `DELETE /api/v1/admin/employees/{employee_id}`

### Swap
- `POST /api/v1/swap/find`
- `POST /api/v1/swap/request`
- `POST /api/v1/swap/requests/{request_id}/decision`
- `GET /api/v1/swap/history`
- `GET /api/v1/swap/inbox`

### Coverback
- `POST /api/v1/coverback`
- `GET /api/v1/coverback/alerts`
- `GET /api/v1/coverback/mine`
- `POST /api/v1/coverback/{post_id}/cancel`

## Timetable Behavior (Current)
- Admin upload replaces only `ADMIN`-source timetable rows.
- Employees can have timetable rows with source:
  - `ADMIN`
  - `MANUAL`
- If an employee has no timetable rows, `/employee/timetable` returns:
  - `has_timetable = false`
  - `requires_manual_setup = true`
  - empty rows with an actionable message
- Employee `PUT /employee/timetable` requires exactly:
  - 7 rows
  - unique dates
  - continuous 7-day range

## Registration Behavior (Current)
- If employee ID is not in DB: registration creates pending account.
- If employee ID already exists (typically seeded by timetable upload):
  - registration updates password/contact
  - account is marked approved/active.

## Swap Behavior (Current)
- Supported types: `DAILY`, `HOLIDAY`.
- Matching is driven by current timetable shifts.
- Creating a request validates both shifts have not changed.
- Request decision:
  - `REJECT` closes request
  - `ACCEPT` swaps both employees’ shifts for the target date and writes swap history.

## Coverback Behavior (Current)
- Employee can create coverback posts for a target date.
- Alerts endpoint lists open posts (optional date filter).
- Employee can list own posts and cancel own post.

## Notes
- Pending swap requests are auto-expired by a background cleanup job.
- Alembic config and migrations exist under `backend/alembic`.
- Tests are available under `backend/tests`.
