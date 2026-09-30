from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.part import Part, PartProvidedBy
from app.models.payment import Payment
from app.models.work_item import WorkItem
from app.repositories.payment import (
    get_payment_by_number,
    list_payments_for_order,
)
from app.schemas.payment import (
    PaymentResponse,
    PaymentSummaryResponse,
    PaymentWrite,
)
from app.services.work_order import require_work_order

_MONEY = Decimal("0.01")

_PAYMENT_NOT_FOUND = (
    "\u041e\u043f\u043b\u0430\u0442\u0430 "
    "\u0432 \u044d\u0442\u043e\u043c "
    "\u0437\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434\u0435 "
    "\u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430."
)

_PAYMENT_EXCEEDS_DEBT = (
    "\u0421\u0443\u043c\u043c\u0430 "
    "\u043e\u043f\u043b\u0430\u0442\u044b "
    "\u043f\u0440\u0435\u0432\u044b\u0448\u0430\u0435\u0442 "
    "\u043e\u0441\u0442\u0430\u0432\u0448\u0443\u044e\u0441\u044f "
    "\u0437\u0430\u0434\u043e\u043b\u0436\u0435\u043d\u043d\u043e\u0441\u0442\u044c "
    "\u043f\u043e "
    "\u0437\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434\u0443."
)


def money(value: Decimal | int | float | None) -> Decimal:
    if value is None:
        value = Decimal("0")

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return value.quantize(
        _MONEY,
        rounding=ROUND_HALF_UP,
    )


def calculate_works_total(
    db: Session,
    work_order_id: UUID,
) -> Decimal:
    value = db.scalar(
        select(
            func.coalesce(
                func.sum(WorkItem.price),
                0,
            )
        ).where(
            WorkItem.work_order_id == work_order_id,
            WorkItem.deleted_at.is_(None),
        )
    )

    return money(value)


def calculate_parts_total(
    db: Session,
    work_order_id: UUID,
) -> Decimal:
    value = db.scalar(
        select(
            func.coalesce(
                func.sum(Part.unit_price * Part.quantity),
                0,
            )
        ).where(
            Part.work_order_id == work_order_id,
            Part.deleted_at.is_(None),
            Part.provided_by == PartProvidedBy.STO,
        )
    )

    return money(value)


def calculate_paid_amount(
    db: Session,
    work_order_id: UUID,
) -> Decimal:
    value = db.scalar(
        select(
            func.coalesce(
                func.sum(Payment.amount),
                0,
            )
        ).where(
            Payment.work_order_id == work_order_id,
            Payment.deleted_at.is_(None),
        )
    )

    return money(value)


def calculate_repair_total(
    db: Session,
    work_order_id: UUID,
) -> tuple[Decimal, Decimal, Decimal]:
    works_total = calculate_works_total(
        db,
        work_order_id,
    )

    parts_total = calculate_parts_total(
        db,
        work_order_id,
    )

    repair_total = money(works_total + parts_total)

    return (
        works_total,
        parts_total,
        repair_total,
    )


def require_order_payment(
    db: Session,
    *,
    order,
    payment_number: int,
) -> Payment:
    payment = get_payment_by_number(
        db,
        payment_number,
    )

    if payment is None or payment.work_order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_PAYMENT_NOT_FOUND,
        )

    return payment


def ensure_payment_fits_debt(
    *,
    repair_total: Decimal,
    paid_without_payment: Decimal,
    new_amount: Decimal,
) -> None:
    resulting_paid = money(paid_without_payment + new_amount)

    if resulting_paid > repair_total:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_PAYMENT_EXCEEDS_DEBT,
        )


def create_payment(
    db: Session,
    *,
    work_order_number: int,
    payload: PaymentWrite,
) -> PaymentResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    _, _, repair_total = calculate_repair_total(
        db,
        order.id,
    )

    paid_amount = calculate_paid_amount(
        db,
        order.id,
    )

    ensure_payment_fits_debt(
        repair_total=repair_total,
        paid_without_payment=paid_amount,
        new_amount=money(payload.amount),
    )

    payment = Payment(
        work_order_id=order.id,
        amount=money(payload.amount),
        method=payload.method,
        comment=payload.comment,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse.model_validate(payment)


def update_payment(
    db: Session,
    *,
    work_order_number: int,
    payment_number: int,
    payload: PaymentWrite,
) -> PaymentResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    payment = require_order_payment(
        db,
        order=order,
        payment_number=payment_number,
    )

    _, _, repair_total = calculate_repair_total(
        db,
        order.id,
    )

    current_paid = calculate_paid_amount(
        db,
        order.id,
    )

    paid_without_current = money(current_paid - payment.amount)

    ensure_payment_fits_debt(
        repair_total=repair_total,
        paid_without_payment=paid_without_current,
        new_amount=money(payload.amount),
    )

    payment.amount = money(payload.amount)
    payment.method = payload.method
    payment.comment = payload.comment

    db.commit()
    db.refresh(payment)

    return PaymentResponse.model_validate(payment)


def delete_payment(
    db: Session,
    *,
    work_order_number: int,
    payment_number: int,
) -> None:
    order = require_work_order(
        db,
        work_order_number,
    )

    payment = require_order_payment(
        db,
        order=order,
        payment_number=payment_number,
    )

    payment.deleted_at = datetime.now(UTC)

    db.commit()


def get_payment_summary(
    db: Session,
    work_order_number: int,
) -> PaymentSummaryResponse:
    order = require_work_order(
        db,
        work_order_number,
    )

    (
        works_total,
        parts_total,
        repair_total,
    ) = calculate_repair_total(
        db,
        order.id,
    )

    paid_amount = calculate_paid_amount(
        db,
        order.id,
    )

    debt_amount = money(repair_total - paid_amount)

    payments = list_payments_for_order(
        db,
        order.id,
    )

    return PaymentSummaryResponse(
        work_order_number=work_order_number,
        works_total=works_total,
        parts_total=parts_total,
        repair_total=repair_total,
        paid_amount=paid_amount,
        debt_amount=debt_amount,
        payments=[PaymentResponse.model_validate(payment) for payment in payments],
    )
