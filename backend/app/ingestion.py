from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Artist, Source, Tattoo
from app.storage import ImageStorage


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
            source_id=source.id,
            artist_id=artist.id if artist else None,
        )
        self.session.add(tattoo)
        self.session.commit()
        self.session.refresh(tattoo)
        return tattoo
