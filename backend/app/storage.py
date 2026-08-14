from dataclasses import dataclass
from typing import BinaryIO

import boto3
from botocore.client import BaseClient


@dataclass(frozen=True)
class StorageConfig:
    endpoint_url: str
    region_name: str
    access_key_id: str
    secret_access_key: str
    bucket: str


class ImageStorage:
    def __init__(self, config: StorageConfig, client: BaseClient | None = None) -> None:
        self.config = config
        self.client = client or boto3.client(
            "s3",
            endpoint_url=config.endpoint_url,
            region_name=config.region_name,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
        )

    def upload_image(self, object_key: str, image: BinaryIO, content_type: str) -> str:
        self.client.upload_fileobj(
            image,
            self.config.bucket,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
        return object_key

    def download_image(self, object_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.config.bucket, Key=object_key)
        body = response["Body"]
        try:
            return body.read()
        finally:
            body.close()
