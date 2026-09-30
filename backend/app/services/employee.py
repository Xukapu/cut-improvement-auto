from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee, EmployeeRate
from app.repositories.employee import (
    get_current_employee_rate,
    get_employee_by_number,
    list_employee_rates,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeFinancialResponse,
    EmployeePublicResponse,
    EmployeeRateHistoryItem,
    EmployeeRateHistoryResponse,
    EmployeeUpdate,
)


def require_employee(
    db: Session,
    employee_number: int,
) -> Employee:
    employee = get_employee_by_number(
        db,
        employee_number,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден.",
        )

    return employee


def employee_public_response(
    employee: Employee,
) -> EmployeePublicResponse:
    return EmployeePublicResponse(
        employee_number=employee.employee_number,
        full_name=employee.full_name,
        is_active=employee.is_active,
    )


def employee_financial_response(
    db: Session,
    employee: Employee,
) -> EmployeeFinancialResponse:
    rate = get_current_employee_rate(
        db,
        employee.id,
    )

    if rate is None:
        raise RuntimeError("У сотрудника отсутствует текущая ставка.")

    return EmployeeFinancialResponse(
        employee_number=employee.employee_number,
        full_name=employee.full_name,
        is_active=employee.is_active,
        current_rate_percent=rate.rate_percent,
    )


def create_employee(
    db: Session,
    payload: EmployeeCreate,
) -> EmployeeFinancialResponse:
    employee = Employee(
        full_name=payload.full_name,
        is_active=True,
    )

    db.add(employee)
    db.flush()

    rate = EmployeeRate(
        employee_id=employee.id,
        rate_percent=payload.rate_percent,
    )

    db.add(rate)
    db.commit()
    db.refresh(employee)

    return employee_financial_response(
        db,
        employee,
    )


def update_employee(
    db: Session,
    *,
    employee: Employee,
    payload: EmployeeUpdate,
) -> EmployeeFinancialResponse:
    employee.full_name = payload.full_name
    employee.is_active = payload.is_active

    db.commit()
    db.refresh(employee)

    return employee_financial_response(
        db,
        employee,
    )


def change_employee_rate(
    db: Session,
    *,
    employee: Employee,
    rate_percent,
) -> EmployeeFinancialResponse:
    current_rate = get_current_employee_rate(
        db,
        employee.id,
    )

    if current_rate is None:
        raise RuntimeError("У сотрудника отсутствует текущая ставка.")

    if current_rate.rate_percent == rate_percent:
        return employee_financial_response(
            db,
            employee,
        )

    now = datetime.now(UTC)

    current_rate.effective_to = now

    new_rate = EmployeeRate(
        employee_id=employee.id,
        rate_percent=rate_percent,
        effective_from=now,
    )

    db.add(new_rate)
    db.commit()

    return employee_financial_response(
        db,
        employee,
    )


def employee_rate_history(
    db: Session,
    employee: Employee,
) -> EmployeeRateHistoryResponse:
    rates = list_employee_rates(
        db,
        employee.id,
    )

    return EmployeeRateHistoryResponse(
        employee_number=employee.employee_number,
        full_name=employee.full_name,
        rates=[
            EmployeeRateHistoryItem(
                rate_percent=rate.rate_percent,
                effective_from=rate.effective_from,
                effective_to=rate.effective_to,
            )
            for rate in rates
        ],
    )
