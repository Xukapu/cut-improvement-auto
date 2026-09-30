"""add appointments

Revision ID: c81d3f6a20b4
Revises: b54c7a2e1d90
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c81d3f6a20b4"
down_revision: str | None = "b54c7a2e1d90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column(
            "appointment_number",
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
            "appointment_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "appointment_time",
            sa.Time(),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "comment",
            sa.String(length=2000),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="scheduled",
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
            "status IN ('scheduled', 'no_show')",
            name=op.f("ck_appointments_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name=op.f("fk_appointments_client_id_clients"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            name=op.f("fk_appointments_vehicle_id_vehicles"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_appointments"),
        ),
        sa.UniqueConstraint(
            "appointment_number",
            name=op.f("uq_appointments_appointment_number"),
        ),
    )

    op.create_index(
        "ix_appointments_date_time",
        "appointments",
        ["appointment_date", "appointment_time"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_client_id",
        "appointments",
        ["client_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_vehicle_id",
        "appointments",
        ["vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_appointments_vehicle_id",
        table_name="appointments",
    )

    op.drop_index(
        "ix_appointments_client_id",
        table_name="appointments",
    )

    op.drop_index(
        "ix_appointments_date_time",
        table_name="appointments",
    )

    op.drop_table("appointments")
