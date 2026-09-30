"""add work order parts

Revision ID: f84c2d731a60
Revises: e73b5a921c44
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f84c2d731a60"
down_revision: str | None = "e73b5a921c44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "parts",
        sa.Column(
            "part_number",
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
            "price",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "supplier",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "provided_by",
            sa.String(length=32),
            nullable=False,
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
        sa.CheckConstraint(
            "price >= 0",
            name=op.f("ck_parts_price_non_negative"),
        ),
        sa.CheckConstraint(
            "provided_by IN ('sto', 'client')",
            name=op.f("ck_parts_provided_by_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
            name=op.f("fk_parts_work_order_id_work_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_parts"),
        ),
        sa.UniqueConstraint(
            "part_number",
            name=op.f("uq_parts_part_number"),
        ),
    )

    op.create_index(
        "ix_parts_work_order_id",
        "parts",
        ["work_order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_parts_work_order_id",
        table_name="parts",
    )

    op.drop_table("parts")
