# LexSearch Data Pipeline (Phase 2)

Ingests Indian legal judgements from [indiankanoon.org](https://indiankanoon.org) into PostgreSQL, Elasticsearch, and Qdrant.

## Prerequisites

1. **Infrastructure running**
   ```powershell
   cd d:\LexSearch
   docker compose up postgres redis elasticsearch qdrant -d
   ```

2. **Python environment**
   ```powershell
   cd d:\LexSearch
   python -m venv data_pipeline\venv
   .\data_pipeline\venv\Scripts\activate
   pip install -r data_pipeline\requirements.txt
   pip install -r backend\requirements.txt   # for PostgreSQL models
   copy .env.example .env
   ```

3. **Database migrated**
   ```powershell
   cd backend
   alembic upgrade head
   ```

## Qdrant Setup

### Local (recommended for development)
Qdrant runs via Docker Compose on `http://localhost:6333`. Set in `.env`:
```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

### Qdrant Cloud (free tier)
1. Create a cluster at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Copy cluster URL and API key to `.env`:
```
QDRANT_URL=https://xxxxxxxx.eu-central.aws.cloud.qdrant.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION_NAME=legal_judgements
```

## Run Pipeline

Full pipeline (scrape 1000 → process → ingest → verify):
```powershell
cd d:\LexSearch
python -m data_pipeline.run_pipeline --step all --limit 1000
```

Individual steps:
```powershell
python -m data_pipeline.run_pipeline --step scrape --limit 1000
python -m data_pipeline.run_pipeline --step process
python -m data_pipeline.run_pipeline --step ingest
python -m data_pipeline.run_pipeline --step verify
```

Re-ingest from existing processed files (recreate ES index + Qdrant collection):
```powershell
python -m data_pipeline.run_pipeline --step ingest --recreate
```

## Output Files

| Path | Contents |
|------|----------|
| `data_pipeline/data/raw/documents.jsonl` | Raw scraped judgements |
| `data_pipeline/data/processed/documents.jsonl` | Cleaned + metadata |
| `data_pipeline/data/chunks/chunks.jsonl` | 800-char chunks (150 overlap) |

## Tests

```powershell
pytest data_pipeline/tests -q
```

## Notes

- Scraping uses **1.5s delay** between requests (configurable via `SCRAPE_DELAY_SECONDS`).
- Scraping **1000 documents** takes ~25–40 minutes depending on network.
- Pipeline supports **resume**: re-running scrape skips already-saved document IDs.
- Embeddings use `all-MiniLM-L6-v2` (384 dimensions) per architecture spec.
