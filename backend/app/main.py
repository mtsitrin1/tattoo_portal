import os
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db import get_session
from app.detail import get_tattoo_detail
from app.gallery import get_gallery
from app.hybrid_search import hybrid_search
from app.ingestion import IngestionService
from app.quality import get_quality_stats
from app.query_parser import OpenAIQueryParser
from app.search import search_tattoos
from app.similar import similar_tattoos
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
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    return get_gallery(session, page, page_size)


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


@app.get("/search")
def search(
    q: str = Query(default=""),
    limit: int = Query(default=24, ge=1, le=100),
    session: Session = Depends(get_session),  # noqa: B008
) -> dict[str, object]:
    return {"query": q, "items": search_tattoos(session, q, limit)}


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
