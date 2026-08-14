from unittest.mock import Mock
from uuid import uuid4

from app.saves import save_tattoo


def test_save_is_idempotent_for_user_and_tattoo() -> None:
    session = Mock()
    session.get.return_value = object()

    assert save_tattoo(session, uuid4(), uuid4()) is True
    session.execute.assert_called_once()
    session.commit.assert_called_once_with()


def test_save_returns_false_for_unknown_tattoo() -> None:
    session = Mock()
    session.get.return_value = None

    assert save_tattoo(session, uuid4(), uuid4()) is False
    session.execute.assert_not_called()
