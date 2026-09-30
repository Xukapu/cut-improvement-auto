from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def list_audit_logs(
    db: Session,
    *,
    entity_type: str | None = None,
    entity_number: int | None = None,
    action: str | None = None,
    actor_login: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    conditions = []

    if entity_type is not None:
        conditions.append(AuditLog.entity_type == entity_type)

    if entity_number is not None:
        conditions.append(AuditLog.entity_number == entity_number)

    if action is not None:
        conditions.append(AuditLog.action == action)

    if actor_login is not None:
        conditions.append(func.lower(AuditLog.actor_login) == actor_login.lower())

    if date_from is not None:
        conditions.append(
            cast(
                AuditLog.created_at,
                Date,
            )
            >= date_from
        )

    if date_to is not None:
        conditions.append(
            cast(
                AuditLog.created_at,
                Date,
            )
            <= date_to
        )

    query = (
        select(AuditLog)
        .where(*conditions)
        .order_by(
            AuditLog.created_at.desc(),
            AuditLog.event_number.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    count_query = select(func.count()).select_from(AuditLog).where(*conditions)

    items = list(db.scalars(query).all())

    total = int(db.scalar(count_query) or 0)

    return items, total
