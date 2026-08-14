from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Like, SavedTattoo, Tattoo
from app.taste import get_taste_vector


def generate_candidates(session: Session, user_id: UUID, limit: int = 200) -> list[Tattoo]:
    limit = min(max(limit, 1), 200)
    taste_vector = get_taste_vector(session, user_id)
    if taste_vector is not None:
        return list(session.scalars(
            select(Tattoo)
            .where(Tattoo.embedding.is_not(None))
            .order_by(Tattoo.embedding.cosine_distance(taste_vector))
            .limit(limit)
        ).all())

    like_count = select(func.count(Like.id)).where(Like.tattoo_id == Tattoo.id).scalar_subquery()
    save_count = select(func.count(SavedTattoo.tattoo_id)).where(
        SavedTattoo.tattoo_id == Tattoo.id
    ).scalar_subquery()
    popularity = like_count + (2 * save_count)
    return list(session.scalars(
        select(Tattoo).order_by(popularity.desc(), Tattoo.created_at.desc()).limit(limit)
    ).all())
