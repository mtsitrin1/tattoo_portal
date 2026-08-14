from app.feed import feed_weights, rank_feed_candidates


def test_feed_weights_are_configured() -> None:
    assert feed_weights() == {
        "vector_similarity_weight": 0.7,
        "popularity_weight": 0.2,
        "recency_weight": 0.1,
    }


def test_feed_ranks_before_applying_diversity() -> None:
    candidates = [
        {"id": "bird-1", "subject": "bird", "vector_similarity": 1.0},
        {"id": "bird-2", "subject": "bird", "vector_similarity": 0.9},
        {"id": "bird-3", "subject": "bird", "vector_similarity": 0.8},
        {"id": "floral-1", "subject": "floral", "vector_similarity": 0.1},
    ]

    result = rank_feed_candidates(candidates, page_size=3)

    assert [candidate["id"] for candidate in result] == ["bird-1", "bird-2", "floral-1"]
