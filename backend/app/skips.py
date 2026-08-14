from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Skip, Tattoo


def skip_tattoo(session: Session, tattoo_id: UUID, session_id: str, user_id: UUID | None = None) -> bool:
    if session.get(Tattoo, tattoo_id) is None:
        return False
    statement = insert(Skip).values(
        tattoo_id=tattoo_id, session_id=session_id, user_id=user_id
    ).on_conflict_do_nothing(index_elements=["session_id", "tattoo_id"])
    session.execute(statement)
    session.commit()
    return True
