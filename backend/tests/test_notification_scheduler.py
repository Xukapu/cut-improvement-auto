from app.services import notification_scheduler


class DummySession:
    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False


class DummySessionFactory:
    def __call__(self):
        return DummySession()


def test_scheduler_interval_is_one_minute() -> None:
    assert notification_scheduler.CHECK_INTERVAL_SECONDS == 60


def test_scheduler_processes_due_reminders(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        notification_scheduler,
        "SessionFactory",
        DummySessionFactory(),
    )

    calls = []

    def fake_prepare(db):
        calls.append(db)
        return 3

    monkeypatch.setattr(
        notification_scheduler,
        "prepare_due_service_reminders",
        fake_prepare,
    )

    result = notification_scheduler.process_due_service_reminders_once()

    assert result == 3
    assert len(calls) == 1
    assert isinstance(
        calls[0],
        DummySession,
    )
