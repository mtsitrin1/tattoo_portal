import base64
import json
import logging
from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from openai import OpenAI
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models import Tattoo

logger = logging.getLogger(__name__)


class TattooMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    subject: str | None = None
    style: str | None = None
    placement: str | None = None
    color: str | None = None
    size: str | None = None
    complexity: str | None = None
    orientation: str | None = None


class VisionMetadataProvider(Protocol):
    def extract(self, image_bytes: bytes) -> TattooMetadata:
        ...


class OpenAIVisionProvider:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract(self, image_bytes: bytes) -> TattooMetadata:
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract tattoo metadata from the image. Return JSON only with these "
                        "optional string fields: subject, style, placement, color, size, "
                        "complexity, orientation. Use null when uncertain."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this tattoo."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                        },
                    ],
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        return TattooMetadata.model_validate(json.loads(content))


class OpenAIDescriptionProvider:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, image_bytes: bytes, metadata: TattooMetadata) -> str:
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write one concise, natural-language tattoo description for semantic "
                        "search. Mention the subject, style, placement, color, size, "
                        "complexity, and orientation when available. Do not invent details."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Metadata: {metadata.model_dump()}"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                        },
                    ],
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()


class OpenAIEmbeddingProvider:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding


def extract_metadata_batch(
    session: Session,
    provider: VisionMetadataProvider,
    images: Iterable[tuple[UUID, bytes]],
) -> tuple[int, int]:
    succeeded = 0
    failed = 0
    for tattoo_id, image_bytes in images:
        try:
            metadata = provider.extract(image_bytes)
            tattoo = session.get(Tattoo, tattoo_id)
            if tattoo is None:
                raise ValueError(f"tattoo {tattoo_id} does not exist")
            for field, value in metadata.model_dump().items():
                setattr(tattoo, field, value)
            session.commit()
            succeeded += 1
        except Exception:
            session.rollback()
            failed += 1
            logger.exception("metadata_extraction_failed tattoo_id=%s", tattoo_id)
    return succeeded, failed


def generate_descriptions_batch(
    session: Session,
    provider,
    records: Iterable[tuple[UUID, bytes, TattooMetadata]],
) -> tuple[int, int]:
    succeeded = 0
    failed = 0
    for tattoo_id, image_bytes, metadata in records:
        try:
            description = provider.generate(image_bytes, metadata)
            if not description:
                raise ValueError("description provider returned an empty description")
            tattoo = session.get(Tattoo, tattoo_id)
            if tattoo is None:
                raise ValueError(f"tattoo {tattoo_id} does not exist")
            tattoo.semantic_description = description
            session.commit()
            succeeded += 1
        except Exception:
            session.rollback()
            failed += 1
            logger.exception("description_generation_failed tattoo_id=%s", tattoo_id)
    return succeeded, failed


def generate_embeddings_batch(session: Session, provider, tattoo_ids: Iterable[UUID]) -> tuple[int, int]:
    succeeded = 0
    failed = 0
    for tattoo_id in tattoo_ids:
        try:
            tattoo = session.get(Tattoo, tattoo_id)
            if tattoo is None:
                raise ValueError(f"tattoo {tattoo_id} does not exist")
            if not tattoo.semantic_description:
                logger.info("embedding_skipped_no_description tattoo_id=%s", tattoo_id)
                continue
            tattoo.embedding = provider.embed(tattoo.semantic_description)
            session.commit()
            succeeded += 1
        except Exception:
            session.rollback()
            failed += 1
            logger.exception("embedding_generation_failed tattoo_id=%s", tattoo_id)
    return succeeded, failed
