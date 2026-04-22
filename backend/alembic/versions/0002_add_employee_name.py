"""add employee name column"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_employee_name"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "employees",
        sa.Column("name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("employees", "name")
