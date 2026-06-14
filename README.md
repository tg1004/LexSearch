# LexSearch

AI-powered semantic search engine for Indian legal judgements.

## Phase 1 — Foundation

Deliverable: app runs locally; users can sign up and log in.

## Phase 4 — LLM + RAG

Deliverable: full search with AI answer, citations, and Groq → Gemini fallback.

```powershell
docker compose up postgres redis elasticsearch qdrant -d
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- `POST /api/search` — hybrid retrieval + AI answer + citations
- `GET /api/providers` — Groq / Gemini / Auto availability

## Phase 3 — Search Backend

Deliverable: `POST /api/search` returns hybrid-ranked results (no LLM yet).

```powershell
docker compose up postgres redis elasticsearch qdrant -d
cd backend
..\backend\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Test at http://localhost:8000/docs → `POST /api/search`

## Phase 2 — Data Pipeline

Deliverable: 1000 judgements searchable in Qdrant and Elasticsearch.

See [`data_pipeline/README.md`](data_pipeline/README.md) for full instructions.

```powershell
docker compose up postgres elasticsearch qdrant -d
python -m data_pipeline.run_pipeline --step all --limit 1000
```

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

## Quick Start (Docker)

```bash
# Copy environment template
cp .env.example .env

# Start all services
docker compose up --build

# Run database migrations (first time)
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Local Development (without Docker for app code)

```bash
# Start infrastructure only
docker compose up postgres redis elasticsearch -d

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

See `LexSearch_Architecture.md` for the full specification and build phases.
