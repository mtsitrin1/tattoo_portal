import json
import math
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.candidates import generate_candidates
from app.diversity import apply_diversity
from app.models import Like, SavedTattoo
from app.taste import get_taste_vector

_CONFIG_PATH = Path(__file__).with_name("feed_config.json")


def feed_weights() -> dict[str, float]:
    return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))


def rank_feed_candidates(candidates: list[dict[str, Any]], page_size: int = 24) -> list[dict[str, Any]]:
    weights = feed_weights()
    for candidate in candidates:
        candidate["score"] = (
            weights["vector_similarity_weight"] * candidate.get("vector_similarity", 0.0)
            + weights["popularity_weight"] * candidate.get("popularity", 0.0)
            + weights["recency_weight"] * candidate.get("recency", 0.0)
        )
    ranked = sorted(candidates, key=lambda candidate: candidate["score"], reverse=True)
    return apply_diversity(ranked, page_size=page_size)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(
        sum(value * value for value in right)
    )
    return sum(a * b for a, b in zip(left, right, strict=True)) / denominator if denominator else 0.0


def get_feed(session: Session, user_id, page: int = 1, page_size: int = 24) -> dict[str, object]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 24)
    taste_vector = get_taste_vector(session, user_id)
    candidates = generate_candidates(session, user_id, 200)
    ranked_candidates = []
    for tattoo in candidates:
        popularity = session.scalar(select(func.count(Like.id)).where(Like.tattoo_id == tattoo.id)) or 0
        popularity += 2 * (session.scalar(
            select(func.count(SavedTattoo.tattoo_id)).where(SavedTattoo.tattoo_id == tattoo.id)
        ) or 0)
        ranked_candidates.append({
            "id": str(tattoo.id),
            "image_url": tattoo.image_url,
            "subject": tattoo.subject,
            "style": tattoo.style,
            "semantic_description": tattoo.semantic_description,
            "vector_similarity": _cosine_similarity(list(tattoo.embedding), taste_vector)
            if taste_vector is not None and tattoo.embedding is not None else 0.0,
            "popularity": float(popularity),
            "recency": 1.0,
        })
    ranked = rank_feed_candidates(ranked_candidates, page_size=len(ranked_candidates))
    start = (page - 1) * page_size
    items = ranked[start:start + page_size]
    return {"items": items, "page": page, "page_size": page_size, "has_more": start + page_size < len(ranked)}
