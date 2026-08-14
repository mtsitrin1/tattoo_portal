from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tattoo, UserInteraction

EVENT_TYPES = {"impression", "view", "like", "skip", "save", "similar-click", "search", "artist-click"}


def record_event(
    session: Session,
    event_type: str,
    session_id: str,
    tattoo_id: UUID,
    user_id: UUID | None = None,
) -> bool:
    if event_type not in EVENT_TYPES or session.get(Tattoo, tattoo_id) is None:
        return False
    session.add(UserInteraction(
        user_id=user_id,
        session_id=session_id,
        tattoo_id=tattoo_id,
        event_type=event_type,
        created_at=datetime.now(UTC),
    ))
    session.commit()
    return True


def list_events(session: Session, limit: int = 100) -> list[UserInteraction]:
    return list(session.scalars(
        select(UserInteraction).order_by(UserInteraction.created_at.desc()).limit(min(limit, 1000))
    ).all())
