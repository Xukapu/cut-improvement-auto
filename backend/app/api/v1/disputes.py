from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    Path,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.api.deps import DbSession, StaffUser
from app.schemas.dispute import (
    DisputeCreate,
    DisputeListResponse,
    DisputePhotoListResponse,
    DisputePhotoResponse,
    DisputeResponse,
    DisputeUpdate,
)
from app.services.dispute import (
    add_dispute_photo,
    create_dispute,
    delete_dispute,
    delete_dispute_photo,
    get_dispute_photo_file,
    get_dispute_photos,
    get_order_disputes,
    update_dispute,
)

_SUMMARY_LIST_DISPUTES = (
    "\u0421\u043f\u043e\u0440\u043d\u044b\u0435 "
    "\u0441\u0438\u0442\u0443\u0430\u0446\u0438\u0438 "
    "\u0437\u0430\u043a\u0430\u0437-\u043d\u0430\u0440\u044f\u0434\u0430"
)

_SUMMARY_ADD_DISPUTE = (
    "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c "
    "\u0441\u043f\u043e\u0440\u043d\u0443\u044e "
    "\u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044e"
)

_SUMMARY_EDIT_DISPUTE = (
    "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c "
    "\u0441\u043f\u043e\u0440\u043d\u0443\u044e "
    "\u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044e"
)

_SUMMARY_DELETE_DISPUTE = (
    "\u0423\u0434\u0430\u043b\u0438\u0442\u044c "
    "\u0441\u043f\u043e\u0440\u043d\u0443\u044e "
    "\u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044e"
)

_SUMMARY_LIST_PHOTOS = (
    "\u0424\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 "
    "\u0441\u043f\u043e\u0440\u043d\u043e\u0439 "
    "\u0441\u0438\u0442\u0443\u0430\u0446\u0438\u0438"
)

_SUMMARY_ADD_PHOTO = (
    "\u041f\u0440\u0438\u043a\u0440\u0435\u043f\u0438\u0442\u044c "
    "\u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044e"
)

_SUMMARY_OPEN_PHOTO = (
    "\u041e\u0442\u043a\u0440\u044b\u0442\u044c "
    "\u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044e"
)

_SUMMARY_DELETE_PHOTO = (
    "\u0423\u0434\u0430\u043b\u0438\u0442\u044c "
    "\u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044e"
)


router = APIRouter(
    prefix="/work-orders",
    tags=["disputes"],
)

PositiveNumber = Annotated[
    int,
    Path(ge=1),
]


@router.get(
    "/{work_order_number}/disputes",
    response_model=DisputeListResponse,
    summary=_SUMMARY_LIST_DISPUTES,
)
def list_disputes(
    work_order_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> DisputeListResponse:
    return get_order_disputes(
        db,
        work_order_number,
    )


@router.post(
    "/{work_order_number}/disputes",
    response_model=DisputeResponse,
    status_code=status.HTTP_201_CREATED,
    summary=_SUMMARY_ADD_DISPUTE,
)
def add_dispute(
    work_order_number: PositiveNumber,
    payload: DisputeCreate,
    db: DbSession,
    _current_user: StaffUser,
) -> DisputeResponse:
    return create_dispute(
        db,
        work_order_number=work_order_number,
        payload=payload,
    )


@router.put(
    "/{work_order_number}/disputes/{dispute_number}",
    response_model=DisputeResponse,
    summary=_SUMMARY_EDIT_DISPUTE,
)
def edit_dispute(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    payload: DisputeUpdate,
    db: DbSession,
    _current_user: StaffUser,
) -> DisputeResponse:
    return update_dispute(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
        payload=payload,
    )


@router.delete(
    "/{work_order_number}/disputes/{dispute_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary=_SUMMARY_DELETE_DISPUTE,
)
def remove_dispute(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> None:
    delete_dispute(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
    )


@router.get(
    "/{work_order_number}/disputes/{dispute_number}/photos",
    response_model=DisputePhotoListResponse,
    summary=_SUMMARY_LIST_PHOTOS,
)
def list_dispute_photos(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> DisputePhotoListResponse:
    return get_dispute_photos(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
    )


@router.post(
    "/{work_order_number}/disputes/{dispute_number}/photos",
    response_model=DisputePhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary=_SUMMARY_ADD_PHOTO,
)
def upload_dispute_photo(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
    file: Annotated[UploadFile, File()],
) -> DisputePhotoResponse:
    return add_dispute_photo(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
        upload=file,
    )


@router.get(
    ("/{work_order_number}/disputes/{dispute_number}/photos/{photo_number}/file"),
    response_class=FileResponse,
    summary=_SUMMARY_OPEN_PHOTO,
)
def open_dispute_photo(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    photo_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> FileResponse:
    path, photo = get_dispute_photo_file(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
        photo_number=photo_number,
    )

    return FileResponse(
        path=path,
        media_type=photo.content_type,
        filename=photo.original_filename,
    )


@router.delete(
    ("/{work_order_number}/disputes/{dispute_number}/photos/{photo_number}"),
    status_code=status.HTTP_204_NO_CONTENT,
    summary=_SUMMARY_DELETE_PHOTO,
)
def remove_dispute_photo(
    work_order_number: PositiveNumber,
    dispute_number: PositiveNumber,
    photo_number: PositiveNumber,
    db: DbSession,
    _current_user: StaffUser,
) -> None:
    delete_dispute_photo(
        db,
        work_order_number=work_order_number,
        dispute_number=dispute_number,
        photo_number=photo_number,
    )
