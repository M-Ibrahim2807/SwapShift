"""add timetable source column"""

from alembic import op
import sqlalchemy as sa


revision = "0003_add_timetable_source"
down_revision = "0002_add_employee_name"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "timetables",
        sa.Column("source", sa.String(length=20), nullable=False, server_default="ADMIN"),
    )


def downgrade() -> None:
    op.drop_column("timetables", "source")
