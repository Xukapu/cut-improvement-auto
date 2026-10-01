from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import (
    DbSession,
    ManagerUser,
)
from app.schemas.notification import (
    CustomerNotificationResponse,
)
from app.schemas.notification_management import (
    CustomerNotificationUpdate,
)
from app.services.notification_management import (
    delete_prepared_notification,
    update_prepared_notification,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.put(
    "/{notification_id}",
    response_model=CustomerNotificationResponse,
    summary="Изменить подготовленное уведомление",
)
def edit_notification(
    notification_id: UUID,
    payload: CustomerNotificationUpdate,
    db: DbSession,
    _current_user: ManagerUser,
) -> CustomerNotificationResponse:
    return update_prepared_notification(
        db,
        notification_id=notification_id,
        payload=payload,
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить подготовленное уведомление",
)
def remove_notification(
    notification_id: UUID,
    db: DbSession,
    _current_user: ManagerUser,
) -> None:
    delete_prepared_notification(
        db,
        notification_id=notification_id,
    )
