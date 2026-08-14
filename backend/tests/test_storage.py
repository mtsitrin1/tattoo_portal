from io import BytesIO
from unittest.mock import Mock

from app.storage import ImageStorage, StorageConfig


def test_upload_image_uses_configured_bucket_and_content_type() -> None:
    client = Mock()
    storage = ImageStorage(
        StorageConfig("http://storage", "us-east-1", "key", "secret", "tattoo-images"),
        client=client,
    )

    result = storage.upload_image("tattoos/one.jpg", BytesIO(b"image"), "image/jpeg")

    assert result == "tattoos/one.jpg"
    client.upload_fileobj.assert_called_once()
    assert client.upload_fileobj.call_args.args[1:3] == ("tattoo-images", "tattoos/one.jpg")
    assert client.upload_fileobj.call_args.kwargs == {"ExtraArgs": {"ContentType": "image/jpeg"}}


def test_download_image_reads_and_closes_response_body() -> None:
    client = Mock()
    body = Mock()
    body.read.return_value = b"image"
    client.get_object.return_value = {"Body": body}
    storage = ImageStorage(
        StorageConfig("http://storage", "us-east-1", "key", "secret", "tattoo-images"),
        client=client,
    )

    assert storage.download_image("tattoos/one.jpg") == b"image"
    client.get_object.assert_called_once_with(Bucket="tattoo-images", Key="tattoos/one.jpg")
    body.close.assert_called_once_with()
