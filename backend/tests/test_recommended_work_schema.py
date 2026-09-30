import pytest
from app.schemas.recommended_work import RecommendedWorkCreate
from pydantic import ValidationError


def test_recommended_work() -> None:
    item = RecommendedWorkCreate(
        name="Замена передних тормозных колодок",
        comment="Износ около 80%.",
    )

    assert item.name == "Замена передних тормозных колодок"
    assert item.comment == "Износ около 80%."


def test_recommended_work_text_is_trimmed() -> None:
    item = RecommendedWorkCreate(
        name="  Замена ремня  ",
        comment="  Проверить при следующем ТО.  ",
    )

    assert item.name == "Замена ремня"
    assert item.comment == "Проверить при следующем ТО."


def test_empty_comment_becomes_none() -> None:
    item = RecommendedWorkCreate(
        name="Диагностика подвески",
        comment="   ",
    )

    assert item.comment is None


def test_short_name_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RecommendedWorkCreate(
            name="X",
        )
