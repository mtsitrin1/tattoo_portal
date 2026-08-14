from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Artist, Source, Tattoo


def get_tattoo_detail(session: Session, tattoo_id: UUID) -> dict[str, object] | None:
    tattoo = session.get(Tattoo, tattoo_id)
    if tattoo is None:
        return None
    artist = session.get(Artist, tattoo.artist_id) if tattoo.artist_id else None
    source = session.get(Source, tattoo.source_id)
    return {
        "id": str(tattoo.id),
        "image_url": tattoo.image_url,
        "artist": {
            "id": str(artist.id),
            "name": artist.name,
            "profile_url": artist.profile_url,
        } if artist else None,
        "source": {"id": str(source.id), "name": source.name, "url": source.url}
        if source else None,
        "metadata": {
            "subject": tattoo.subject,
            "style": tattoo.style,
            "placement": tattoo.placement,
            "color": tattoo.color,
            "size": tattoo.size,
            "complexity": tattoo.complexity,
            "orientation": tattoo.orientation,
            "semantic_description": tattoo.semantic_description,
        },
    }
