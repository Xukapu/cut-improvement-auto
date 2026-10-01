from decimal import Decimal

import pytest
from app.schemas.work_participation import (
    WorkParticipationUpdate,
)
from pydantic import ValidationError


def test_disabled_participation_does_not_require_rate() -> None:
    payload = WorkParticipationUpdate(
        enabled=False,
    )

    assert payload.enabled is False
    assert payload.rate_percent is None


def test_enabled_participation_requires_rate() -> None:
    with pytest.raises(ValidationError):
        WorkParticipationUpdate(
            enabled=True,
        )


def test_enabled_participation_accepts_rate() -> None:
    payload = WorkParticipationUpdate(
        enabled=True,
        rate_percent=Decimal("35.50"),
    )

    assert payload.enabled is True
    assert payload.rate_percent == Decimal("35.50")


def test_rate_cannot_exceed_one_hundred() -> None:
    with pytest.raises(ValidationError):
        WorkParticipationUpdate(
            enabled=True,
            rate_percent=Decimal("101"),
        )
