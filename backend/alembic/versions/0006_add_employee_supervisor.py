"""add employee supervisor name"""

from alembic import op
import sqlalchemy as sa


revision = "0006_emp_supervisor"
down_revision = "0005_add_coverbacks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "employees",
        sa.Column("supervisor_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("employees", "supervisor_name")
