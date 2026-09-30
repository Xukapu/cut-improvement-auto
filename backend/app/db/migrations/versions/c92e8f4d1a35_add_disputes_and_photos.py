"""add disputes and photos

Revision ID: c92e8f4d1a35
Revises: b63c4f217e92
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c92e8f4d1a35"
down_revision: str | None = "b63c4f217e92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dispute_records",
        sa.Column(
            "dispute_number",
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
            "found_text",
            sa.String(length=4000),
            nullable=False,
        ),
        sa.Column(
            "master_recommendation",
            sa.String(length=4000),
            nullable=True,
        ),
        sa.Column(
            "client_response",
            sa.String(length=4000),
            nullable=True,
        ),
        sa.Column(
            "recorded_at",
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
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["work_orders.id"],
            name=op.f("fk_dispute_records_work_order_id_work_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_dispute_records"),
        ),
        sa.UniqueConstraint(
            "dispute_number",
            name=op.f("uq_dispute_records_dispute_number"),
        ),
    )

    op.create_index(
        "ix_dispute_records_work_order_id",
        "dispute_records",
        ["work_order_id"],
        unique=False,
    )

    op.create_table(
        "dispute_photos",
        sa.Column(
            "photo_number",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "dispute_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "original_filename",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "stored_relative_path",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "size_bytes",
            sa.BigInteger(),
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
        sa.ForeignKeyConstraint(
            ["dispute_id"],
            ["dispute_records.id"],
            name=op.f("fk_dispute_photos_dispute_id_dispute_records"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_dispute_photos"),
        ),
        sa.UniqueConstraint(
            "photo_number",
            name=op.f("uq_dispute_photos_photo_number"),
        ),
    )

    op.create_index(
        "ix_dispute_photos_dispute_id",
        "dispute_photos",
        ["dispute_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dispute_photos_dispute_id",
        table_name="dispute_photos",
    )

    op.drop_table("dispute_photos")

    op.drop_index(
        "ix_dispute_records_work_order_id",
        table_name="dispute_records",
    )

    op.drop_table("dispute_records")
