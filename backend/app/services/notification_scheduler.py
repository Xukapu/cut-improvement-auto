import asyncio
import logging
import os
from contextlib import suppress

from app.db.session import SessionLocal as SessionFactory
from app.services.notification import prepare_due_service_reminders

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60

_scheduler_task: asyncio.Task[None] | None = None


def process_due_service_reminders_once() -> int:
    with SessionFactory() as db:
        return prepare_due_service_reminders(db)


async def _notification_scheduler_loop() -> None:
    while True:
        try:
            prepared_count = await asyncio.to_thread(process_due_service_reminders_once)

            if prepared_count:
                logger.info(
                    "Prepared %s due customer notifications",
                    prepared_count,
                )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception("Automatic notification check failed")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def start_notification_scheduler() -> None:
    global _scheduler_task

    if os.getenv("PYTEST_CURRENT_TEST"):
        return

    if _scheduler_task is not None and not _scheduler_task.done():
        return

    logger.info("Customer notification scheduler started")

    _scheduler_task = asyncio.create_task(
        _notification_scheduler_loop(),
        name="customer-notification-scheduler",
    )


async def stop_notification_scheduler() -> None:
    global _scheduler_task

    if _scheduler_task is None:
        return

    _scheduler_task.cancel()

    with suppress(asyncio.CancelledError):
        await _scheduler_task

    _scheduler_task = None

    logger.info("Customer notification scheduler stopped")
