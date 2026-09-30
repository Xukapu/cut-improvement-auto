from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.services.audit import (
    audit_json_value,
    get_audit_actor,
    record_audit_event,
)

_PENDING_KEY = "_pending_audit_events"

_ALWAYS_EXCLUDED_FIELDS = {
    "id",
    "created_at",
    "updated_at",
}


_ENTITY_MAP: dict[str, tuple[str, str | None]] = {
    "app_users": (
        "user",
        None,
    ),
    "clients": (
        "client",
        "client_number",
    ),
    "vehicles": (
        "vehicle",
        "vehicle_number",
    ),
    "client_vehicles": (
        "vehicle_owner",
        None,
    ),
    "appointments": (
        "appointment",
        "appointment_number",
    ),
    "work_orders": (
        "work_order",
        "work_order_number",
    ),
    "employees": (
        "employee",
        "employee_number",
    ),
    "employee_rates": (
        "employee_rate",
        None,
    ),
    "work_items": (
        "work_item",
        "work_item_number",
    ),
    "work_item_assignments": (
        "work_assignment",
        None,
    ),
    "parts": (
        "part",
        "part_number",
    ),
    "recommended_works": (
        "recommended_work",
        "recommended_work_number",
    ),
    "dispute_records": (
        "dispute",
        "dispute_number",
    ),
    "dispute_photos": (
        "dispute_photo",
        "photo_number",
    ),
    "payments": (
        "payment",
        "payment_number",
    ),
}


def is_sensitive_field(
    key: str,
) -> bool:
    normalized = key.lower()

    if normalized in _ALWAYS_EXCLUDED_FIELDS:
        return True

    sensitive_fragments = (
        "password",
        "token",
        "secret",
    )

    return any(fragment in normalized for fragment in sensitive_fragments)


def tracked_entity(
    obj: Any,
) -> tuple[str, str | None] | None:
    table = getattr(
        obj,
        "__tablename__",
        None,
    )

    if table is None:
        return None

    return _ENTITY_MAP.get(table)


def snapshot_object(
    obj: Any,
) -> dict[str, Any]:
    state = inspect(obj)

    result: dict[str, Any] = {}

    for attribute in state.mapper.column_attrs:
        key = attribute.key

        if is_sensitive_field(key):
            continue

        result[key] = audit_json_value(
            getattr(
                obj,
                key,
                None,
            )
        )

    return result


def changed_values(
    obj: Any,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
]:
    state = inspect(obj)

    old_values: dict[str, Any] = {}
    new_values: dict[str, Any] = {}

    for attribute in state.mapper.column_attrs:
        key = attribute.key

        if is_sensitive_field(key):
            continue

        history = state.attrs[key].history

        if not history.has_changes():
            continue

        old_value = None

        if history.deleted:
            old_value = history.deleted[0]

        new_value = getattr(
            obj,
            key,
            None,
        )

        old_values[key] = audit_json_value(old_value)

        new_values[key] = audit_json_value(new_value)

    return old_values, new_values


def classify_audit_action(
    *,
    entity_type: str,
    old_values: dict[str, Any] | None,
    new_values: dict[str, Any] | None,
    is_new: bool,
    is_deleted: bool,
) -> str:
    if is_new:
        return "create"

    if is_deleted:
        return "delete"

    changed = set()

    if old_values:
        changed.update(old_values)

    if new_values:
        changed.update(new_values)

    if "deleted_at" in changed:
        deleted_value = None

        if new_values:
            deleted_value = new_values.get("deleted_at")

        if deleted_value is None:
            return "restore"

        return "delete"

    if "archived_at" in changed or "is_archived" in changed:
        archived = None

        if new_values:
            if "archived_at" in new_values:
                archived = new_values.get("archived_at")
            else:
                archived = new_values.get("is_archived")

        if archived:
            return "archive"

        return "restore"

    if "status" in changed:
        return "status_change"

    if "internal_mark" in changed:
        return "internal_mark_change"

    if entity_type == "payment":
        return "payment_change"

    if entity_type == "employee_rate":
        return "rate_change"

    return "update"


def entity_number(
    obj: Any,
    number_field: str | None,
) -> int | None:
    if number_field is None:
        return None

    value = getattr(
        obj,
        number_field,
        None,
    )

    if value is None:
        return None

    return int(value)


@event.listens_for(
    Session,
    "before_flush",
)
def collect_audit_events(
    session: Session,
    _flush_context: Any,
    _instances: Any,
) -> None:
    pending: list[dict[str, Any]] = []

    actor = get_audit_actor(session)

    for obj in session.new:
        if isinstance(obj, AuditLog):
            continue

        entity = tracked_entity(obj)

        if entity is None:
            continue

        entity_type, number_field = entity

        pending.append(
            {
                "obj": obj,
                "actor": actor,
                "entity_type": entity_type,
                "number_field": number_field,
                "action": "create",
                "mode": "create",
                "old_values": None,
                "new_values": None,
            }
        )

    for obj in session.dirty:
        if isinstance(obj, AuditLog):
            continue

        entity = tracked_entity(obj)

        if entity is None:
            continue

        old_values, new_values = changed_values(obj)

        if not old_values and not new_values:
            continue

        entity_type, number_field = entity

        action = classify_audit_action(
            entity_type=entity_type,
            old_values=old_values,
            new_values=new_values,
            is_new=False,
            is_deleted=False,
        )

        pending.append(
            {
                "obj": obj,
                "actor": actor,
                "entity_type": entity_type,
                "number_field": number_field,
                "action": action,
                "mode": "update",
                "old_values": old_values,
                "new_values": new_values,
            }
        )

    for obj in session.deleted:
        if isinstance(obj, AuditLog):
            continue

        entity = tracked_entity(obj)

        if entity is None:
            continue

        entity_type, number_field = entity

        pending.append(
            {
                "obj": obj,
                "actor": actor,
                "entity_type": entity_type,
                "number_field": number_field,
                "action": "delete",
                "mode": "delete",
                "old_values": snapshot_object(obj),
                "new_values": None,
            }
        )

    if pending:
        session.info.setdefault(
            _PENDING_KEY,
            [],
        ).extend(pending)


@event.listens_for(
    Session,
    "after_flush_postexec",
)
def write_audit_events(
    session: Session,
    _flush_context: Any,
) -> None:
    pending = session.info.pop(
        _PENDING_KEY,
        [],
    )

    for item in pending:
        obj = item["obj"]

        new_values = item["new_values"]

        if item["mode"] == "create":
            new_values = snapshot_object(obj)

        record_audit_event(
            session,
            actor=item["actor"],
            action=item["action"],
            entity_type=item["entity_type"],
            entity_id=getattr(
                obj,
                "id",
                None,
            ),
            entity_number=entity_number(
                obj,
                item["number_field"],
            ),
            old_values=item["old_values"],
            new_values=new_values,
        )
