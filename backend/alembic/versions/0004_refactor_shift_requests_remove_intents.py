"""refactor shift requests to remove intent references"""

from alembic import op
import sqlalchemy as sa


revision = "0004_refactor_shift_requests"
down_revision = "0003_add_timetable_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shift_requests", sa.Column("requester_shift", sa.String(length=20), nullable=True))
    op.add_column("shift_requests", sa.Column("receiver_shift", sa.String(length=20), nullable=True))

    op.execute("UPDATE shift_requests SET requester_shift = 'UNKNOWN' WHERE requester_shift IS NULL")
    op.execute("UPDATE shift_requests SET receiver_shift = 'UNKNOWN' WHERE receiver_shift IS NULL")

    op.alter_column("shift_requests", "requester_shift", nullable=False)
    op.alter_column("shift_requests", "receiver_shift", nullable=False)

    op.execute("""
    ALTER TABLE shift_requests 
    DROP CONSTRAINT IF EXISTS shift_requests_requester_intent_id_fkey;
    """)

    op.execute("""
    ALTER TABLE shift_requests 
    DROP CONSTRAINT IF EXISTS shift_requests_receiver_intent_id_fkey;
    """)
    op.drop_column("shift_requests", "requester_intent_id")
    op.drop_column("shift_requests", "receiver_intent_id")


def downgrade() -> None:
    op.add_column("shift_requests", sa.Column("receiver_intent_id", sa.Integer(), nullable=True))
    op.add_column("shift_requests", sa.Column("requester_intent_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "shift_requests_requester_intent_id_fkey",
        "shift_requests",
        "swap_intents",
        ["requester_intent_id"],
        ["id"],
    )
    op.create_foreign_key(
        "shift_requests_receiver_intent_id_fkey",
        "shift_requests",
        "swap_intents",
        ["receiver_intent_id"],
        ["id"],
    )
    op.drop_column("shift_requests", "receiver_shift")
    op.drop_column("shift_requests", "requester_shift")
