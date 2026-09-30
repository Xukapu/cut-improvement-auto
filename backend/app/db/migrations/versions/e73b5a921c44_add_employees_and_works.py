"""add employees rates and work items

Revision ID: e73b5a921c44
Revises: d41a8c7b30f2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e73b5a921c44"
down_revision: str | None = "d41a8c7b30f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column(
            "employee_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
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
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_employees"),
        ),
        sa.UniqueConstraint(
            "employee_number",
            name=op.f("uq_employees_employee_number"),
        ),
    )

    op.create_table(
        "employee_rates",
        sa.Column(
            "employee_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "rate_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "effective_to",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
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
            "rate_percent >= 0 AND rate_percent <= 100",
            name=op.f("ck_employee_rates_rate_percent_valid"),
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name=op.f("ck_employee_rates_effective_dates_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_employee_rates_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_employee_rates"),
        ),
    )

    op.create_index(
        "ix_employee_rates_employee_id",
        "employee_rates",
        ["employee_id"],
        unique=False,
    )

    op.create_index(
        "uq_employee_rates_current",
        "employee_rates",
        ["employee_id"],
        unique=True,
        postgresql_where=sa.text("effective_to IS NULL"),
    )

    op.create_table(
        "work_items",
        sa.Column(
            "work_item_number",
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
        sa.Column("id", sa.Uuid(), nullable=False),
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
            name=op.f("ck_work_items_price_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
            name=op.f("fk_work_items_work_order_id_work_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_work_items"),
        ),
        sa.UniqueConstraint(
            "work_item_number",
            name=op.f("uq_work_items_work_item_number"),
        ),
    )

    op.create_index(
        "ix_work_items_work_order_id",
        "work_items",
        ["work_order_id"],
        unique=False,
    )

    op.create_table(
        "work_item_assignments",
        sa.Column(
            "work_item_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "employee_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "share_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column(
            "rate_percent_snapshot",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
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
            "share_percent > 0 AND share_percent <= 100",
            name=op.f("ck_work_item_assignments_share_percent_valid"),
        ),
        sa.CheckConstraint(
            "rate_percent_snapshot >= 0 AND rate_percent_snapshot <= 100",
            name=op.f("ck_work_item_assignments_rate_snapshot_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_work_item_assignments_employee_id_employees"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["work_item_id"],
            ["work_items.id"],
            name=op.f("fk_work_item_assignments_work_item_id_work_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_work_item_assignments"),
        ),
        sa.UniqueConstraint(
            "work_item_id",
            "employee_id",
            name=op.f("uq_work_item_assignments_work_item_employee"),
        ),
    )

    op.create_index(
        "ix_work_item_assignments_work_item_id",
        "work_item_assignments",
        ["work_item_id"],
        unique=False,
    )

    op.create_index(
        "ix_work_item_assignments_employee_id",
        "work_item_assignments",
        ["employee_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("work_item_assignments")
    op.drop_table("work_items")
    op.drop_table("employee_rates")
    op.drop_table("employees")
