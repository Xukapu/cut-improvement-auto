"""add part quantity

Revision ID: a15e4c982b71
Revises: f84c2d731a60
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a15e4c982b71"
down_revision: str | None = "f84c2d731a60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "parts",
        sa.Column(
            "quantity",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
    )

    op.create_check_constraint(
        op.f("ck_parts_quantity_positive"),
        "parts",
        "quantity > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_parts_quantity_positive"),
        "parts",
        type_="check",
    )

    op.drop_column(
        "parts",
        "quantity",
    )
