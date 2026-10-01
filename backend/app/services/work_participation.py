from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee, EmployeeRate
from app.models.user import User
from app.schemas.work_participation import (
    WorkParticipationResponse,
    WorkParticipationUpdate,
)


def _current_rate(
    db: Session,
    employee_id: UUID,
) -> EmployeeRate | None:
    return db.scalar(
        select(EmployeeRate).where(
            EmployeeRate.employee_id == employee_id,
            EmployeeRate.effective_to.is_(None),
            EmployeeRate.deleted_at.is_(None),
        )
    )


def _set_rate(
    db: Session,
    *,
    employee: Employee,
    rate_percent: Decimal,
) -> None:
    current = _current_rate(
        db,
        employee.id,
    )

    if current is not None and current.rate_percent == rate_percent:
        return

    now = datetime.now(UTC)

    if current is not None:
        current.effective_to = now

    db.add(
        EmployeeRate(
            employee_id=employee.id,
            rate_percent=rate_percent,
            effective_from=now,
        )
    )


def _employee_for_user(
    db: Session,
    user: User,
) -> Employee | None:
    if user.employee_id is None:
        return None

    return db.get(
        Employee,
        user.employee_id,
    )


def get_work_participation(
    db: Session,
    *,
    user: User,
) -> WorkParticipationResponse:
    employee = _employee_for_user(
        db,
        user,
    )

    if employee is None:
        return WorkParticipationResponse(
            enabled=False,
            employee_number=None,
            employee_name=user.full_name,
            rate_percent=None,
        )

    rate = _current_rate(
        db,
        employee.id,
    )

    return WorkParticipationResponse(
        enabled=(employee.deleted_at is None and employee.is_active),
        employee_number=(employee.employee_number),
        employee_name=(employee.full_name),
        rate_percent=(rate.rate_percent if rate is not None else None),
    )


def update_work_participation(
    db: Session,
    *,
    user: User,
    payload: WorkParticipationUpdate,
) -> WorkParticipationResponse:
    employee = _employee_for_user(
        db,
        user,
    )

    if employee is None:
        if not payload.enabled:
            return get_work_participation(
                db,
                user=user,
            )

        employee = Employee(
            full_name=user.full_name,
            is_active=True,
        )

        db.add(employee)
        db.flush()

        user.employee_id = employee.id

    employee.full_name = user.full_name

    if payload.enabled:
        employee.deleted_at = None
        employee.is_active = True

        if payload.rate_percent is None:
            raise ValueError("Укажите ставку исполнителя.")

        _set_rate(
            db,
            employee=employee,
            rate_percent=(payload.rate_percent),
        )
    else:
        employee.is_active = False

    db.commit()
    db.refresh(employee)

    return get_work_participation(
        db,
        user=user,
    )
