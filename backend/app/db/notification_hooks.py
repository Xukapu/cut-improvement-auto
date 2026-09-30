from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.services.notification import (
    cancel_prepared_appointment_notifications,
    prepare_appointment_notifications,
)

_WATCHED_FIELDS = {
    "client_id",
    "vehicle_id",
    "appointment_date",
    "appointment_time",
    "status",
    "deleted_at",
}


def _appointment_changed(
    appointment: Appointment,
) -> bool:
    state = inspect(appointment)

    return any(state.attrs[field].history.has_changes() for field in _WATCHED_FIELDS)


@event.listens_for(
    Session,
    "before_flush",
)
def collect_appointment_notification_changes(
    session: Session,
    _flush_context,
    _instances,
) -> None:
    changes = session.info.setdefault(
        "_appointment_notification_changes",
        [],
    )

    known = {id(item) for item in changes}

    for item in session.new:
        if isinstance(item, Appointment) and id(item) not in known:
            changes.append(item)
            known.add(id(item))

    for item in session.dirty:
        if isinstance(item, Appointment) and id(item) not in known and _appointment_changed(item):
            changes.append(item)
            known.add(id(item))

    for item in session.deleted:
        if isinstance(item, Appointment) and id(item) not in known:
            changes.append(item)
            known.add(id(item))


@event.listens_for(
    Session,
    "after_flush_postexec",
)
def apply_appointment_notification_changes(
    session: Session,
    _flush_context,
) -> None:
    changes = session.info.pop(
        "_appointment_notification_changes",
        [],
    )

    if not changes:
        return

    for appointment in changes:
        if appointment.id is None:
            continue

        if appointment in session.deleted or appointment.deleted_at is not None:
            cancel_prepared_appointment_notifications(
                session,
                appointment.id,
            )
            continue

        prepare_appointment_notifications(
            session,
            appointment,
        )
