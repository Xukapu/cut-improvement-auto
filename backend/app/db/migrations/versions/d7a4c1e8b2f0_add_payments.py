"""add payments

Revision ID: d7a4c1e8b2f0
Revises: c92e8f4d1a35
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d7a4c1e8b2f0"
down_revision: str | None = "c92e8f4d1a35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column(
            "payment_number",
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
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "method",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "comment",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "paid_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
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
            "amount > 0",
            name=op.f("ck_payments_amount_positive"),
        ),
        sa.CheckConstraint(
            "method IN ('cash', 'card', 'transfer')",
            name=op.f("ck_payments_method_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
            name=op.f("fk_payments_work_order_id_work_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_payments"),
        ),
        sa.UniqueConstraint(
            "payment_number",
            name=op.f("uq_payments_payment_number"),
        ),
    )

    op.create_index(
        "ix_payments_work_order_id",
        "payments",
        ["work_order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payments_work_order_id",
        table_name="payments",
    )

    op.drop_table("payments")
