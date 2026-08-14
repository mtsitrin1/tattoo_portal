from unittest.mock import Mock, patch
from uuid import uuid4

from app.feed import get_feed


def test_feed_returns_page_size_24_and_has_more() -> None:
    session = Mock()
    session.scalar.return_value = 0
    candidates = [
        Mock(
            id=uuid4(), image_url="image", subject="bird", style="blackwork",
            semantic_description="bird", embedding=None,
        )
        for _ in range(25)
    ]
    with patch("app.feed.get_taste_vector", return_value=None), patch(
        "app.feed.generate_candidates", return_value=candidates
    ):
        result = get_feed(session, uuid4())

    assert result["page_size"] == 24
    assert len(result["items"]) == 24
    assert result["has_more"] is True
