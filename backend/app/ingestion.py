import logging
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import imagehash
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Artist, Source, Tattoo
from app.storage import ImageStorage

logger = logging.getLogger(__name__)


def perceptual_hash(image) -> str:
    image.seek(0)
    return str(imagehash.phash(Image.open(image)))


def is_duplicate(candidate_hash: str, existing_hash: str, max_distance: int = 5) -> bool:
    return imagehash.hex_to_hash(candidate_hash) - imagehash.hex_to_hash(existing_hash) <= max_distance


class IngestionService:
    def __init__(self, session: Session, storage: ImageStorage) -> None:
        self.session = session
        self.storage = storage

    def ingest(
        self,
        image,
        filename: str,
        content_type: str,
        source_url: str,
        artist_name: str | None = None,
    ) -> Tattoo:
        image_hash = perceptual_hash(image)
        for existing in self.session.scalars(select(Tattoo).where(Tattoo.image_hash.is_not(None))):
            if is_duplicate(image_hash, existing.image_hash):
                logger.info("image_deduplicated duplicate_of=%s image_hash=%s", existing.id, image_hash)
                return existing

        source = self.session.scalar(select(Source).where(Source.url == source_url))
        if source is None:
            parsed_source = urlparse(source_url)
            source = Source(name=parsed_source.netloc or source_url, url=source_url)
            self.session.add(source)
            self.session.flush()

        artist = None
        if artist_name:
            artist = self.session.scalar(select(Artist).where(Artist.name == artist_name))
            if artist is None:
                artist = Artist(name=artist_name)
                self.session.add(artist)
                self.session.flush()

        suffix = Path(filename).suffix.lower() or ".bin"
        object_key = f"tattoos/{uuid4()}{suffix}"
        self.storage.upload_image(object_key, image, content_type)
        tattoo = Tattoo(
            image_url=f"s3://{self.storage.config.bucket}/{object_key}",
            image_hash=image_hash,
            source_id=source.id,
            artist_id=artist.id if artist else None,
        )
        self.session.add(tattoo)
        self.session.commit()
        self.session.refresh(tattoo)
        return tattoo
