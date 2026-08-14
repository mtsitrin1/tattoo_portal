from collections import Counter
from collections.abc import Iterable
from typing import Any


def apply_diversity(
    candidates: Iterable[dict[str, Any]], page_size: int = 24, cap: int = 2
) -> list[dict[str, Any]]:
    candidates = list(candidates)
    selected: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    deferred: list[dict[str, Any]] = []
    for candidate in candidates:
        subject = candidate.get("subject") or "__unknown__"
        if counts[subject] < cap:
            selected.append(candidate)
            counts[subject] += 1
        else:
            deferred.append(candidate)
        if len(selected) == page_size:
            return selected
    for candidate in deferred:
        if len(selected) == page_size:
            break
        selected.append(candidate)
    return selected
