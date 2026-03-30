# SwapShift Backend (FastAPI + PostgreSQL)

This backend now follows layered architecture:

- `api/` = routes/controllers (HTTP input-output)
- `schemas/` = request/response shapes (Pydantic)
- `services/` = business logic and use-case flow
- `repositories/` = database query layer
- `models/` = SQLAlchemy tables
- `database/` = connection + init
- `utils/` = helper functions (XLS parsing, matching, WhatsApp link)

---

## 1. Setup Commands (Run In Terminal)

### 1.1 Go to backend
```bash
cd /home/muhammad-ibrahim/Documents/SwapShift/backend
```

### 1.2 Create/activate virtual env (if not already)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Create PostgreSQL database
```bash
sudo -u postgres psql -c "CREATE DATABASE swapshift;"
```

### 1.5 Check `.env`
Use existing `.env` in backend root:

- `DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/swapshift`
- `ADMIN_API_KEY=swapshift-admin-key`

If your postgres password/user is different, update `DATABASE_URL`.

### 1.6 Run app
```bash
uvicorn app.main:app --reload
```

Swagger docs:
- `http://127.0.0.1:8000/docs`

Health endpoint:
- `GET http://127.0.0.1:8000/health`

---

## 2. High-Level Workflow (Layered)

For each feature:

1. Route in `api/...` receives request.
2. Validates request with `schemas/...`.
3. Calls `services/...` (business rules).
4. Service calls `repositories/...` (DB ops).
5. Repository reads/writes `models/...` tables.
6. Service returns response DTO.

This keeps code clean and beginner-friendly.

---

## 3. Database Tables Implemented

- `employees` (`models/employee.py`)
- `timetables` (`models/timetable.py`)
- `swap_intents` (`models/swap.py`) for find-swap intents
- `shift_requests` (`models/shift_request.py`) for pending/accepted/rejected requests
- `swap_history` (`models/swap_history.py`) for completed swaps

Tables are auto-created on startup via `database/init_db.py`.

---

## 4. Use Case Implementation Guide (UC-01 to UC-10)

## UC-01 Employee Registration

### Route
- `POST /api/v1/employee/register`
- File: `app/api/employee/register.py`

### Schema
- Request: `RegisterIn` (`schemas/employee_schema.py`)
- Response: `RegisterOut`

### Service Flow
- File: `services/employee_service.py`
1. Validate contact number.
2. Check if employee exists in DB.
3. If new: create pending employee.
4. If approved by admin already: activate immediately.
5. Commit.

### Repository
- `EmployeeRepository` in `repositories/employee_repo.py`

### Alternate Flow (Admin approval)
- `GET /api/v1/admin/registration-requests`
- `POST /api/v1/admin/registration-requests/{employee_id}/approve`
- `POST /api/v1/admin/registration-requests/{employee_id}/reject`
- Admin key required via header: `x-admin-key`.

---

## UC-02 Employee Login

### Route
- `POST /api/v1/employee/login`
- File: `app/api/employee/login.py`

### Service
- `services/auth_service.py`
1. Fetch employee by `employee_id`.
2. Ensure `is_active=True`.
3. Verify contact number hash.
4. Return JWT access token.

### Security
- JWT helpers in `core/security.py`.
- Protected routes use `dependencies.get_current_employee`.

---

## UC-03 Upload Weekly Timetable (Admin)

### Route
- `POST /api/v1/admin/timetable/upload`
- File: `app/api/admin/upload_timetable.py`

### Service
- `services/timetable_service.py`
1. Parse XLS via `utils/xls_parser.py`.
2. Validate required columns:
   - `employee_id`
   - `contact_number`
   - `date`
   - `shift_name`
3. Upsert timetable rows.
4. Auto-create employee rows from XLS if missing.

### XLS Format Example
Use these exact headers:

| employee_id | contact_number | date       | shift_name |
|-------------|----------------|------------|------------|
| EMP001      | 923001112233   | 2026-03-16 | MORNING    |
| EMP001      | 923001112233   | 2026-03-17 | EVENING    |
| EMP002      | 923009998887   | 2026-03-16 | HOLIDAY    |

