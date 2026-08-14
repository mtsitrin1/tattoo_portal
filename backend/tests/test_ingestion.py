from io import BytesIO
from unittest.mock import Mock
from uuid import uuid4

from app.ingestion import IngestionService, is_duplicate, perceptual_hash
from app.storage import ImageStorage, StorageConfig


def test_ingestion_uploads_image_and_persists_tattoo() -> None:
    from PIL import Image

    source_id = uuid4()
    session = Mock()
    session.scalar.side_effect = [None, None]
    session.scalars.return_value = []
    session.flush.side_effect = lambda: setattr(
        session.add.call_args.args[0], "id", source_id
    )
    storage = ImageStorage(
        StorageConfig("http://storage", "us-east-1", "key", "secret", "tattoo-images"),
        client=Mock(),
    )

    image = Image.new("RGB", (32, 32), color="black")
    tattoo = IngestionService(session, storage).ingest(
        BytesIO(_png_bytes(image)),
        "design.png",
        "image/png",
        "https://example.com/gallery",
        "A. Artist",
    )

    assert tattoo.image_url.startswith("s3://tattoo-images/tattoos/")
    assert tattoo.source_id == source_id
    assert tattoo.artist_id == source_id
    storage.client.upload_fileobj.assert_called_once()
    session.commit.assert_called_once_with()


def test_perceptual_hash_is_stable_for_same_image() -> None:
    from PIL import Image

    image = Image.new("RGB", (32, 32), color="black")
    first = perceptual_hash(BytesIO(_png_bytes(image)))
    second = perceptual_hash(BytesIO(_png_bytes(image)))

    assert first == second
    assert is_duplicate(first, second)


def _png_bytes(image) -> bytes:
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
