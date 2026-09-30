"""add audit log

Revision ID: e9c1a7b4d2f6
Revises: d7a4c1e8b2f0
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e9c1a7b4d2f6"
down_revision: str | None = "d7a4c1e8b2f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column(
            "event_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "actor_login",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "actor_role",
            sa.String(length=32),
            nullable=True,
        ),
        sa.Column(
            "action",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "entity_type",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "entity_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "entity_number",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "old_values",
            postgresql.JSONB(
                astext_type=sa.Text(),
            ),
            nullable=True,
        ),
        sa.Column(
            "new_values",
            postgresql.JSONB(
                astext_type=sa.Text(),
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["app_users.id"],
            name=op.f("fk_audit_logs_actor_user_id_app_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_audit_logs"),
        ),
        sa.UniqueConstraint(
            "event_number",
            name=op.f("uq_audit_logs_event_number"),
        ),
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ix_audit_logs_actor_user_id",
        "audit_logs",
        ["actor_user_id"],
        unique=False,
    )

    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        [
            "entity_type",
            "entity_number",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_audit_logs_entity",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_actor_user_id",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs",
    )

    op.drop_table("audit_logs")
