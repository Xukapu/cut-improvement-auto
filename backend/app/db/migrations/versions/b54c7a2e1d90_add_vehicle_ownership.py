"""add vehicle numbering and ownership integrity

Revision ID: b54c7a2e1d90
Revises: 9f2a6c1d4e70
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b54c7a2e1d90"
down_revision: str | None = "9f2a6c1d4e70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "vehicles",
        sa.Column(
            "vehicle_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
    )

    op.create_unique_constraint(
        op.f("uq_vehicles_vehicle_number"),
        "vehicles",
        ["vehicle_number"],
    )

    op.create_check_constraint(
        op.f("ck_vehicles_year_valid"),
        "vehicles",
        "year IS NULL OR year BETWEEN 1886 AND 2100",
    )

    op.execute(
        """
        UPDATE client_vehicles
        SET started_at = COALESCE(
            started_at,
            created_at::date,
            CURRENT_DATE
        )
        """
    )

    op.alter_column(
        "client_vehicles",
        "started_at",
        existing_type=sa.Date(),
        nullable=False,
        server_default=sa.text("CURRENT_DATE"),
    )

    op.create_check_constraint(
        op.f("ck_client_vehicles_ownership_state_valid"),
        "client_vehicles",
        (
            "("
            "is_current = true AND ended_at IS NULL"
            ") OR ("
            "is_current = false AND ended_at IS NOT NULL"
            ")"
        ),
    )

    op.create_index(
        "ix_client_vehicles_client_current",
        "client_vehicles",
        ["client_id", "is_current"],
        unique=False,
    )

    op.create_index(
        "uq_client_vehicles_one_current_owner",
        "client_vehicles",
        ["vehicle_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true AND deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_client_vehicles_one_current_owner",
        table_name="client_vehicles",
    )

    op.drop_index(
        "ix_client_vehicles_client_current",
        table_name="client_vehicles",
    )

    op.drop_constraint(
        op.f("ck_client_vehicles_ownership_state_valid"),
        "client_vehicles",
        type_="check",
    )

    op.alter_column(
        "client_vehicles",
        "started_at",
        existing_type=sa.Date(),
        nullable=True,
        server_default=None,
    )

    op.drop_constraint(
        op.f("ck_vehicles_year_valid"),
        "vehicles",
        type_="check",
    )

    op.drop_constraint(
        op.f("uq_vehicles_vehicle_number"),
        "vehicles",
        type_="unique",
    )

    op.drop_column(
        "vehicles",
        "vehicle_number",
    )
