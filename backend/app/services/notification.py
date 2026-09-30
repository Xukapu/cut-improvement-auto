# ruff: noqa: E501
from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.client_vehicle import ClientVehicle
from app.models.notification import (
    ClientNotificationPreference,
    CustomerNotification,
    NotificationChannel,
    NotificationKind,
    NotificationStatus,
    ServiceReminder,
    ServiceReminderStatus,
)
from app.models.vehicle import Vehicle
from app.schemas.notification import (
    CustomerNotificationResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    ServiceReminderCreate,
    ServiceReminderResponse,
)


def _enum_value(value) -> str:
    return getattr(value, "value", str(value))


def local_now() -> datetime:
    return datetime.now().astimezone()


def appointment_datetime(
    appointment: Appointment,
) -> datetime:
    now = local_now()

    return datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time,
    ).replace(
        tzinfo=now.tzinfo,
    )


def build_confirmation_message(
    appointment: Appointment,
) -> str:
    return (
        "\u0412\u044b \u0437\u0430\u043f\u0438\u0441\u0430\u043d\u044b "
        "\u0432 \u0426\u0423\u0422 Improvement Auto "
        f"{appointment.appointment_date.strftime('%d.%m.%Y')} "
        f"\u0432 {appointment.appointment_time.strftime('%H:%M')}."
    )


def build_appointment_reminder_message(
    appointment: Appointment,
) -> str:
    return (
        "\u041d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u0435\u043c: "
        f"{appointment.appointment_date.strftime('%d.%m.%Y')} "
        f"\u0432 {appointment.appointment_time.strftime('%H:%M')} "
        "\u0443 \u0432\u0430\u0441 \u0437\u0430\u043f\u0438\u0441\u044c "
        "\u0432 \u0426\u0423\u0422 Improvement Auto."
    )


def get_client_by_number(
    db: Session,
    client_number: int,
) -> Client:
    client = db.scalar(
        select(Client).where(
            Client.client_number == client_number,
            Client.deleted_at.is_(None),
        )
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="\u041a\u043b\u0438\u0435\u043d\u0442 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d.",
        )

    return client


def get_vehicle_by_number(
    db: Session,
    vehicle_number: int,
) -> Vehicle:
    vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.vehicle_number == vehicle_number,
            Vehicle.deleted_at.is_(None),
        )
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="\u0410\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d.",
        )

    return vehicle


def get_or_create_preferences(
    db: Session,
    client_id: UUID,
) -> ClientNotificationPreference:
    preferences = db.scalar(
        select(ClientNotificationPreference).where(
            ClientNotificationPreference.client_id == client_id,
            ClientNotificationPreference.deleted_at.is_(None),
        )
    )

    if preferences is not None:
        return preferences

    preferences = ClientNotificationPreference(
        client_id=client_id,
    )

    db.add(preferences)
    db.flush()

    return preferences


def preference_response(
    client: Client,
    preferences: ClientNotificationPreference,
) -> NotificationPreferenceResponse:
    return NotificationPreferenceResponse(
        client_id=client.id,
        client_number=client.client_number,
        client_name=client.full_name,
        phone_primary=client.phone_primary,
        sms_enabled=preferences.sms_enabled,
        max_enabled=preferences.max_enabled,
        max_connected=bool(preferences.max_user_id),
        appointment_confirmation_enabled=(preferences.appointment_confirmation_enabled),
        appointment_reminder_enabled=(preferences.appointment_reminder_enabled),
        service_reminder_enabled=(preferences.service_reminder_enabled),
    )


def get_preferences_by_client_number(
    db: Session,
    client_number: int,
) -> NotificationPreferenceResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    preferences = get_or_create_preferences(
        db,
        client.id,
    )

    db.commit()

    return preference_response(
        client,
        preferences,
    )


