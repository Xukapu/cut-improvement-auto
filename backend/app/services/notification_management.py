from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import (
    CustomerNotification,
    NotificationStatus,
)
from app.schemas.notification import (
    CustomerNotificationResponse,
)
from app.schemas.notification_management import (
    CustomerNotificationUpdate,
)
from app.services.notification import (
    notification_response,
)


def require_prepared_notification(
    db: Session,
    notification_id: UUID,
) -> CustomerNotification:
    item = db.scalar(
        select(CustomerNotification).where(
            CustomerNotification.id == notification_id,
            CustomerNotification.deleted_at.is_(None),
        )
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено.",
        )

    if item.status != NotificationStatus.PREPARED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Редактировать или удалять можно только подготовленные уведомления."),
        )

    return item


def update_prepared_notification(
    db: Session,
    *,
    notification_id: UUID,
    payload: CustomerNotificationUpdate,
) -> CustomerNotificationResponse:
    item = require_prepared_notification(
        db,
        notification_id,
    )

    item.message_text = payload.message_text.strip()

    item.scheduled_for = payload.scheduled_for

    db.commit()
    db.refresh(item)

    return notification_response(
        db,
        item,
    )


def delete_prepared_notification(
    db: Session,
    *,
    notification_id: UUID,
) -> None:
    item = require_prepared_notification(
        db,
        notification_id,
    )

    item.deleted_at = datetime.now(UTC)

    db.commit()
