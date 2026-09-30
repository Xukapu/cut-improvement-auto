"""add work orders

Revision ID: d41a8c7b30f2
Revises: c81d3f6a20b4
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d41a8c7b30f2"
down_revision: str | None = "c81d3f6a20b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "work_orders",
        sa.Column(
            "work_order_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "vehicle_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "appointment_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="planned",
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.String(length=2000),
            nullable=False,
        ),
        sa.Column(
            "mileage",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "ready_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
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
        sa.CheckConstraint(
            "status IN ('planned', 'in_progress', 'ready', 'issued')",
            name=op.f("ck_work_orders_status_valid"),
        ),
        sa.CheckConstraint(
            "mileage IS NULL OR mileage >= 0",
            name=op.f("ck_work_orders_mileage_non_negative"),
        ),
        sa.CheckConstraint(
            "(status <> 'issued') OR (issued_at IS NOT NULL)",
            name=op.f("ck_work_orders_issued_requires_date"),
        ),
        sa.ForeignKeyConstraint(
            ["appointment_id"],
            ["appointments.id"],
            name=op.f("fk_work_orders_appointment_id_appointments"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name=op.f("fk_work_orders_client_id_clients"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            name=op.f("fk_work_orders_vehicle_id_vehicles"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_work_orders"),
        ),
        sa.UniqueConstraint(
            "appointment_id",
            name=op.f("uq_work_orders_appointment_id"),
        ),
        sa.UniqueConstraint(
            "work_order_number",
            name=op.f("uq_work_orders_work_order_number"),
        ),
    )

    op.create_index(
        "ix_work_orders_client_id",
        "work_orders",
        ["client_id"],
        unique=False,
    )

    op.create_index(
        "ix_work_orders_vehicle_id",
        "work_orders",
        ["vehicle_id"],
        unique=False,
    )

    op.create_index(
        "ix_work_orders_status",
        "work_orders",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_work_orders_created_at",
        "work_orders",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_work_orders_created_at",
        table_name="work_orders",
    )

    op.drop_index(
        "ix_work_orders_status",
        table_name="work_orders",
    )

    op.drop_index(
        "ix_work_orders_vehicle_id",
        table_name="work_orders",
    )

    op.drop_index(
        "ix_work_orders_client_id",
        table_name="work_orders",
    )

    op.drop_table("work_orders")
