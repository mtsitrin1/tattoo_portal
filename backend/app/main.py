import os
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db import get_session
from app.detail import get_tattoo_detail
from app.events import EVENT_TYPES, list_events, record_event
from app.gallery import get_gallery
from app.hybrid_search import hybrid_search
from app.ingestion import IngestionService
from app.likes import like_tattoo
from app.quality import get_quality_stats
from app.query_parser import OpenAIQueryParser
from app.saves import list_saved_tattoos, save_tattoo
from app.search import search_tattoos
from app.similar import similar_tattoos
from app.skips import skip_tattoo
from app.storage import ImageStorage, StorageConfig
from app.vector_search import embedding_provider_from_env, vector_search

app = FastAPI(title="Tattoo Portal API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tattoos")
def gallery(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
    session_id: str | None = Query(default=None),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    return get_gallery(session, page, page_size, session_id)


@app.get("/tattoos/{tattoo_id}")
def tattoo_detail(tattoo_id: str, session: Session = Depends(get_session)) -> dict[str, object]:  # noqa: B008
    try:
        detail = get_tattoo_detail(session, UUID(tattoo_id))
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid tattoo id") from error
    if detail is None:
        raise HTTPException(status_code=404, detail="Tattoo not found")
    return detail


@app.get("/tattoos/{tattoo_id}/similar")
def similar_tattoo_endpoint(
    tattoo_id: str,
    limit: int = Query(default=12, ge=1, le=50),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    try:
        from uuid import UUID

        parsed_id = UUID(tattoo_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid tattoo id") from error
    return {"tattoo_id": tattoo_id, "items": similar_tattoos(session, parsed_id, limit)}


@app.post("/tattoos/{tattoo_id}/like")
def like_tattoo_endpoint(
    tattoo_id: str,
    session_id: str = Form(...),
    user_id: str | None = Form(default=None),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    from uuid import UUID

    try:
        parsed_id = UUID(tattoo_id)
        parsed_user_id = UUID(user_id) if user_id else None
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid id") from error
    if not like_tattoo(session, parsed_id, session_id, parsed_user_id):
        raise HTTPException(status_code=404, detail="Tattoo not found")
    record_event(session, "like", session_id, parsed_id, parsed_user_id)
    return {"tattoo_id": tattoo_id, "liked": True}


@app.post("/tattoos/{tattoo_id}/skip")
def skip_tattoo_endpoint(
    tattoo_id: str,
    session_id: str = Form(...),
    user_id: str | None = Form(default=None),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    try:
        parsed_id = UUID(tattoo_id)
        parsed_user_id = UUID(user_id) if user_id else None
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid id") from error
    if not skip_tattoo(session, parsed_id, session_id, parsed_user_id):
        raise HTTPException(status_code=404, detail="Tattoo not found")
    record_event(session, "skip", session_id, parsed_id, parsed_user_id)
    return {"tattoo_id": tattoo_id, "skipped": True}


@app.post("/tattoos/{tattoo_id}/save")
def save_tattoo_endpoint(
    tattoo_id: str,
    user_id: str = Form(...),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    try:
        parsed_id, parsed_user_id = UUID(tattoo_id), UUID(user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid id") from error
    if not save_tattoo(session, parsed_id, parsed_user_id):
        raise HTTPException(status_code=404, detail="Tattoo not found")
    record_event(session, "save", str(parsed_user_id), parsed_id, parsed_user_id)
    return {"tattoo_id": tattoo_id, "saved": True}


@app.post("/events")
def event_endpoint(
    event_type: str = Form(...),
    session_id: str = Form(...),
    tattoo_id: str = Form(...),
    user_id: str | None = Form(default=None),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    try:
        parsed_tattoo_id = UUID(tattoo_id)
        parsed_user_id = UUID(user_id) if user_id else None
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid id") from error
    if event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid event type")
    if not record_event(session, event_type, session_id, parsed_tattoo_id, parsed_user_id):
        raise HTTPException(status_code=404, detail="Tattoo not found")
    return {"recorded": True}


@app.get("/events")
def events_endpoint(limit: int = Query(default=100, ge=1, le=1000), session: Session = Depends(get_session)) -> dict[str, object]:  # noqa: B008
    return {"events": [
        {"id": str(event.id), "session_id": event.session_id, "tattoo_id": str(event.tattoo_id),
         "event_type": event.event_type, "created_at": event.created_at.isoformat()}
        for event in list_events(session, limit)
    ]}


@app.get("/saved/{user_id}")
def saved_tattoos_endpoint(user_id: str, session: Session = Depends(get_session)) -> dict[str, object]:  # noqa: B008
    try:
        parsed_user_id = UUID(user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Invalid user id") from error
    items = list_saved_tattoos(session, parsed_user_id)
    return {
        "user_id": user_id,
        "items": [{"id": str(item.id), "image_url": item.image_url, "style": item.style, "subject": item.subject} for item in items],
    }


@app.get("/search")
def search(
    q: str = Query(default=""),
    limit: int = Query(default=24, ge=1, le=100),
    session_id: str | None = Query(default=None),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    return {"query": q, "items": search_tattoos(session, q, limit, session_id)}


@app.get("/search/vector")
def vector_search_endpoint(
    q: str = Query(default=""),
    limit: int = Query(default=24, ge=1, le=100),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    return {"query": q, "items": vector_search(session, embedding_provider_from_env(), q, limit)}


@app.get("/search/hybrid")
def hybrid_search_endpoint(
    q: str = Query(default=""),
    limit: int = Query(default=24, ge=1, le=100),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    filters = OpenAIQueryParser(
        os.getenv("OPENAI_API_KEY", ""), os.getenv("OPENAI_QUERY_MODEL", "gpt-4o-mini")
    ).parse(q)
    return {"query": q, "filters": filters.model_dump(exclude_none=True), "items": hybrid_search(
        session, embedding_provider_from_env(), q, filters, limit
    )}


@app.get("/quality")
def quality_dashboard(session: Session = Depends(get_session)) -> dict[str, int | float]:  # noqa: B008
    return get_quality_stats(session).as_dict()


def get_storage() -> ImageStorage:
    return ImageStorage(
        StorageConfig(
            endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:9000"),
            region_name=os.getenv("S3_REGION", "us-east-1"),
            access_key_id=os.getenv("S3_ACCESS_KEY_ID", "minioadmin"),
            secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin"),
            bucket=os.getenv("S3_BUCKET", "tattoo-images"),
        )
    )


@app.post("/ingest")
def ingest_tattoo(
    image: UploadFile = File(...),  # noqa: B008
    source_url: str = Form(...),
    artist_name: str | None = Form(default=None),
    session: Session = Depends(get_session),  # noqa: B008
    storage: ImageStorage = Depends(get_storage),  # noqa: B008
) -> dict[str, str | None]:
    tattoo = IngestionService(session, storage).ingest(
        image=image.file,
        filename=image.filename or "image",
        content_type=image.content_type or "application/octet-stream",
        source_url=source_url,
        artist_name=artist_name,
    )
    return {
        "id": str(tattoo.id),
        "image_url": tattoo.image_url,
        "source_id": str(tattoo.source_id),
        "artist_id": str(tattoo.artist_id) if tattoo.artist_id else None,
    }
