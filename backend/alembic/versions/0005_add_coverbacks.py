"""add coverbacks table"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_coverbacks"
down_revision = "0004_refactor_shift_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coverbacks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employees.id"), nullable=False),
        sa.Column("coverback_type", sa.String(length=20), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("employee_shift", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_coverbacks_employee_id", "coverbacks", ["employee_id"])
    op.create_index("ix_coverbacks_coverback_type", "coverbacks", ["coverback_type"])
    op.create_index("ix_coverbacks_target_date", "coverbacks", ["target_date"])
    op.create_index("ix_coverbacks_status", "coverbacks", ["status"])


def downgrade() -> None:
    op.drop_index("ix_coverbacks_status", table_name="coverbacks")
    op.drop_index("ix_coverbacks_target_date", table_name="coverbacks")
    op.drop_index("ix_coverbacks_coverback_type", table_name="coverbacks")
    op.drop_index("ix_coverbacks_employee_id", table_name="coverbacks")
    op.drop_table("coverbacks")
