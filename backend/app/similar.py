from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tattoo
from app.search import SearchItem


def similar_tattoos(session: Session, tattoo_id: UUID, limit: int = 12) -> list[dict[str, str | None]]:
    source = session.get(Tattoo, tattoo_id)
    if source is None or source.embedding is None:
        return []
    limit = min(max(limit, 1), 50)
    tattoos = session.scalars(
        select(Tattoo)
        .where(Tattoo.id != tattoo_id, Tattoo.embedding.is_not(None))
        .order_by(Tattoo.embedding.cosine_distance(source.embedding))
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
