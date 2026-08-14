from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.hybrid_search import hybrid_search
from app.query_parser import StructuredFilters


def test_hybrid_search_combines_vector_query_and_structured_filters() -> None:
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
    provider = Mock()
    provider.embed.return_value = [0.1, 0.2]

    result = hybrid_search(
        session,
        provider,
        "black bird",
        StructuredFilters(style="blackwork", placement="forearm"),
    )

    provider.embed.assert_called_once_with("black bird")
    assert result[0]["id"] == str(tattoo_id)
    assert result[0]["score"] is None
