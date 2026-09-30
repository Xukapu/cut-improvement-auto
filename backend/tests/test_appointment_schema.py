from datetime import date, time

import pytest
from app.models.appointment import AppointmentStatus
from app.schemas.appointment import AppointmentCreate
from pydantic import ValidationError


def test_appointment_defaults_to_scheduled() -> None:
    appointment = AppointmentCreate(
        client_number=1,
        vehicle_number=1,
        appointment_date=date(2026, 10, 1),
        appointment_time=time(10, 30),
        reason="Замена масла",
    )

    assert appointment.status == AppointmentStatus.SCHEDULED


def test_appointment_text_is_trimmed() -> None:
    appointment = AppointmentCreate(
        client_number=1,
        vehicle_number=1,
        appointment_date=date(2026, 10, 1),
        appointment_time=time(10, 30),
        reason="  Замена масла  ",
        comment="  Позвонить заранее  ",
    )

    assert appointment.reason == "Замена масла"
    assert appointment.comment == "Позвонить заранее"


def test_empty_reason_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            client_number=1,
            vehicle_number=1,
            appointment_date=date(2026, 10, 1),
            appointment_time=time(10, 30),
            reason=" ",
        )


def test_client_number_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            client_number=0,
            vehicle_number=1,
            appointment_date=date(2026, 10, 1),
            appointment_time=time(10, 30),
            reason="Диагностика",
        )


def test_vehicle_number_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            client_number=1,
            vehicle_number=0,
            appointment_date=date(2026, 10, 1),
            appointment_time=time(10, 30),
            reason="Диагностика",
        )
