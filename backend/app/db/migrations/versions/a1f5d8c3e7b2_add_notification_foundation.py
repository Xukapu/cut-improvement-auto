"""add notification foundation

Revision ID: a1f5d8c3e7b2
Revises: e9c1a7b4d2f6
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1f5d8c3e7b2"
down_revision: str | None = "e9c1a7b4d2f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client_notification_preferences",
        sa.Column(
            "client_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "sms_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "max_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "appointment_confirmation_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "appointment_reminder_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "service_reminder_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "max_user_id",
            sa.String(length=255),
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
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_client_notification_preferences_client_id",
        "client_notification_preferences",
        ["client_id"],
        unique=True,
    )

    op.create_table(
        "customer_notifications",
        sa.Column(
            "client_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "vehicle_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "appointment_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "channel",
            sa.Enum(
                "sms",
                "max",
                name="notification_channel",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "kind",
            sa.Enum(
                "appointment_confirmation",
                "appointment_reminder",
                "service_reminder",
                name="notification_kind",
                native_enum=False,
                length=64,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "prepared",
                "sent",
                "failed",
                "cancelled",
                name="notification_status",
                native_enum=False,
                length=32,
            ),
            server_default="prepared",
            nullable=False,
        ),
        sa.Column(
            "message_text",
            sa.String(length=2000),
            nullable=False,
        ),
        sa.Column(
            "scheduled_for",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "provider_message_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.String(length=2000),
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
            "channel IN ('sms', 'max')",
            name="channel_valid",
        ),
        sa.CheckConstraint(
            "kind IN ('appointment_confirmation', 'appointment_reminder', 'service_reminder')",
            name="kind_valid",
        ),
        sa.CheckConstraint(
            "status IN ('prepared', 'sent', 'failed', 'cancelled')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["appointment_id"],
            ["appointments.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_customer_notifications_client_id",
        "customer_notifications",
        ["client_id"],
        unique=False,
    )

    op.create_index(
        "ix_customer_notifications_vehicle_id",
        "customer_notifications",
        ["vehicle_id"],
        unique=False,
    )

    op.create_index(
        "ix_customer_notifications_appointment_id",
        "customer_notifications",
        ["appointment_id"],
        unique=False,
    )

    op.create_index(
        "ix_customer_notifications_scheduled_for",
        "customer_notifications",
        ["scheduled_for"],
        unique=False,
    )

    op.create_index(
        "ix_customer_notifications_status_scheduled",
        "customer_notifications",
        ["status", "scheduled_for"],
        unique=False,
    )

    op.create_table(
        "service_reminders",
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
            "work_name",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "due_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "due_mileage",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "message_text",
            sa.String(length=2000),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "planned",
                "completed",
                "cancelled",
                name="service_reminder_status",
                native_enum=False,
                length=32,
            ),
            server_default="planned",
            nullable=False,
        ),
        sa.Column(
            "completed_at",
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
            "due_date IS NOT NULL OR due_mileage IS NOT NULL",
            name="due_condition",
        ),
        sa.CheckConstraint(
            "due_mileage IS NULL OR due_mileage >= 0",
            name="due_mileage_non_negative",
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'completed', 'cancelled')",
            name="status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_service_reminders_client_id",
        "service_reminders",
        ["client_id"],
        unique=False,
    )

    op.create_index(
        "ix_service_reminders_vehicle_id",
        "service_reminders",
        ["vehicle_id"],
        unique=False,
    )

    op.create_index(
        "ix_service_reminders_due_date",
        "service_reminders",
        ["due_date"],
        unique=False,
    )

    op.create_index(
        "ix_service_reminders_due_mileage",
        "service_reminders",
        ["due_mileage"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_reminders_due_mileage",
        table_name="service_reminders",
    )

    op.drop_index(
        "ix_service_reminders_due_date",
        table_name="service_reminders",
    )

    op.drop_index(
        "ix_service_reminders_vehicle_id",
        table_name="service_reminders",
    )

    op.drop_index(
        "ix_service_reminders_client_id",
        table_name="service_reminders",
    )

    op.drop_table(
        "service_reminders",
    )

    op.drop_index(
        "ix_customer_notifications_status_scheduled",
        table_name="customer_notifications",
    )

    op.drop_index(
        "ix_customer_notifications_scheduled_for",
        table_name="customer_notifications",
    )

    op.drop_index(
        "ix_customer_notifications_appointment_id",
        table_name="customer_notifications",
    )

    op.drop_index(
        "ix_customer_notifications_vehicle_id",
        table_name="customer_notifications",
    )

    op.drop_index(
        "ix_customer_notifications_client_id",
        table_name="customer_notifications",
    )

    op.drop_table(
        "customer_notifications",
    )

    op.drop_index(
        "ix_client_notification_preferences_client_id",
        table_name="client_notification_preferences",
    )

    op.drop_table(
        "client_notification_preferences",
    )
