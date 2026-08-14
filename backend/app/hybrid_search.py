from sqlalchemy import case, desc, select
from sqlalchemy.orm import Session

from app.metadata import OpenAIEmbeddingProvider
from app.models import Tattoo
from app.query_parser import StructuredFilters
from app.search import SearchItem


def hybrid_search(
    session: Session,
    embedding_provider: OpenAIEmbeddingProvider,
    query: str,
    filters: StructuredFilters,
    limit: int = 24,
) -> list[dict[str, str | float | None]]:
    query_embedding = embedding_provider.embed(query)
    limit = min(max(limit, 1), 100)
    filter_fields = {
        "subject": Tattoo.subject,
        "style": Tattoo.style,
        "placement": Tattoo.placement,
        "size": Tattoo.size,
    }
    active_filters = [
        field == value
        for name, field in filter_fields.items()
        if (value := getattr(filters, name)) is not None
    ]
    filter_score = sum(case((condition, 1), else_=0) for condition in active_filters)
    filter_weight = 0.3 if active_filters else 0.0
    vector_weight = 1.0 - filter_weight
    distance = Tattoo.embedding.cosine_distance(query_embedding)
    score = vector_weight * (1 - distance)
    if active_filters:
        score = score + filter_weight * (filter_score / len(active_filters))
    tattoos = session.scalars(
        select(Tattoo)
        .where(Tattoo.embedding.is_not(None))
        .order_by(desc(score), Tattoo.created_at.desc())
        .limit(limit)
    ).all()
    return [
        {
            **SearchItem(
                tattoo.id,
                tattoo.image_url,
                tattoo.artist_id,
                tattoo.style,
                tattoo.subject,
                tattoo.placement,
                tattoo.semantic_description,
            ).as_dict(),
            "score": None,
        }
        for tattoo in tattoos
    ]
