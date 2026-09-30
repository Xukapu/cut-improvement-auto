import pytest
from app.schemas.dispute import DisputeCreate
from pydantic import ValidationError


def test_dispute_record() -> None:
    item = DisputeCreate(
        found_text=("Обнаружена течь масла в районе переднего сальника."),
        master_recommendation=("Рекомендована замена сальника."),
        client_response=("Клиент отказался от ремонта сейчас."),
    )

    assert "течь масла" in item.found_text
    assert item.master_recommendation is not None
    assert item.client_response is not None


def test_dispute_text_is_trimmed() -> None:
    item = DisputeCreate(
        found_text="  Обнаружен люфт.  ",
        master_recommendation="  Заменить деталь.  ",
        client_response="  Клиент ознакомлен.  ",
    )

    assert item.found_text == "Обнаружен люфт."
    assert item.master_recommendation == "Заменить деталь."
    assert item.client_response == "Клиент ознакомлен."


def test_optional_empty_text_becomes_none() -> None:
    item = DisputeCreate(
        found_text="Обнаружен износ.",
        master_recommendation="   ",
        client_response="   ",
    )

    assert item.master_recommendation is None
    assert item.client_response is None


def test_empty_found_text_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DisputeCreate(
            found_text=" ",
        )
