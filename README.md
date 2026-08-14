# Tattoo Portal

Tattoo Portal helps people discover tattoo designs they would seriously consider getting.

## Repository layout

- `backend/` — FastAPI service and Python tests
- `frontend/` — Next.js application
- `.github/workflows/ci.yml` — pull-request checks

## Local development

Copy `.env.example` to `.env` and start the two applications in separate terminals:

```bash
cp .env.example .env

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

cd ..
docker compose up -d postgres

cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The API is available at http://localhost:8000 and the web app at http://localhost:3000.

Stop the database with `docker compose down`. Add `-v` only when you intentionally want to remove the local database volume.

## Checks

```bash
cd backend && ruff check . && pytest
cd frontend && npm run lint && npm run typecheck
```
