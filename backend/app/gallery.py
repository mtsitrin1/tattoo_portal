from dataclasses import asdict, dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Tattoo


@dataclass(frozen=True)
class GalleryItem:
    id: UUID
    image_url: str
    artist_id: UUID | None
    style: str | None
    subject: str | None

    def as_dict(self) -> dict[str, str | None]:
        values = asdict(self)
        values["id"] = str(self.id)
        values["artist_id"] = str(self.artist_id) if self.artist_id else None
        return values


def get_gallery(session: Session, page: int, page_size: int) -> dict[str, object]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = int(session.scalar(select(func.count(Tattoo.id))) or 0)
    tattoos = session.scalars(
        select(Tattoo)
        .order_by(Tattoo.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = [
        GalleryItem(t.id, t.image_url, t.artist_id, t.style, t.subject).as_dict() for t in tattoos
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}
