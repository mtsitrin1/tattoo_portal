from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.gallery import get_gallery


def test_gallery_returns_page_of_live_database_records() -> None:
    first_id = uuid4()
    session = Mock()
    session.scalar.return_value = 3
    session.scalars.return_value.all.return_value = [
        SimpleNamespace(
            id=first_id,
            image_url="s3://tattoo-images/one.png",
            artist_id=None,
            style="blackwork",
            subject="bird",
        )
    ]

    result = get_gallery(session, page=2, page_size=10)

    assert result == {
        "items": [
            {
                "id": str(first_id),
                "image_url": "s3://tattoo-images/one.png",
                "artist_id": None,
                "style": "blackwork",
                "subject": "bird",
            }
        ],
        "page": 2,
        "page_size": 10,
        "total": 3,
    }