def update_preferences_by_client_number(
    db: Session,
    client_number: int,
    payload: NotificationPreferenceUpdate,
) -> NotificationPreferenceResponse:
    client = get_client_by_number(
        db,
        client_number,
    )

    preferences = get_or_create_preferences(
        db,
        client.id,
    )

    preferences.sms_enabled = payload.sms_enabled
    preferences.max_enabled = payload.max_enabled
    preferences.appointment_confirmation_enabled = payload.appointment_confirmation_enabled
    preferences.appointment_reminder_enabled = payload.appointment_reminder_enabled
    preferences.service_reminder_enabled = payload.service_reminder_enabled

    db.flush()

    sync_future_appointments_for_client(
        db,
        client.id,
    )

    db.commit()
    db.refresh(preferences)

    return preference_response(
        client,
        preferences,
    )


def enabled_channels(
    preferences: ClientNotificationPreference,
) -> list[NotificationChannel]:
    channels: list[NotificationChannel] = []

    if preferences.sms_enabled:
        channels.append(NotificationChannel.SMS)

    if preferences.max_enabled and preferences.max_user_id:
        channels.append(NotificationChannel.MAX)

    return channels


def cancel_prepared_appointment_notifications(
    db: Session,
    appointment_id: UUID,
) -> int:
    items = list(
        db.scalars(
            select(CustomerNotification).where(
                CustomerNotification.appointment_id == appointment_id,
                CustomerNotification.status == NotificationStatus.PREPARED,
                CustomerNotification.kind.in_(
                    [
                        NotificationKind.APPOINTMENT_CONFIRMATION,
                        NotificationKind.APPOINTMENT_REMINDER,
                    ]
                ),
                CustomerNotification.deleted_at.is_(None),
            )
        ).all()
    )

    for item in items:
        item.status = NotificationStatus.CANCELLED

    return len(items)


def prepare_appointment_notifications(
    db: Session,
    appointment: Appointment,
    *,
    now: datetime | None = None,
) -> int:
    if now is None:
        now = local_now()

    cancel_prepared_appointment_notifications(
        db,
        appointment.id,
    )

    if appointment.deleted_at is not None:
        return 0

    if _enum_value(appointment.status) != "scheduled":
        return 0

    appointment_at = appointment_datetime(appointment)

    if appointment_at <= now:
        return 0

    preferences = get_or_create_preferences(
        db,
        appointment.client_id,
    )

    channels = enabled_channels(preferences)

    if not channels:
        return 0

    created = 0

    for channel in channels:
        if preferences.appointment_confirmation_enabled:
            db.add(
                CustomerNotification(
                    client_id=appointment.client_id,
                    vehicle_id=appointment.vehicle_id,
                    appointment_id=appointment.id,
                    channel=channel,
                    kind=(NotificationKind.APPOINTMENT_CONFIRMATION),
                    status=NotificationStatus.PREPARED,
                    message_text=build_confirmation_message(appointment),
                    scheduled_for=now,
                )
            )

            created += 1

        if preferences.appointment_reminder_enabled:
            reminder_at = appointment_at - timedelta(hours=2)

            if reminder_at < now:
                reminder_at = now

            db.add(
                CustomerNotification(
                    client_id=appointment.client_id,
                    vehicle_id=appointment.vehicle_id,
                    appointment_id=appointment.id,
                    channel=channel,
                    kind=(NotificationKind.APPOINTMENT_REMINDER),
                    status=NotificationStatus.PREPARED,
                    message_text=(build_appointment_reminder_message(appointment)),
                    scheduled_for=reminder_at,
                )
            )

            created += 1

    return created


def sync_future_appointments_for_client(
    db: Session,
    client_id: UUID,
) -> int:
    now = local_now()

    appointments = list(
        db.scalars(
            select(Appointment)
            .where(
                Appointment.client_id == client_id,
                Appointment.status == "scheduled",
                Appointment.deleted_at.is_(None),
                Appointment.appointment_date >= now.date(),
            )
            .order_by(
                Appointment.appointment_date.asc(),
                Appointment.appointment_time.asc(),
            )
        ).all()
    )

    created = 0

    for appointment in appointments:
        created += prepare_appointment_notifications(
            db,
            appointment,
            now=now,
        )

    return created


