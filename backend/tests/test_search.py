from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.search import search_tattoos


def test_search_returns_ranked_database_matches() -> None:
    tattoo_id = uuid4()
    session = Mock()
    session.scalars.return_value.all.return_value = [
        SimpleNamespace(
            id=tattoo_id,
            image_url="s3://tattoo-images/one.png",
            artist_id=None,
            style="blackwork",
            subject="bird",
            placement="forearm",
            semantic_description="A blackwork bird on the forearm.",
        )
    ]

    result = search_tattoos(session, "bird")

    assert result == [
        {
            "id": str(tattoo_id),
            "image_url": "s3://tattoo-images/one.png",
            "artist_id": None,
            "style": "blackwork",
            "subject": "bird",
            "placement": "forearm",
            "semantic_description": "A blackwork bird on the forearm.",
        }
    ]


def test_empty_search_does_not_query_database() -> None:
    session = Mock()

    assert search_tattoos(session, "   ") == []
    session.scalars.assert_not_called()
