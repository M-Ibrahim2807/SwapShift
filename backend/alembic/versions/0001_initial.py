"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("contact_number", sa.String(length=30), nullable=False),
        sa.Column("contact_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("registration_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_employees_id", "employees", ["id"])
    op.create_index("ix_employees_employee_id", "employees", ["employee_id"], unique=True)

    op.create_table(
        "swap_intents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("swap_type", sa.String(length=20), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("week_start", sa.Date(), nullable=True),
        sa.Column("current_payload", sa.JSON(), nullable=False),
        sa.Column("wanted_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_swap_intents_employee_id", "swap_intents", ["employee_id"])
    op.create_index("ix_swap_intents_target_date", "swap_intents", ["target_date"])
    op.create_index("ix_swap_intents_week_start", "swap_intents", ["week_start"])

    op.create_table(
        "timetables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("shift_name", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("employee_id", "work_date", name="uq_employee_work_date"),
    )
    op.create_index("ix_timetables_employee_id", "timetables", ["employee_id"])
    op.create_index("ix_timetables_work_date", "timetables", ["work_date"])

    op.create_table(
        "shift_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("receiver_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("requester_intent_id", sa.Integer(), sa.ForeignKey("swap_intents.id"), nullable=False),
        sa.Column("receiver_intent_id", sa.Integer(), sa.ForeignKey("swap_intents.id"), nullable=False),
        sa.Column("swap_type", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_shift_requests_requester_id", "shift_requests", ["requester_id"])
    op.create_index("ix_shift_requests_receiver_id", "shift_requests", ["receiver_id"])
    op.create_index("ix_shift_requests_status", "shift_requests", ["status"])

    op.create_table(
        "swap_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("shift_requests.id"), nullable=False),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("receiver_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("swap_type", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index("ix_swap_history_requester_id", "swap_history", ["requester_id"])
    op.create_index("ix_swap_history_receiver_id", "swap_history", ["receiver_id"])


def downgrade() -> None:
    op.drop_index("ix_swap_history_receiver_id", table_name="swap_history")
    op.drop_index("ix_swap_history_requester_id", table_name="swap_history")
    op.drop_table("swap_history")
    op.drop_index("ix_shift_requests_status", table_name="shift_requests")
    op.drop_index("ix_shift_requests_receiver_id", table_name="shift_requests")
    op.drop_index("ix_shift_requests_requester_id", table_name="shift_requests")
    op.drop_table("shift_requests")
    op.drop_index("ix_timetables_work_date", table_name="timetables")
    op.drop_index("ix_timetables_employee_id", table_name="timetables")
    op.drop_table("timetables")
    op.drop_index("ix_swap_intents_week_start", table_name="swap_intents")
    op.drop_index("ix_swap_intents_target_date", table_name="swap_intents")
    op.drop_index("ix_swap_intents_employee_id", table_name="swap_intents")
    op.drop_table("swap_intents")
    op.drop_index("ix_employees_employee_id", table_name="employees")
    op.drop_index("ix_employees_id", table_name="employees")
    op.drop_table("employees")
