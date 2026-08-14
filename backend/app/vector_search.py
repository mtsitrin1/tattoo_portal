import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.metadata import OpenAIEmbeddingProvider
from app.models import Tattoo
from app.search import SearchItem


def vector_search(
    session: Session,
    embedding_provider: OpenAIEmbeddingProvider,
    query: str,
    limit: int = 24,
) -> list[dict[str, str | None]]:
    query_embedding = embedding_provider.embed(query)
    limit = min(max(limit, 1), 100)
    tattoos = session.scalars(
        select(Tattoo)
        .where(Tattoo.embedding.is_not(None))
        .order_by(Tattoo.embedding.cosine_distance(query_embedding))
        .limit(limit)
    ).all()
    return [
        SearchItem(
            tattoo.id,
            tattoo.image_url,
            tattoo.artist_id,
            tattoo.style,
            tattoo.subject,
            tattoo.placement,
            tattoo.semantic_description,
        ).as_dict()
        for tattoo in tattoos
    ]


def embedding_provider_from_env() -> OpenAIEmbeddingProvider:
    return OpenAIEmbeddingProvider(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )
