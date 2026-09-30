from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee, EmployeeRate


def get_employee_by_number(
    db: Session,
    employee_number: int,
) -> Employee | None:
    return db.scalar(
        select(Employee).where(
            Employee.employee_number == employee_number,
            Employee.deleted_at.is_(None),
        )
    )


def get_current_employee_rate(
    db: Session,
    employee_id,
) -> EmployeeRate | None:
    return db.scalar(
        select(EmployeeRate).where(
            EmployeeRate.employee_id == employee_id,
            EmployeeRate.effective_to.is_(None),
            EmployeeRate.deleted_at.is_(None),
        )
    )


def list_employee_rates(
    db: Session,
    employee_id,
) -> list[EmployeeRate]:
    return list(
        db.scalars(
            select(EmployeeRate)
            .where(
                EmployeeRate.employee_id == employee_id,
                EmployeeRate.deleted_at.is_(None),
            )
            .order_by(EmployeeRate.effective_from.desc())
        ).all()
    )


def list_employees(
    db: Session,
    *,
    include_inactive: bool,
) -> list[Employee]:
    filters = [
        Employee.deleted_at.is_(None),
    ]

    if not include_inactive:
        filters.append(Employee.is_active.is_(True))

    return list(
        db.scalars(select(Employee).where(*filters).order_by(Employee.employee_number.asc())).all()
    )
