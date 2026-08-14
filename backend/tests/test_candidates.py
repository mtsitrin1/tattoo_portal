from unittest.mock import Mock, patch
from uuid import uuid4

from app.candidates import generate_candidates


def test_candidate_generation_returns_top_vector_neighbors_for_personalized_user() -> None:
    session = Mock()
    session.scalars.return_value.all.return_value = [object()]

    with patch("app.candidates.get_taste_vector", return_value=[0.1, 0.2]):
        result = generate_candidates(session, uuid4())

    assert len(result) == 1
    session.scalars.assert_called_once()


def test_candidate_generation_falls_back_to_popularity_for_cold_start() -> None:
    session = Mock()
    session.execute.return_value.all.return_value = []
    session.scalars.return_value.all.return_value = [object(), object()]

    result = generate_candidates(session, uuid4())

    assert len(result) == 2
