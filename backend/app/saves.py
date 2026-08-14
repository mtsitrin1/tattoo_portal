from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import SavedTattoo, Tattoo


def save_tattoo(session: Session, tattoo_id: UUID, user_id: UUID) -> bool:
    if session.get(Tattoo, tattoo_id) is None:
        return False
    statement = insert(SavedTattoo).values(tattoo_id=tattoo_id, user_id=user_id).on_conflict_do_nothing()
    session.execute(statement)
    session.commit()
    return True


def list_saved_tattoos(session: Session, user_id: UUID) -> list[Tattoo]:
    return list(session.scalars(
        select(Tattoo)
        .join(SavedTattoo, SavedTattoo.tattoo_id == Tattoo.id)
        .where(SavedTattoo.user_id == user_id)
        .order_by(SavedTattoo.created_at.desc())
    ).all())
