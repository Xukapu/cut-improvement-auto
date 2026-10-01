from datetime import UTC, datetime

import pytest
from app.schemas.notification_management import (
    CustomerNotificationUpdate,
)
from pydantic import ValidationError


def test_notification_update_valid() -> None:
    payload = CustomerNotificationUpdate(
        message_text="Напоминаем о записи.",
        scheduled_for=datetime(
            2026,
            10,
            2,
            12,
            30,
            tzinfo=UTC,
        ),
    )

    assert payload.message_text == "Напоминаем о записи."


def test_notification_update_requires_message() -> None:
    with pytest.raises(ValidationError):
        CustomerNotificationUpdate(
            message_text="",
            scheduled_for=datetime(
                2026,
                10,
                2,
                12,
                30,
                tzinfo=UTC,
            ),
        )
