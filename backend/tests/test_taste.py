from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.taste import get_taste_vector, weighted_mean


def test_weighted_mean_gives_saves_two_times_the_weight() -> None:
    assert weighted_mean([([1.0, 0.0], 1), ([0.0, 1.0], 2)]) == [1 / 3, 2 / 3]


def test_taste_vector_is_none_for_cold_start() -> None:
    session = Mock()
    session.execute.return_value.all.return_value = []

    assert get_taste_vector(session, uuid4()) is None


def test_taste_vector_uses_latest_interactions() -> None:
    user_id, first_id, second_id = uuid4(), uuid4(), uuid4()
    session = Mock()
    session.execute.side_effect = [
        SimpleNamespace(all=lambda: [SimpleNamespace(tattoo_id=first_id, created_at=2)]),
        SimpleNamespace(all=lambda: [SimpleNamespace(tattoo_id=second_id, created_at=1)]),
    ]
    session.get.side_effect = [
        SimpleNamespace(embedding=[1.0, 0.0]),
        SimpleNamespace(embedding=[0.0, 1.0]),
    ]

    assert get_taste_vector(session, user_id) == [1 / 3, 2 / 3]
