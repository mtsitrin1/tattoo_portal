from dataclasses import asdict, dataclass
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Tattoo


@dataclass(frozen=True)
class SearchItem:
    id: UUID
    image_url: str
    artist_id: UUID | None
    style: str | None
    subject: str | None
    placement: str | None
    semantic_description: str | None

    def as_dict(self) -> dict[str, str | None]:
        values = asdict(self)
        values["id"] = str(self.id)
        values["artist_id"] = str(self.artist_id) if self.artist_id else None
        return values


def search_tattoos(session: Session, query: str, limit: int = 24) -> list[dict[str, str | None]]:
    query = query.strip()
    if not query:
        return []
    limit = min(max(limit, 1), 100)
    pattern = f"%{query}%"
    fields = [
        Tattoo.semantic_description,
        Tattoo.subject,
        Tattoo.style,
        Tattoo.placement,
    ]
    matches = or_(*(field.ilike(pattern) for field in fields))
    rank = func.lower(func.concat_ws(" ", *fields)).like(f"%{query.lower()}%")
    tattoos = session.scalars(
        select(Tattoo).where(matches).order_by(rank.desc(), Tattoo.created_at.desc()).limit(limit)
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
