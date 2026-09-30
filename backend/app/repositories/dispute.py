from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dispute import DisputePhoto, DisputeRecord


def get_dispute_by_number(
    db: Session,
    dispute_number: int,
) -> DisputeRecord | None:
    return db.scalar(
        select(DisputeRecord).where(
            DisputeRecord.dispute_number == dispute_number,
            DisputeRecord.deleted_at.is_(None),
        )
    )


def list_disputes_for_order(
    db: Session,
    work_order_id: UUID,
) -> list[DisputeRecord]:
    return list(
        db.scalars(
            select(DisputeRecord)
            .where(
                DisputeRecord.work_order_id == work_order_id,
                DisputeRecord.deleted_at.is_(None),
            )
            .order_by(
                DisputeRecord.recorded_at.asc(),
                DisputeRecord.dispute_number.asc(),
            )
        ).all()
    )


def get_photo_by_number(
    db: Session,
    photo_number: int,
) -> DisputePhoto | None:
    return db.scalar(
        select(DisputePhoto).where(
            DisputePhoto.photo_number == photo_number,
            DisputePhoto.deleted_at.is_(None),
        )
    )


def list_photos_for_dispute(
    db: Session,
    dispute_id: UUID,
) -> list[DisputePhoto]:
    return list(
        db.scalars(
            select(DisputePhoto)
            .where(
                DisputePhoto.dispute_id == dispute_id,
                DisputePhoto.deleted_at.is_(None),
            )
            .order_by(
                DisputePhoto.photo_number.asc(),
            )
        ).all()
    )
