from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.repositories.audit import list_audit_logs
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
)

_AUDIT_ACTOR_KEY = "audit_actor"


def set_audit_actor(
    db: Session,
    user: Any,
) -> None:
    role = getattr(
        user,
        "role",
        None,
    )

    role_value = None

    if role is not None:
        role_value = getattr(
            role,
            "value",
            str(role),
        )

    db.info[_AUDIT_ACTOR_KEY] = {
        "id": getattr(
            user,
            "id",
            None,
        ),
        "login": getattr(
            user,
            "login",
            None,
        ),
        "role": role_value,
    }


def get_audit_actor(
    db: Session,
) -> dict[str, Any] | None:
    return db.info.get(_AUDIT_ACTOR_KEY)


def audit_json_value(value: Any) -> Any:
    """Преобразовать значение в безопасный JSON для журнала."""

    if value is None:
        return None

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {str(key): audit_json_value(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [audit_json_value(item) for item in value]

    if isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    return str(value)


def audit_payload(
    value: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if value is None:
        return None

    return {str(key): audit_json_value(item) for key, item in value.items()}


def snapshot_fields(
    obj: Any,
    *fields: str,
) -> dict[str, Any]:
    return {field: audit_json_value(getattr(obj, field)) for field in fields}


def record_audit_event(
    db: Session,
    *,
    actor: Any | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    entity_number: int | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
) -> AuditLog:
    actor_user_id = None
    actor_login = None
    actor_role = None

    if actor is not None:
        if isinstance(actor, dict):
            actor_user_id = actor.get("id")
            actor_login = actor.get("login")
            actor_role = actor.get("role")

        else:
            actor_user_id = getattr(
                actor,
                "id",
                None,
            )

            actor_login = getattr(
                actor,
                "login",
                None,
            )

            role = getattr(
                actor,
                "role",
                None,
            )

            if role is not None:
                actor_role = getattr(
                    role,
                    "value",
                    str(role),
                )

    event = AuditLog(
        actor_user_id=actor_user_id,
        actor_login=actor_login,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_number=entity_number,
        old_values=audit_payload(old_values),
        new_values=audit_payload(new_values),
    )

    db.add(event)

    return event


def validate_audit_period(
    date_from: date | None,
    date_to: date | None,
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("Дата начала периода не может быть позже даты окончания периода."),
        )


def get_audit_log(
    db: Session,
    *,
    entity_type: str | None,
    entity_number: int | None,
    action: str | None,
    actor_login: str | None,
    date_from: date | None,
    date_to: date | None,
    limit: int,
    offset: int,
) -> AuditLogListResponse:
    validate_audit_period(
        date_from,
        date_to,
    )

    items, total = list_audit_logs(
        db,
        entity_type=entity_type,
        entity_number=entity_number,
        action=action,
        actor_login=actor_login,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
