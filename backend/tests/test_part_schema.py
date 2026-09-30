from decimal import Decimal

import pytest
from app.models.part import PartProvidedBy
from app.schemas.part import PartCreate
from pydantic import ValidationError


def test_sto_part_with_quantity() -> None:
    part = PartCreate(
        name="Свеча зажигания",
        quantity=6,
        unit_price=Decimal("800"),
        supplier="Автодок",
        provided_by=PartProvidedBy.STO,
    )

    assert part.quantity == 6
    assert part.unit_price == Decimal("800")
    assert part.provided_by == PartProvidedBy.STO


def test_quantity_defaults_to_one() -> None:
    part = PartCreate(
        name="Масляный фильтр",
        unit_price=Decimal("1200"),
        supplier="Поставщик",
        provided_by=PartProvidedBy.STO,
    )

    assert part.quantity == 1


def test_client_part_can_have_zero_price() -> None:
    part = PartCreate(
        name="Свечи клиента",
        quantity=6,
        unit_price=Decimal("0"),
        supplier=None,
        provided_by=PartProvidedBy.CLIENT,
    )

    assert part.quantity == 6
    assert part.unit_price == Decimal("0")
    assert part.supplier is None


def test_quantity_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        PartCreate(
            name="Свеча",
            quantity=0,
            unit_price=Decimal("800"),
            provided_by=PartProvidedBy.STO,
        )


def test_negative_unit_price_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PartCreate(
            name="Фильтр",
            quantity=1,
            unit_price=Decimal("-1"),
            provided_by=PartProvidedBy.STO,
        )


def test_part_text_is_trimmed() -> None:
    part = PartCreate(
        name="  Фильтр  ",
        quantity=1,
        unit_price=Decimal("1000"),
        supplier="  Поставщик  ",
        provided_by=PartProvidedBy.STO,
    )

    assert part.name == "Фильтр"
    assert part.supplier == "Поставщик"