def notification_response(
    db: Session,
    item: CustomerNotification,
) -> CustomerNotificationResponse:
    client = db.get(
        Client,
        item.client_id,
    )

    vehicle = (
        db.get(
            Vehicle,
            item.vehicle_id,
        )
        if item.vehicle_id
        else None
    )

    appointment = (
        db.get(
            Appointment,
            item.appointment_id,
        )
        if item.appointment_id
        else None
    )

    return CustomerNotificationResponse(
        id=item.id,
        client_number=(client.client_number if client is not None else None),
        client_name=(client.full_name if client is not None else None),
        vehicle_number=(vehicle.vehicle_number if vehicle is not None else None),
        appointment_number=(appointment.appointment_number if appointment is not None else None),
        channel=item.channel,
        kind=item.kind,
        status=item.status,
        message_text=item.message_text,
        scheduled_for=item.scheduled_for,
        sent_at=item.sent_at,
        error_message=item.error_message,
        created_at=item.created_at,
    )


def list_notifications(
    db: Session,
    *,
    client_number: int | None = None,
    notification_status: NotificationStatus | None = None,
    kind: NotificationKind | None = None,
    limit: int = 100,
) -> list[CustomerNotificationResponse]:
    statement = (
        select(CustomerNotification)
        .where(CustomerNotification.deleted_at.is_(None))
        .order_by(CustomerNotification.scheduled_for.desc())
        .limit(limit)
    )

    if client_number is not None:
        client = get_client_by_number(
            db,
            client_number,
        )

        statement = statement.where(CustomerNotification.client_id == client.id)

    if notification_status is not None:
        statement = statement.where(CustomerNotification.status == notification_status)

    if kind is not None:
        statement = statement.where(CustomerNotification.kind == kind)

    items = list(db.scalars(statement).all())

    return [
        notification_response(
            db,
            item,
        )
        for item in items
    ]


def validate_current_ownership(
    db: Session,
    client: Client,
    vehicle: Vehicle,
) -> None:
    ownership = db.scalar(
        select(ClientVehicle).where(
            ClientVehicle.client_id == client.id,
            ClientVehicle.vehicle_id == vehicle.id,
            ClientVehicle.is_current.is_(True),
            ClientVehicle.deleted_at.is_(None),
        )
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "\u0410\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c "
                "\u043d\u0435 \u043f\u0440\u0438\u0432\u044f\u0437\u0430\u043d "
                "\u043a \u044d\u0442\u043e\u043c\u0443 "
                "\u043a\u043b\u0438\u0435\u043d\u0442\u0443 "
                "\u043a\u0430\u043a \u0442\u0435\u043a\u0443\u0449\u0438\u0439."
            ),
        )


def service_reminder_response(
    db: Session,
    reminder: ServiceReminder,
) -> ServiceReminderResponse:
    client = db.get(
        Client,
        reminder.client_id,
    )

    vehicle = db.get(
        Vehicle,
        reminder.vehicle_id,
    )

    return ServiceReminderResponse(
        id=reminder.id,
        client_number=client.client_number,
        client_name=client.full_name,
        vehicle_number=vehicle.vehicle_number,
        vehicle_name=(f"{vehicle.brand} {vehicle.model}"),
        work_name=reminder.work_name,
        due_date=reminder.due_date,
        due_mileage=reminder.due_mileage,
        message_text=reminder.message_text,
        status=reminder.status,
        completed_at=reminder.completed_at,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at,
    )


