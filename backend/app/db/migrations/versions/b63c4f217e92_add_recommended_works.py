"""add recommended works

Revision ID: b63c4f217e92
Revises: a15e4c982b71
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b63c4f217e92"
down_revision: str | None = "a15e4c982b71"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recommended_works",
        sa.Column(
            "recommended_work_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "work_order_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "comment",
            sa.String(length=2000),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
            name=op.f("fk_recommended_works_work_order_id_work_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_recommended_works"),
        ),
        sa.UniqueConstraint(
            "recommended_work_number",
            name=op.f("uq_recommended_works_recommended_work_number"),
        ),
    )

    op.create_index(
        "ix_recommended_works_work_order_id",
        "recommended_works",
        ["work_order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_recommended_works_work_order_id",
        table_name="recommended_works",
    )

    op.drop_table("recommended_works")
