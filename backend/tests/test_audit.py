from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from app.services.audit import (
    audit_json_value,
    audit_payload,
)


class ExampleStatus(StrEnum):
    READY = "ready"


def test_audit_decimal_is_exact_string() -> None:
    assert audit_json_value(Decimal("1234.50")) == "1234.50"


def test_audit_uuid_is_string() -> None:
    value = UUID("12345678-1234-5678-1234-567812345678")

    assert audit_json_value(value) == str(value)


def test_audit_date_is_iso_string() -> None:
    value = date(
        2026,
        9,
        30,
    )

    assert audit_json_value(value) == "2026-09-30"


def test_audit_datetime_is_iso_string() -> None:
    value = datetime(
        2026,
        9,
        30,
        12,
        30,
        tzinfo=UTC,
    )

    assert audit_json_value(value) == "2026-09-30T12:30:00+00:00"


def test_audit_enum_uses_value() -> None:
    assert audit_json_value(ExampleStatus.READY) == "ready"


def test_audit_payload_is_recursive() -> None:
    payload = audit_payload(
        {
            "price": Decimal("1000.00"),
            "nested": {
                "status": ExampleStatus.READY,
            },
            "items": [
                Decimal("20.50"),
                None,
            ],
        }
    )

    assert payload == {
        "price": "1000.00",
        "nested": {
            "status": "ready",
        },
        "items": [
            "20.50",
            None,
        ],
    }
