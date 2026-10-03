"""create decisions table

Revision ID: 0005
Revises: 0004
Create Date: 2026-01-03 00:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "meeting_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        # A decision always comes from exactly one source. This is the
        # authoritative enforcement of that rule; application code in
        # decision_service also never attempts to violate it, but the
        # database is what actually guarantees it.
        sa.CheckConstraint(
            "(meeting_id IS NOT NULL) <> (document_id IS NOT NULL)",
            name="ck_decisions_exactly_one_source",
        ),
    )
    op.create_index("ix_decisions_owner_id", "decisions", ["owner_id"])
    op.create_index("ix_decisions_meeting_id", "decisions", ["meeting_id"])
    op.create_index("ix_decisions_document_id", "decisions", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_decisions_document_id", table_name="decisions")
    op.drop_index("ix_decisions_meeting_id", table_name="decisions")
    op.drop_index("ix_decisions_owner_id", table_name="decisions")
    op.drop_table("decisions")
