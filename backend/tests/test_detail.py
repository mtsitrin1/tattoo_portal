from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.detail import get_tattoo_detail


def test_tattoo_detail_includes_artist_source_and_metadata() -> None:
    tattoo_id, artist_id, source_id = uuid4(), uuid4(), uuid4()
    session = Mock()
    session.get.side_effect = [
        SimpleNamespace(
            id=tattoo_id, image_url="s3://tattoo-images/one.png", artist_id=artist_id,
            source_id=source_id, subject="bird", style="blackwork", placement="forearm",
            color="black", size="small", complexity="simple", orientation="vertical",
            semantic_description="A blackwork bird.",
        ),
        SimpleNamespace(id=artist_id, name="A. Artist", profile_url="https://artist.example"),
        SimpleNamespace(id=source_id, name="Gallery", url="https://gallery.example/one"),
    ]

    result = get_tattoo_detail(session, tattoo_id)

    assert result["artist"]["name"] == "A. Artist"
    assert result["source"]["url"] == "https://gallery.example/one"
    assert result["metadata"]["style"] == "blackwork"
