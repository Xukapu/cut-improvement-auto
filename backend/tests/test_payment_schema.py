from decimal import Decimal

import pytest
from app.models.payment import PaymentMethod
from app.schemas.payment import PaymentCreate
from pydantic import ValidationError


def test_cash_payment() -> None:
    payment = PaymentCreate(
        amount=Decimal("5000"),
        method=PaymentMethod.CASH,
        comment="Частичная оплата",
    )

    assert payment.amount == Decimal("5000")
    assert payment.method == PaymentMethod.CASH


def test_card_payment() -> None:
    payment = PaymentCreate(
        amount=Decimal("1000"),
        method=PaymentMethod.CARD,
    )

    assert payment.method == PaymentMethod.CARD


def test_transfer_payment() -> None:
    payment = PaymentCreate(
        amount=Decimal("1000"),
        method=PaymentMethod.TRANSFER,
    )

    assert payment.method == PaymentMethod.TRANSFER


def test_zero_payment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PaymentCreate(
            amount=Decimal("0"),
            method=PaymentMethod.CASH,
        )


def test_negative_payment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PaymentCreate(
            amount=Decimal("-1"),
            method=PaymentMethod.CASH,
        )


def test_empty_comment_becomes_none() -> None:
    payment = PaymentCreate(
        amount=Decimal("1000"),
        method=PaymentMethod.CASH,
        comment="   ",
    )

    assert payment.comment is None
