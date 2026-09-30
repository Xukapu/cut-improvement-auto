from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import (
    DbSession,
    ManagerUser,
    StaffUser,
)
from app.models.notification import (
    NotificationKind,
    NotificationStatus,
    ServiceReminderStatus,
)
from app.schemas.notification import (
    CustomerNotificationResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    PrepareDueNotificationsResponse,
    ServiceReminderCreate,
    ServiceReminderResponse,
)
from app.services.notification import (
    cancel_service_reminder,
    create_service_reminder,
    get_preferences_by_client_number,
    list_notifications,
    list_service_reminders,
    prepare_due_service_reminders,
    update_preferences_by_client_number,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get(
    "/clients/{client_number}/preferences",
    response_model=NotificationPreferenceResponse,
    summary="Настройки уведомлений клиента",
)
def get_client_preferences(
    client_number: int,
    db: DbSession,
    _current_user: StaffUser,
) -> NotificationPreferenceResponse:
    return get_preferences_by_client_number(
        db,
        client_number,
    )


@router.put(
    "/clients/{client_number}/preferences",
    response_model=NotificationPreferenceResponse,
    summary="Изменить настройки уведомлений клиента",
)
def update_client_preferences(
    client_number: int,
    payload: NotificationPreferenceUpdate,
    db: DbSession,
    _current_user: ManagerUser,
) -> NotificationPreferenceResponse:
    return update_preferences_by_client_number(
        db,
        client_number,
        payload,
    )


@router.get(
    "",
    response_model=list[CustomerNotificationResponse],
    summary="Очередь уведомлений клиентам",
)
def get_notifications(
    db: DbSession,
    _current_user: StaffUser,
    client_number: int | None = None,
    notification_status: NotificationStatus | None = None,
    kind: NotificationKind | None = None,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
) -> list[CustomerNotificationResponse]:
    return list_notifications(
        db,
        client_number=client_number,
        notification_status=notification_status,
        kind=kind,
        limit=limit,
    )


@router.post(
    "/service-reminders",
    response_model=ServiceReminderResponse,
    status_code=201,
    summary="Создать сервисное напоминание",
)
def add_service_reminder(
    payload: ServiceReminderCreate,
    db: DbSession,
    _current_user: ManagerUser,
) -> ServiceReminderResponse:
    return create_service_reminder(
        db,
        payload,
    )


@router.get(
    "/service-reminders",
    response_model=list[ServiceReminderResponse],
    summary="Сервисные напоминания",
)
def get_service_reminders(
    db: DbSession,
    _current_user: StaffUser,
    client_number: int | None = None,
    reminder_status: ServiceReminderStatus | None = None,
) -> list[ServiceReminderResponse]:
    return list_service_reminders(
        db,
        client_number=client_number,
        reminder_status=reminder_status,
    )


@router.post(
    "/service-reminders/prepare-due",
    response_model=PrepareDueNotificationsResponse,
    summary="Подготовить наступившие сервисные уведомления",
)
def prepare_due(
    db: DbSession,
    _current_user: ManagerUser,
) -> PrepareDueNotificationsResponse:
    count = prepare_due_service_reminders(db)

    return PrepareDueNotificationsResponse(
        prepared_count=count,
    )


@router.post(
    "/service-reminders/{reminder_id}/cancel",
    response_model=ServiceReminderResponse,
    summary="Отменить сервисное напоминание",
)
def cancel_reminder(
    reminder_id: UUID,
    db: DbSession,
    _current_user: ManagerUser,
) -> ServiceReminderResponse:
    return cancel_service_reminder(
        db,
        reminder_id,
    )
