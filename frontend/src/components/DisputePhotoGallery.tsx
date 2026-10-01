import {
  Camera,
  ChevronLeft,
  ChevronRight,
  Download,
  Trash2,
  X,
} from "lucide-react";
import {
  useState,
} from "react";
import type {
  ChangeEvent,
} from "react";

import {
  disputePhotoUrl,
} from "../api/workOrders";
import type {
  DisputePhoto,
} from "../types/workOrder";


type Props = {
  workOrderNumber: number;
  disputeNumber: number;

  photos: DisputePhoto[];

  canEdit: boolean;

  onUpload: (
    file: File,
  ) => Promise<void>;

  onDelete: (
    photo: DisputePhoto,
  ) => Promise<void>;
};


export function DisputePhotoGallery({
  workOrderNumber,
  disputeNumber,
  photos,
  canEdit,
  onUpload,
  onDelete,
}: Props) {
  const [
    activeIndex,
    setActiveIndex,
  ] = useState<
    number | null
  >(null);

  const [
    uploading,
    setUploading,
  ] = useState(false);

  const activePhoto =
    activeIndex === null
      ? null
      : photos[
          activeIndex
        ] ?? null;


  function photoUrl(
    photo: DisputePhoto,
  ): string {
    return disputePhotoUrl(
      workOrderNumber,
      disputeNumber,
      photo.photo_number,
    );
  }


  async function handleUpload(
    event:
      ChangeEvent<HTMLInputElement>,
  ) {
    const input =
      event.currentTarget;

    const file =
      input.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);

    try {
      await onUpload(file);
    } finally {
      setUploading(false);
      input.value = "";
    }
  }


  async function handleDelete(
    photo: DisputePhoto,
  ) {
    await onDelete(photo);

    if (
      activePhoto
        ?.photo_number ===
      photo.photo_number
    ) {
      setActiveIndex(null);
    }
  }


  function showPrevious() {
    if (
      activeIndex === null ||
      photos.length < 2
    ) {
      return;
    }

    setActiveIndex(
      (
        activeIndex -
        1 +
        photos.length
      ) %
        photos.length,
    );
  }


  function showNext() {
    if (
      activeIndex === null ||
      photos.length < 2
    ) {
      return;
    }

    setActiveIndex(
      (
        activeIndex +
        1
      ) %
        photos.length,
    );
  }


  return (
    <>
      <div className="wo-photo-area">
        <div className="wo-photo-heading">
          <div>
            <strong>
              Фотографии
            </strong>

            <span>
              {photos.length}
            </span>
          </div>

          {canEdit && (
            <label className="wo-photo-upload">
              <Camera size={14} />

              {uploading
                ? "Загружаем..."
                : "Добавить фото"}

              <input
                accept="image/*"
                disabled={
                  uploading
                }
                type="file"
                onChange={(event) => {
                  void handleUpload(
                    event,
                  );
                }}
              />
            </label>
          )}
        </div>


        {photos.length === 0 ? (
          <div className="wo-photo-empty">
            <Camera size={20} />

            <span>
              Фото пока не прикреплены.
            </span>
          </div>
        ) : (
          <div className="wo-photo-grid">
            {photos.map(
              (
                photo,
                index,
              ) => (
                <div
                  className="wo-photo-thumb-wrap"
                  key={
                    photo.photo_number
                  }
                >
                  <button
                    className="wo-photo-thumb"
                    onClick={() => {
                      setActiveIndex(
                        index,
                      );
                    }}
                    title={
                      photo
                        .original_filename
                    }
                    type="button"
                  >
                    <img
                      alt={
                        photo
                          .original_filename
                      }
                      loading="lazy"
                      src={
                        photoUrl(
                          photo,
                        )
                      }
                    />

                    <span>
                      Открыть
                    </span>
                  </button>

                  {canEdit && (
                    <button
                      aria-label="Удалить фотографию"
                      className="wo-photo-thumb-delete"
                      onClick={() => {
                        void handleDelete(
                          photo,
                        );
                      }}
                      title="Удалить"
                      type="button"
                    >
                      <Trash2
                        size={13}
                      />
                    </button>
                  )}
                </div>
              ),
            )}
          </div>
        )}
      </div>


      {activePhoto && (
        <div
          aria-modal="true"
          className="wo-lightbox"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              setActiveIndex(
                null,
              );
            }
          }}
          role="dialog"
        >
          <div className="wo-lightbox-shell">
            <div className="wo-lightbox-header">
              <div>
                <strong>
                  {
                    activePhoto
                      .original_filename
                  }
                </strong>

                <span>
                  Фото{" "}
                  {
                    (
                      activeIndex ??
                      0
                    ) + 1
                  }{" "}
                  из{" "}
                  {photos.length}
                </span>
              </div>

              <button
                aria-label="Закрыть"
                className="wo-lightbox-close"
                onClick={() => {
                  setActiveIndex(
                    null,
                  );
                }}
                type="button"
              >
                <X size={20} />
              </button>
            </div>


            <div className="wo-lightbox-image-area">
              {photos.length > 1 && (
                <button
                  aria-label="Предыдущее фото"
                  className="wo-lightbox-arrow wo-lightbox-arrow-left"
                  onClick={
                    showPrevious
                  }
                  type="button"
                >
                  <ChevronLeft
                    size={26}
                  />
                </button>
              )}

              <img
                alt={
                  activePhoto
                    .original_filename
                }
                src={
                  photoUrl(
                    activePhoto,
                  )
                }
              />

              {photos.length > 1 && (
                <button
                  aria-label="Следующее фото"
                  className="wo-lightbox-arrow wo-lightbox-arrow-right"
                  onClick={
                    showNext
                  }
                  type="button"
                >
                  <ChevronRight
                    size={26}
                  />
                </button>
              )}
            </div>


            <div className="wo-lightbox-footer">
              <span>
                {
                  activePhoto
                    .original_filename
                }
              </span>

              <a
                className="wo-photo-download"
                download={
                  activePhoto
                    .original_filename
                }
                href={
                  photoUrl(
                    activePhoto,
                  )
                }
              >
                <Download
                  size={15}
                />

                Скачать
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}