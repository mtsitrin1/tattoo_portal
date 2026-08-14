from app.diversity import apply_diversity


def test_diversity_caps_subjects_and_backfills_page() -> None:
    candidates = [{"id": index, "subject": "bird"} for index in range(4)]
    candidates += [{"id": 4, "subject": "floral"}, {"id": 5, "subject": "animal"}]

    result = apply_diversity(candidates, page_size=6, cap=2)

    assert len(result) == 6
    assert [item["id"] for item in result[:4]] == [0, 1, 4, 5]
    assert {item["id"] for item in result} == set(range(6))


def test_diversity_does_not_leave_slots_empty_when_candidates_exist() -> None:
    candidates = [{"id": index, "subject": "bird"} for index in range(3)]

    assert len(apply_diversity(candidates, page_size=3, cap=2)) == 3
