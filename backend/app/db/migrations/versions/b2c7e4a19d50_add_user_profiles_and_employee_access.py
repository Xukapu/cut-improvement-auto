"""add user profiles and employee access

Revision ID: b2c7e4a19d50
Revises: a1f5d8c3e7b2
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c7e4a19d50"
down_revision: str | None = "a1f5d8c3e7b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "app_users",
        sa.Column(
            "first_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "app_users",
        sa.Column(
            "last_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "app_users",
        sa.Column(
            "phone",
            sa.String(length=32),
            nullable=True,
        ),
    )

    op.add_column(
        "app_users",
        sa.Column(
            "employee_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_app_users_employee_id_employees",
        "app_users",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "ix_app_users_phone",
        "app_users",
        ["phone"],
        unique=False,
    )

    op.create_index(
        "uq_app_users_employee_id",
        "app_users",
        ["employee_id"],
        unique=True,
    )

    op.execute(
        """
        UPDATE app_users
        SET
            first_name = CASE
                WHEN btrim(full_name) = ''
                    THEN 'Пользователь'
                WHEN strpos(btrim(full_name), ' ') > 0
                    THEN split_part(
                        btrim(full_name),
                        ' ',
                        1
                    )
                ELSE btrim(full_name)
            END,
            last_name = CASE
                WHEN strpos(
                    btrim(full_name),
                    ' '
                ) > 0
                    THEN btrim(
                        substr(
                            btrim(full_name),
                            strpos(
                                btrim(full_name),
                                ' '
                            ) + 1
                        )
                    )
                ELSE ''
            END
        WHERE
            first_name IS NULL
            OR last_name IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index(
        "uq_app_users_employee_id",
        table_name="app_users",
    )

    op.drop_index(
        "ix_app_users_phone",
        table_name="app_users",
    )

    op.drop_constraint(
        "fk_app_users_employee_id_employees",
        "app_users",
        type_="foreignkey",
    )

    op.drop_column(
        "app_users",
        "employee_id",
    )

    op.drop_column(
        "app_users",
        "phone",
    )

    op.drop_column(
        "app_users",
        "last_name",
    )

    op.drop_column(
        "app_users",
        "first_name",
    )