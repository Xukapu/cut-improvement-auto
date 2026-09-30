import re
from uuid import UUID

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.client import Client


def get_client_by_id(
    db: Session,
    client_id: UUID,
) -> Client | None:
    return db.scalar(
        select(Client)
        .options(joinedload(Client.referred_by))
        .where(
            Client.id == client_id,
            Client.deleted_at.is_(None),
            Client.archived_at.is_(None),
        )
    )


def get_client_by_number(
    db: Session,
    client_number: int,
) -> Client | None:
    return db.scalar(
        select(Client)
        .options(joinedload(Client.referred_by))
        .where(
            Client.client_number == client_number,
            Client.deleted_at.is_(None),
            Client.archived_at.is_(None),
        )
    )


def get_archived_client_by_number(
    db: Session,
    client_number: int,
) -> Client | None:
    return db.scalar(
        select(Client)
        .options(joinedload(Client.referred_by))
        .where(
            Client.client_number == client_number,
            Client.deleted_at.is_(None),
            Client.archived_at.is_not(None),
        )
    )


def build_search_filter(
    search: str | None,
) -> ColumnElement[bool] | None:
    if not search:
        return None

    value = search.strip()

    if not value:
        return None

    pattern = f"%{value}%"

    search_conditions = [
        Client.full_name.ilike(pattern),
        Client.phone_primary.ilike(pattern),
        Client.phone_secondary.ilike(pattern),
    ]

    if value.isdigit():
        search_conditions.append(Client.client_number == int(value))

    digits = re.sub(r"\D", "", value)

    if len(digits) >= 4:
        digit_pattern = f"%{digits}%"

        search_conditions.extend(
            [
                func.regexp_replace(
                    Client.phone_primary,
                    r"\D",
                    "",
                    "g",
                ).ilike(digit_pattern),
                func.regexp_replace(
                    func.coalesce(
                        Client.phone_secondary,
                        "",
                    ),
                    r"\D",
                    "",
                    "g",
                ).ilike(digit_pattern),
            ]
        )

    return or_(*search_conditions)


def list_clients(
    db: Session,
    *,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Client], int]:
    filters = [
        Client.deleted_at.is_(None),
        Client.archived_at.is_(None),
    ]

    search_filter = build_search_filter(search)

    if search_filter is not None:
        filters.append(search_filter)

    total = db.scalar(select(func.count()).select_from(Client).where(*filters))

    clients = list(
        db.scalars(
            select(Client)
            .options(joinedload(Client.referred_by))
            .where(*filters)
            .order_by(Client.client_number.asc())
            .limit(limit)
            .offset(offset)
        ).all()
    )

    return clients, int(total or 0)


def list_archived_clients(
    db: Session,
    *,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Client], int]:
    filters = [
        Client.deleted_at.is_(None),
        Client.archived_at.is_not(None),
    ]

    search_filter = build_search_filter(search)

    if search_filter is not None:
        filters.append(search_filter)

    total = db.scalar(select(func.count()).select_from(Client).where(*filters))

    clients = list(
        db.scalars(
            select(Client)
            .options(joinedload(Client.referred_by))
            .where(*filters)
            .order_by(
                Client.archived_at.desc(),
                Client.client_number.asc(),
            )
            .limit(limit)
            .offset(offset)
        ).all()
    )

    return clients, int(total or 0)
