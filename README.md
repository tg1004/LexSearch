# LexSearch

AI-powered semantic search engine for Indian legal judgements.

## Phase 8 — Quality + Deployment

Deliverable: live deployed app with CI/CD, quality benchmarks, and production configs.

### Quality evaluation (50 queries)

```powershell
cd d:\LexSearch\backend
.\venv\Scripts\activate
pip install httpx
cd ..
python scripts/eval_search_quality.py --api-url http://localhost:8000
```

Report saved to `reports/search_quality_report.json`. Each query scored 0–5 on results, citations, legal content, and latency.

### Performance benchmark (<3s p95)

```powershell
python scripts/benchmark_search.py --api-url http://localhost:8000 --max-p95-ms 3000
```

### Run all backend tests

```powershell
cd backend
pytest -q
```

### Scale data pipeline to 10,000+ documents

```powershell
python -m data_pipeline.run_pipeline --step all --limit 10000
# Or ingest-only after scrape/process:
python -m data_pipeline.run_pipeline --step ingest --ingest-target qdrant
```

Tune chunking via `.env`: `CHUNK_SIZE=800`, `CHUNK_OVERLAP=150`

### Deploy backend (Railway)

1. Push repo to GitHub
2. [Railway](https://railway.app) → New Project → Deploy from GitHub
3. Add **PostgreSQL** and **Redis** plugins
4. Set env vars from [`.env.production.example`](.env.production.example)
5. Railway reads [`railway.toml`](railway.toml) — builds `backend/Dockerfile`, runs migrations on start

### Deploy frontend (Vercel)

1. [Vercel](https://vercel.com) → Import GitHub repo
2. Set **Root Directory** to `frontend`
3. Add env var: `VITE_API_URL=https://your-backend.up.railway.app`
4. Deploy — uses [`frontend/vercel.json`](frontend/vercel.json)

### CI/CD

GitHub Actions runs on push/PR to `main`: backend pytest, frontend build, pipeline tests. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Phase 1–7 Summary

See [`LexSearch_Architecture.md`](LexSearch_Architecture.md) for the full specification.

```powershell
docker compose up postgres redis elasticsearch qdrant -d
cd backend
.\venv\Scripts\activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

## Quick Start (Docker)

```powershell
cp .env.example .env
docker compose up --build
docker compose exec backend alembic upgrade head
```

## Stack verification

```powershell
.\scripts\verify_stack.ps1
```

## Project Structure

See `LexSearch_Architecture.md` for the full specification and build phases.
