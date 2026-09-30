"""add client number

Revision ID: 8c7d1e5a9b2f
Revises: 4706b728c103
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8c7d1e5a9b2f"
down_revision: str | None = "4706b728c103"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE SEQUENCE client_number_seq
        AS BIGINT
        START WITH 1
        INCREMENT BY 1
        NO CYCLE
        """
    )

    op.add_column(
        "clients",
        sa.Column(
            "client_number",
            sa.BigInteger(),
            server_default=sa.text("nextval('client_number_seq'::regclass)"),
            nullable=False,
        ),
    )

    op.execute(
        """
        ALTER SEQUENCE client_number_seq
        OWNED BY clients.client_number
        """
    )

    op.create_unique_constraint(
        op.f("uq_clients_client_number"),
        "clients",
        ["client_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("uq_clients_client_number"),
        "clients",
        type_="unique",
    )

    op.drop_column(
        "clients",
        "client_number",
    )

    op.execute("DROP SEQUENCE IF EXISTS client_number_seq")
