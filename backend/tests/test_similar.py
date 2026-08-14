from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.similar import similar_tattoos


def test_similar_tattoos_uses_source_embedding_and_excludes_source() -> None:
    source_id, similar_id = uuid4(), uuid4()
    session = Mock()
    session.get.return_value = SimpleNamespace(id=source_id, embedding=[0.1, 0.2])
    session.scalars.return_value.all.return_value = [
        SimpleNamespace(
            id=similar_id, image_url="s3://tattoo-images/two.png", artist_id=None,
            style="blackwork", subject="bird", placement="forearm",
            semantic_description="Another blackwork bird.",
        )
    ]

    result = similar_tattoos(session, source_id)

    assert result[0]["id"] == str(similar_id)
    session.scalars.assert_called_once()


def test_similar_tattoos_returns_empty_without_source_embedding() -> None:
    session = Mock()
    session.get.return_value = SimpleNamespace(embedding=None)

    assert similar_tattoos(session, uuid4()) == []
    session.scalars.assert_not_called()
