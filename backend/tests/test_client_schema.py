import pytest
from app.models.client import ArchiveReason, ClientSource
from app.schemas.client import (
    ArchiveClientRequest,
    ClientCreate,
    ClientInternalMarkUpdate,
    ClientUpdate,
)
from pydantic import ValidationError


def test_internal_mark_defaults_to_false() -> None:
    client = ClientCreate(
        full_name="Иван Иванов",
        phone_primary="+79990000000",
        source=ClientSource.OTHER,
    )

    assert client.internal_mark is False


def test_owner_can_choose_internal_mark_on_create() -> None:
    client = ClientCreate(
        full_name="Иван Иванов",
        phone_primary="+79990000000",
        source=ClientSource.OTHER,
        internal_mark=True,
    )

    assert client.internal_mark is True


def test_regular_client_update_cannot_change_internal_mark() -> None:
    with pytest.raises(ValidationError):
        ClientUpdate(
            full_name="Иван Иванов",
            phone_primary="+79990000000",
            source=ClientSource.OTHER,
            internal_mark=True,
        )


def test_internal_mark_update_schema() -> None:
    payload = ClientInternalMarkUpdate(
        internal_mark=True,
    )

    assert payload.internal_mark is True


def test_referral_requires_referrer_number() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            full_name="Иван Иванов",
            phone_primary="+79990000000",
            source=ClientSource.REFERRAL,
        )


def test_non_referral_rejects_referrer_number() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            full_name="Иван Иванов",
            phone_primary="+79990000000",
            source=ClientSource.AVITO,
            referred_by_client_number=1,
        )


def test_client_text_fields_are_trimmed() -> None:
    client = ClientCreate(
        full_name="  Иван Иванов  ",
        phone_primary="  +79990000000  ",
        phone_secondary="   ",
        source=ClientSource.OTHER,
        notes="  заметка  ",
    )

    assert client.full_name == "Иван Иванов"
    assert client.phone_primary == "+79990000000"
    assert client.phone_secondary is None
    assert client.notes == "заметка"


def test_referrer_number_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            full_name="Иван Иванов",
            phone_primary="+79990000000",
            source=ClientSource.REFERRAL,
            referred_by_client_number=0,
        )


def test_archiving_requires_explicit_confirmation() -> None:
    with pytest.raises(ValidationError):
        ArchiveClientRequest(
            confirm=False,
            reason=ArchiveReason.OTHER,
        )


def test_archive_comment_is_trimmed() -> None:
    payload = ArchiveClientRequest(
        confirm=True,
        reason=ArchiveReason.NO_LONGER_SERVICED,
        comment="  Больше не обслуживается  ",
    )

    assert payload.comment == "Больше не обслуживается"
