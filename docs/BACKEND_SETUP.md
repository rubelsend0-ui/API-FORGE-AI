# Backend Setup

## Local development

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for interactive OpenAPI docs (provided
automatically by FastAPI).

## Configuration

All configuration is environment-driven — see `.env.example` for the
full list. The important ones for this MVP slice:

| Variable | Purpose |
|---|---|
| `APP_SECRET_KEY` | Shared API key every client must send as `X-API-Key` |
| `DATABASE_PATH` | SQLite file path |
| `STORAGE_DIR` | Where uploaded ZIPs are saved |
| `MAX_UPLOAD_SIZE_BYTES` | Upload size limit (default 50 MB) |
| `CORS_ALLOW_ORIGINS` | Comma-separated allowed origins |

`GITHUB_*` and `RENDER_API_KEY` are placeholders for integrations that
are **not implemented yet** in this slice.

## Running tests

```bash
cd backend
pytest -v
```

All 23 tests are offline and deterministic — no network access or API
keys required.

## Docker

```bash
cd backend
docker build -t api-forge-ai-backend .
docker run -p 8000:8000 --env-file .env api-forge-ai-backend
```

## Next steps toward the full spec

This backend only covers project CRUD + ZIP analysis. To reach the
full product spec you'd still need to add, roughly in this order:

1. Real per-user authentication (replace the shared API key).
2. A GitHub App integration for repo creation/push (Section 7 of the spec).
3. An isolated worker (e.g. a sandboxed container) for any code
   generation or build step that touches untrusted uploaded code.
4. A Render API integration for deployment + health-check verification
   (Section 9).

None of that is safe to fake — each should be built and tested against
the real GitHub/Render APIs once you have credentials for them.
