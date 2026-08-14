from dataclasses import asdict, dataclass

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Tattoo


@dataclass(frozen=True)
class QualityStats:
    total_tattoos: int
    artist_percent: float
    style_percent: float
    placement_percent: float
    description_percent: float
    embedding_percent: float

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


def get_quality_stats(session: Session) -> QualityStats:
    fields = [
        Tattoo.artist_id.is_not(None),
        Tattoo.style.is_not(None),
        Tattoo.placement.is_not(None),
        Tattoo.semantic_description.is_not(None),
        Tattoo.embedding.is_not(None),
    ]
    counts = session.execute(
        select(
            func.count(Tattoo.id),
            *(func.sum(case((field, 1), else_=0)) for field in fields),
        )
    ).one()
    total = int(counts[0] or 0)
    percentages = [round((int(count or 0) / total) * 100, 2) if total else 0.0 for count in counts[1:]]
    return QualityStats(total, *percentages)
