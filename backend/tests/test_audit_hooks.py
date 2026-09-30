from datetime import date

import pytest
from app.db.audit_hooks import classify_audit_action
from app.services.audit import validate_audit_period
from fastapi import HTTPException


def test_create_action() -> None:
    assert (
        classify_audit_action(
            entity_type="client",
            old_values=None,
            new_values={
                "full_name": "Иван",
            },
            is_new=True,
            is_deleted=False,
        )
        == "create"
    )


def test_status_change_action() -> None:
    assert (
        classify_audit_action(
            entity_type="work_order",
            old_values={
                "status": "planned",
            },
            new_values={
                "status": "in_progress",
            },
            is_new=False,
            is_deleted=False,
        )
        == "status_change"
    )


def test_internal_mark_action() -> None:
    assert (
        classify_audit_action(
            entity_type="client",
            old_values={
                "internal_mark": False,
            },
            new_values={
                "internal_mark": True,
            },
            is_new=False,
            is_deleted=False,
        )
        == "internal_mark_change"
    )


def test_soft_delete_action() -> None:
    assert (
        classify_audit_action(
            entity_type="part",
            old_values={
                "deleted_at": None,
            },
            new_values={
                "deleted_at": ("2026-09-30T15:00:00+00:00"),
            },
            is_new=False,
            is_deleted=False,
        )
        == "delete"
    )


def test_payment_change_action() -> None:
    assert (
        classify_audit_action(
            entity_type="payment",
            old_values={
                "amount": "5000.00",
            },
            new_values={
                "amount": "4000.00",
            },
            is_new=False,
            is_deleted=False,
        )
        == "payment_change"
    )


def test_regular_update_action() -> None:
    assert (
        classify_audit_action(
            entity_type="vehicle",
            old_values={
                "mileage": 55000,
            },
            new_values={
                "mileage": 56000,
            },
            is_new=False,
            is_deleted=False,
        )
        == "update"
    )


def test_valid_audit_period() -> None:
    validate_audit_period(
        date(2026, 9, 1),
        date(2026, 9, 30),
    )


def test_invalid_audit_period() -> None:
    with pytest.raises(HTTPException):
        validate_audit_period(
            date(2026, 10, 1),
            date(2026, 9, 30),
        )
