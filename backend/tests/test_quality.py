from unittest.mock import Mock

from app.quality import get_quality_stats


def test_quality_stats_are_percentages_of_live_total() -> None:
    session = Mock()
    session.execute.return_value.one.return_value = (4, 2, 3, 1, 4, 2)

    result = get_quality_stats(session)

    assert result.as_dict() == {
        "total_tattoos": 4,
        "artist_percent": 50.0,
        "style_percent": 75.0,
        "placement_percent": 25.0,
        "description_percent": 100.0,
        "embedding_percent": 50.0,
    }


def test_quality_stats_handles_empty_dataset() -> None:
    session = Mock()
    session.execute.return_value.one.return_value = (0, 0, 0, 0, 0, 0)

    result = get_quality_stats(session)

    assert result.total_tattoos == 0
    assert result.embedding_percent == 0.0
