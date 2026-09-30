from decimal import Decimal

from app.services.work_item import calculate_earning


def test_employee_earning_calculation() -> None:
    result = calculate_earning(
        price=Decimal("10000"),
        share_percent=Decimal("70"),
        rate_percent=Decimal("30"),
    )

    assert result == Decimal("2100.00")


def test_second_employee_earning_calculation() -> None:
    result = calculate_earning(
        price=Decimal("10000"),
        share_percent=Decimal("30"),
        rate_percent=Decimal("40"),
    )

    assert result == Decimal("1200.00")
