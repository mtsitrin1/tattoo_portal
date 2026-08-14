import json
from pathlib import Path
from typing import Any

from app.diversity import apply_diversity

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
