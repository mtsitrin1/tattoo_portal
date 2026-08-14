from io import BytesIO
from unittest.mock import Mock
from uuid import uuid4

from app.ingestion import IngestionService
from app.storage import ImageStorage, StorageConfig


def test_ingestion_uploads_image_and_persists_tattoo() -> None:
    source_id = uuid4()
    session = Mock()
    session.scalar.side_effect = [None, None]
    session.flush.side_effect = lambda: setattr(
        session.add.call_args.args[0], "id", source_id
    )
    storage = ImageStorage(
        StorageConfig("http://storage", "us-east-1", "key", "secret", "tattoo-images"),
        client=Mock(),
    )

    tattoo = IngestionService(session, storage).ingest(
        BytesIO(b"image"), "design.jpg", "image/jpeg", "https://example.com/gallery", "A. Artist"
    )

    assert tattoo.image_url.startswith("s3://tattoo-images/tattoos/")
    assert tattoo.source_id == source_id
    assert tattoo.artist_id == source_id
    storage.client.upload_fileobj.assert_called_once()
    session.commit.assert_called_once_with()
