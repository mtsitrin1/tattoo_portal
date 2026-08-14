from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from app.events import record_event


def test_record_event_persists_supported_event_with_timestamp() -> None:
    session = Mock()
    session.get.return_value = object()

    assert record_event(session, "view", "session-1", uuid4()) is True
    event = session.add.call_args.args[0]
    assert event.event_type == "view"
    assert isinstance(event.created_at, datetime)
    session.commit.assert_called_once_with()


def test_record_event_rejects_unknown_type() -> None:
    session = Mock()

    assert record_event(session, "unknown", "session-1", uuid4()) is False
    session.add.assert_not_called()
