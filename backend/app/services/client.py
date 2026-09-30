from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import ArchiveReason, Client, ClientSource
from app.repositories.client import (
    get_archived_client_by_number,
    get_client_by_id,
    get_client_by_number,
)
from app.schemas.client import ClientCreate, ClientUpdate


def resolve_referrer(
    db: Session,
    *,
    source: ClientSource,
    referred_by_client_number: int | None,
    current_client_id: UUID | None = None,
) -> Client | None:
    if source != ClientSource.REFERRAL:
        return None

    if referred_by_client_number is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Не указан клиент, который дал рекомендацию.",
        )

    referrer = get_client_by_number(
        db,
        referred_by_client_number,
    )

    if referrer is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Клиент, указанный как рекомендатель, не найден.",
        )

    if current_client_id is not None and referrer.id == current_client_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Клиент не может рекомендовать сам себя.",
        )

    return referrer


def create_client(
    db: Session,
    payload: ClientCreate,
) -> Client:
    referrer = resolve_referrer(
        db,
        source=payload.source,
        referred_by_client_number=payload.referred_by_client_number,
    )

    data = payload.model_dump(exclude={"referred_by_client_number"})

    client = Client(
        **data,
        referred_by_client_id=(referrer.id if referrer is not None else None),
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    result = get_client_by_id(
        db,
        client.id,
    )

    if result is None:
        raise RuntimeError("Созданный клиент не найден.")

    return result


def update_client(
    db: Session,
    *,
    client: Client,
    payload: ClientUpdate,
) -> Client:
    referrer = resolve_referrer(
        db,
        source=payload.source,
        referred_by_client_number=payload.referred_by_client_number,
        current_client_id=client.id,
    )

    data = payload.model_dump(exclude={"referred_by_client_number"})

    for field, value in data.items():
        setattr(client, field, value)

    client.referred_by_client_id = referrer.id if referrer is not None else None

    db.commit()

    result = get_client_by_id(
        db,
        client.id,
    )

    if result is None:
        raise RuntimeError("Обновлённый клиент не найден.")

    return result


def archive_client(
    db: Session,
    *,
    client: Client,
    actor_user_id: UUID,
    reason: ArchiveReason,
    comment: str | None,
) -> Client:
    client.archived_at = datetime.now(UTC)
    client.archive_reason = reason
    client.archive_comment = comment
    client.archived_by_user_id = actor_user_id

    db.commit()

    result = get_archived_client_by_number(
        db,
        client.client_number,
    )

    if result is None:
        raise RuntimeError("Архивированный клиент не найден.")

    return result


def restore_client(
    db: Session,
    client: Client,
) -> Client:
    client.archived_at = None
    client.archive_reason = None
    client.archive_comment = None
    client.archived_by_user_id = None

    db.commit()

    result = get_client_by_number(
        db,
        client.client_number,
    )

    if result is None:
        raise RuntimeError("Восстановленный клиент не найден.")

    return result
