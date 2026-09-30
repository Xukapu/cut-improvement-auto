from decimal import Decimal

from app.schemas.employee import (
    EmployeeFinancialResponse,
    EmployeePublicResponse,
)
from app.schemas.work_item import (
    WorkAssignmentFinancialResponse,
    WorkAssignmentPublicResponse,
    WorkItemFinancialResponse,
    WorkItemPublicResponse,
)


def test_public_employee_has_no_rate() -> None:
    employee = EmployeePublicResponse(
        employee_number=1,
        full_name="Иван Механик",
        is_active=True,
    )

    data = employee.model_dump()

    assert "current_rate_percent" not in data


def test_financial_employee_contains_rate() -> None:
    employee = EmployeeFinancialResponse(
        employee_number=1,
        full_name="Иван Механик",
        is_active=True,
        current_rate_percent=Decimal("30"),
    )

    assert employee.current_rate_percent == Decimal("30")


def test_public_work_hides_financial_calculation() -> None:
    work = WorkItemPublicResponse(
        work_item_number=1,
        name="Замена масла",
        price=Decimal("10000"),
        assignments=[
            WorkAssignmentPublicResponse(
                employee_number=1,
                employee_name="Иван Механик",
            )
        ],
    )

    data = work.model_dump()

    assignment = data["assignments"][0]

    assert "share_percent" not in assignment
    assert "rate_percent_snapshot" not in assignment
    assert "earning_amount" not in assignment
    assert "total_employee_earnings" not in data


def test_financial_work_contains_owner_calculation() -> None:
    work = WorkItemFinancialResponse(
        work_item_number=1,
        name="Замена масла",
        price=Decimal("10000"),
        assignments=[
            WorkAssignmentFinancialResponse(
                employee_number=1,
                employee_name="Иван Механик",
                share_percent=Decimal("70"),
                rate_percent_snapshot=Decimal("30"),
                earning_amount=Decimal("2100"),
            )
        ],
        total_employee_earnings=Decimal("2100"),
    )

    assert work.assignments[0].share_percent == Decimal("70")
    assert work.assignments[0].rate_percent_snapshot == Decimal("30")
    assert work.assignments[0].earning_amount == Decimal("2100")