def create_service_reminder(
    db: Session,
    payload: ServiceReminderCreate,
) -> ServiceReminderResponse:
    if payload.due_date is None and payload.due_mileage is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "\u041d\u0443\u0436\u043d\u043e "
                "\u0443\u043a\u0430\u0437\u0430\u0442\u044c "
                "\u0434\u0430\u0442\u0443 "
                "\u0438/\u0438\u043b\u0438 "
                "\u043f\u0440\u043e\u0431\u0435\u0433 "
                "\u0434\u043b\u044f "
                "\u043d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u044f."
            ),
        )

    client = get_client_by_number(
        db,
        payload.client_number,
    )

    vehicle = get_vehicle_by_number(
        db,
        payload.vehicle_number,
    )

    validate_current_ownership(
        db,
        client,
        vehicle,
    )

    reminder = ServiceReminder(
        client_id=client.id,
        vehicle_id=vehicle.id,
        work_name=payload.work_name,
        due_date=payload.due_date,
        due_mileage=payload.due_mileage,
        message_text=payload.message_text,
        status=ServiceReminderStatus.PLANNED,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return service_reminder_response(
        db,
        reminder,
    )


def list_service_reminders(
    db: Session,
    *,
    client_number: int | None = None,
    reminder_status: ServiceReminderStatus | None = None,
) -> list[ServiceReminderResponse]:
    statement = (
        select(ServiceReminder)
        .where(ServiceReminder.deleted_at.is_(None))
        .order_by(
            ServiceReminder.due_date.asc().nulls_last(),
            ServiceReminder.created_at.desc(),
        )
    )

    if client_number is not None:
        client = get_client_by_number(
            db,
            client_number,
        )

        statement = statement.where(ServiceReminder.client_id == client.id)

    if reminder_status is not None:
        statement = statement.where(ServiceReminder.status == reminder_status)

    reminders = list(db.scalars(statement).all())

    return [
        service_reminder_response(
            db,
            reminder,
        )
        for reminder in reminders
    ]


def service_reminder_is_due(
    *,
    due_date: date | None,
    due_mileage: int | None,
    current_date: date,
    current_mileage: int | None,
) -> bool:
    by_date = due_date is not None and current_date >= due_date

    by_mileage = (
        due_mileage is not None and current_mileage is not None and current_mileage >= due_mileage
    )

    return by_date or by_mileage


def prepare_due_service_reminders(
    db: Session,
) -> int:
    now = local_now()

    reminders = list(
        db.scalars(
            select(ServiceReminder).where(
                ServiceReminder.status == ServiceReminderStatus.PLANNED,
                ServiceReminder.deleted_at.is_(None),
                or_(
                    ServiceReminder.due_date <= now.date(),
                    ServiceReminder.due_mileage.is_not(None),
                ),
            )
        ).all()
    )

    prepared_count = 0

    for reminder in reminders:
        vehicle = db.get(
            Vehicle,
            reminder.vehicle_id,
        )

        if vehicle is None:
            continue

        if not service_reminder_is_due(
            due_date=reminder.due_date,
            due_mileage=reminder.due_mileage,
            current_date=now.date(),
            current_mileage=vehicle.mileage,
        ):
            continue

        preferences = get_or_create_preferences(
            db,
            reminder.client_id,
        )

        if not preferences.service_reminder_enabled:
            continue

        channels = enabled_channels(preferences)

        if not channels:
            continue

        for channel in channels:
            db.add(
                CustomerNotification(
                    client_id=reminder.client_id,
                    vehicle_id=reminder.vehicle_id,
                    appointment_id=None,
                    channel=channel,
                    kind=NotificationKind.SERVICE_REMINDER,
                    status=NotificationStatus.PREPARED,
                    message_text=reminder.message_text,
                    scheduled_for=now,
                )
            )

            prepared_count += 1

        reminder.status = ServiceReminderStatus.COMPLETED
        reminder.completed_at = now

    db.commit()

    return prepared_count


def cancel_service_reminder(
    db: Session,
    reminder_id: UUID,
) -> ServiceReminderResponse:
    reminder = db.scalar(
        select(ServiceReminder).where(
            ServiceReminder.id == reminder_id,
            ServiceReminder.deleted_at.is_(None),
        )
    )

    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u043e\u0435 "
                "\u043d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435 "
                "\u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e."
            ),
        )

    if reminder.status == ServiceReminderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "\u0423\u0436\u0435 "
                "\u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u043d\u043e\u0435 "
                "\u043d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435 "
                "\u043d\u0435\u043b\u044c\u0437\u044f "
                "\u043e\u0442\u043c\u0435\u043d\u0438\u0442\u044c."
            ),
        )

    reminder.status = ServiceReminderStatus.CANCELLED

    db.commit()
    db.refresh(reminder)

    return service_reminder_response(
        db,
        reminder,
    )
