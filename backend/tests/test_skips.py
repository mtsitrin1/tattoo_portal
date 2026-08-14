from unittest.mock import Mock
from uuid import uuid4

from app.skips import skip_tattoo


def test_skip_is_persisted_idempotently_for_session_and_tattoo() -> None:
    session = Mock()
    session.get.return_value = object()

    assert skip_tattoo(session, uuid4(), "session-1") is True
    session.execute.assert_called_once()
    session.commit.assert_called_once_with()


def test_skip_returns_false_for_unknown_tattoo() -> None:
    session = Mock()
    session.get.return_value = None

    assert skip_tattoo(session, uuid4(), "session-1") is False
    session.execute.assert_not_called()