---

## UC-04 View Weekly Timetable

### Route
- `GET /api/v1/employee/timetable?week_start=YYYY-MM-DD`
- File: `app/api/employee/timetable.py`

### Service
- `services/timetable_service.py`
1. Compute `week_end = week_start + 6 days`.
2. Query employee timetable for date range.
3. Return Mon-Sun rows.

---

## UC-05 Find Swap (Reciprocal Match Engine)

### Route
- `POST /api/v1/swap/find`
- File: `app/api/swap/find_swap.py`

### Request Schema
- `FindSwapIn` (`schemas/swap_schema.py`)
- Supports `DAILY`, `WEEKLY`, `HOLIDAY`.

### Service / Engine Flow
- `services/matching_engine.py`
1. Detect current shift from timetable.
2. Build employee swap intent (`swap_intents`).
3. Find other open intents in same scope/date.
4. Reciprocal check:
   - Daily/Holiday via `utils/shift_matcher.is_reciprocal_daily`
   - Weekly via `utils/shift_matcher.is_reciprocal_weekly`
5. Return compatible candidates.

### Reciprocal Rule Implemented
- `other.current == my.wanted`
- `other.wanted == my.current`

For weekly: checked across all 7 days.

---

## UC-06 Swap Daily Shift

Handled by `swap_type="DAILY"` in `/swap/find` and then `/swap/request`.

Flow:
1. Find reciprocal candidates.
2. Send request.
3. Receiver accepts.
4. Atomic shift exchange for that date.

---

## UC-07 Swap Whole Week

Handled by `swap_type="WEEKLY"` with `wanted_week_shifts` containing 7 day mappings.

Engine verifies reciprocal mapping day-by-day.

On accept, service swaps all 7 timetable entries in one transaction.

---

## UC-08 Swap Holiday

Handled by `swap_type="HOLIDAY"`.

Validation naturally comes from reciprocal rule + timetable values (Holiday vs Working shift).

---

## UC-09 Accept / Reject Swap

### Routes
- Send request: `POST /api/v1/swap/request` (`api/swap/request_swap.py`)
- Decision: `POST /api/v1/swap/requests/{request_id}/decision` (`api/swap/accept_reject_swap.py`)

### Service
- `services/swap_service.py`

Decision flow:
1. Ensure receiver is current user.
2. Ensure request status is pending and not expired.
3. Reject path: mark REJECTED.
4. Accept path:
   - Swap timetable rows atomically.
   - Mark request ACCEPTED.
   - Close both intents.
   - Insert `swap_history` record.

---

## UC-10 WhatsApp Redirect

On successful accept, response returns:

- `requester_whatsapp`
- `receiver_whatsapp`

Generated by `utils/whatsapp_redirect.py` as:

- `https://wa.me/<contact_number>`

Your frontend can open this URL directly.

---

## 5. API Testing Order (Important)

Use this exact order in Postman/Swagger:

1. Upload timetable as admin.
2. Register Employee A.
3. Register Employee B.
4. Approve both registrations as admin.
5. Login both, save tokens.
6. Employee A calls `/swap/find`.
7. Employee B calls `/swap/find` with reciprocal wanted shift.
8. Employee A calls `/swap/request`.
9. Employee B checks `/swap/inbox`.
10. Employee B decides `ACCEPT`.
11. Verify `/employee/timetable` and `/swap/history`.

---

## 6. Important Files You Should Study First

1. `app/main.py`
2. `app/api/router.py`
3. `app/dependencies.py`
4. `app/services/employee_service.py`
5. `app/services/timetable_service.py`
6. `app/services/matching_engine.py`
7. `app/services/swap_service.py`

If you understand these 7 files, you will understand the full workflow.

---

## 7. Next Best-Practice Improvements

1. Add Alembic migrations (instead of create_all).
2. Add role-based auth for admin (instead of static header key).
3. Add background queue for notifications.
4. Add expiry scheduler for pending requests.
5. Add integration tests with test database.

