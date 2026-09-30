from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


def get_payment_by_number(
    db: Session,
    payment_number: int,
) -> Payment | None:
    return db.scalar(
        select(Payment).where(
            Payment.payment_number == payment_number,
            Payment.deleted_at.is_(None),
        )
    )


def list_payments_for_order(
    db: Session,
    work_order_id: UUID,
) -> list[Payment]:
    return list(
        db.scalars(
            select(Payment)
            .where(
                Payment.work_order_id == work_order_id,
                Payment.deleted_at.is_(None),
            )
            .order_by(
                Payment.paid_at.asc(),
                Payment.payment_number.asc(),
            )
        ).all()
    )
