from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Like, SavedTattoo, Tattoo


def weighted_mean(vectors: Iterable[tuple[list[float], int]]) -> list[float] | None:
    vectors = list(vectors)
    if not vectors:
        return None
    dimensions = len(vectors[0][0])
    totals = [0.0] * dimensions
    total_weight = 0
    for vector, weight in vectors:
        for index, value in enumerate(vector):
            totals[index] += value * weight
        total_weight += weight
    return [value / total_weight for value in totals]


def get_taste_vector(session: Session, user_id: UUID) -> list[float] | None:
    liked = session.execute(
        select(Like.tattoo_id, Like.created_at).where(Like.user_id == user_id)
    ).all()
    saved = session.execute(
        select(SavedTattoo.tattoo_id, SavedTattoo.created_at).where(SavedTattoo.user_id == user_id)
    ).all()
    interactions = [(row.tattoo_id, row.created_at, 1) for row in liked]
    interactions += [(row.tattoo_id, row.created_at, 2) for row in saved]
    interactions = sorted(interactions, key=lambda row: row[1], reverse=True)[:50]
    vectors = []
    for tattoo_id, _created_at, weight in interactions:
        tattoo = session.get(Tattoo, tattoo_id)
        if tattoo is not None and tattoo.embedding is not None:
            vectors.append((list(tattoo.embedding), weight))
    return weighted_mean(vectors)
