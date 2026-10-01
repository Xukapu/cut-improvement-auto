from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.work_item import WorkItem, WorkItemAssignment


def get_work_item_by_number(
    db: Session,
    work_item_number: int,
) -> WorkItem | None:
    return db.scalar(
        select(WorkItem).where(
            WorkItem.work_item_number == work_item_number,
            WorkItem.deleted_at.is_(None),
        )
    )


def list_work_items_for_order(
    db: Session,
    work_order_id,
) -> list[WorkItem]:
    return list(
        db.scalars(
            select(WorkItem)
            .where(
                WorkItem.work_order_id == work_order_id,
                WorkItem.deleted_at.is_(None),
            )
            .order_by(WorkItem.work_item_number.asc())
        ).all()
    )


def list_assignments_for_work(
    db: Session,
    work_item_id,
) -> list[
    tuple[
        WorkItemAssignment,
        Employee,
    ]
]:
    rows = db.execute(
        select(
            WorkItemAssignment,
            Employee,
        )
        .join(
            Employee,
            Employee.id == WorkItemAssignment.employee_id,
        )
        .where(
            WorkItemAssignment.work_item_id == work_item_id,
            WorkItemAssignment.deleted_at.is_(None),
        )
        .order_by(Employee.employee_number.asc())
    ).all()

    return [(row[0], row[1]) for row in rows]
