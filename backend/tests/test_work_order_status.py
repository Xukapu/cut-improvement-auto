from app.models.work_order import WorkOrderStatus
from app.services.work_order import _ALLOWED_STATUS_TRANSITIONS


def test_planned_can_only_start() -> None:
    assert _ALLOWED_STATUS_TRANSITIONS[WorkOrderStatus.PLANNED] == frozenset(
        {
            WorkOrderStatus.IN_PROGRESS,
        }
    )


def test_in_progress_can_become_ready() -> None:
    assert _ALLOWED_STATUS_TRANSITIONS[WorkOrderStatus.IN_PROGRESS] == frozenset(
        {
            WorkOrderStatus.READY,
        }
    )


def test_ready_can_return_to_work_or_be_issued() -> None:
    assert _ALLOWED_STATUS_TRANSITIONS[WorkOrderStatus.READY] == frozenset(
        {
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.ISSUED,
        }
    )


def test_issued_is_final() -> None:
    assert not _ALLOWED_STATUS_TRANSITIONS[WorkOrderStatus.ISSUED]
