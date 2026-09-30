from datetime import date, time
from types import SimpleNamespace

from app.services.notification import (
    build_appointment_reminder_message,
    build_confirmation_message,
    service_reminder_is_due,
)


def appointment_stub():
    return SimpleNamespace(
        appointment_date=date(
            2026,
            10,
            3,
        ),
        appointment_time=time(
            15,
            0,
        ),
    )


def test_confirmation_message() -> None:
    text = build_confirmation_message(appointment_stub())

    assert "03.10.2026" in text
    assert "15:00" in text
    assert "ЦУТ Improvement Auto" in text


def test_appointment_reminder_message() -> None:
    text = build_appointment_reminder_message(appointment_stub())

    assert "03.10.2026" in text
    assert "15:00" in text
    assert "Напоминаем" in text


def test_service_reminder_due_by_date() -> None:
    assert service_reminder_is_due(
        due_date=date(
            2026,
            10,
            1,
        ),
        due_mileage=None,
        current_date=date(
            2026,
            10,
            1,
        ),
        current_mileage=55000,
    )


def test_service_reminder_due_by_mileage() -> None:
    assert service_reminder_is_due(
        due_date=None,
        due_mileage=55000,
        current_date=date(
            2026,
            10,
            1,
        ),
        current_mileage=55000,
    )


def test_service_reminder_not_due() -> None:
    assert not service_reminder_is_due(
        due_date=date(
            2027,
            4,
            1,
        ),
        due_mileage=65000,
        current_date=date(
            2026,
            10,
            1,
        ),
        current_mileage=55000,
    )
