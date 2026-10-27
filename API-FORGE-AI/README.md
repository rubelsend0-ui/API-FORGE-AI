# API Forge AI

Turn a ZIP-based software project into a working REST API — Android app
+ FastAPI backend.

## Honest status of this repository

This repo is an **early, working MVP slice**, not the full platform
described in the product spec. It was built incrementally and every
piece below was actually run and tested in the environment that built
it (except the Android/Kotlin code, which has no Android SDK available
to compile here — see "What's not verified" below).

### Implemented and tested right now

- **Backend** (`backend/`): FastAPI app with SQLite storage.
  - `GET /health`
  - `POST /api/v1/projects`, `GET /api/v1/projects`, `GET /api/v1/projects/{id}`
  - `POST /api/v1/projects/{id}/upload` — accepts a ZIP, enforces a size limit
  - `POST /api/v1/projects/{id}/analyze` — runs a **real** static analyzer
    (no external deps) that detects project language/framework, rejects
    zip bombs and path-traversal entries, and returns a structured report
  - Shared `X-API-Key` auth on every `/api/v1/*` route
  - 23 passing unit tests covering the analyzer, the database layer, and
    file storage (`backend/tests/`) — run with `pytest -v` from `backend/`
- **Android app** (`android/`): Kotlin + Jetpack Compose skeleton —
  Home, Import (native ZIP picker), Analysis (shows the real backend
  report), Settings screens; a Retrofit client wired to the backend's
  actual endpoints. Dark graphite/navy theme with electric-blue/cyan
  accents per the product's visual direction.
- **CI**: `.github/workflows/backend-tests.yml` runs the backend test
  suite on every push/PR. `.github/workflows/android-build.yml` builds
  the debug APK and uploads it as an artifact named
  `api-forge-ai-debug-apk`.

### What's not verified

- The Android/Kotlin code was hand-written against standard, well-known
  APIs but **not compiled** — there is no Android SDK or `kotlinc` in
  the sandbox that built this repo. The GitHub Actions workflow is what
  actually proves it builds; see "First push" below.
- There is **no committed Gradle wrapper jar** (`gradle-wrapper.jar` is
  a binary that a real local Gradle install generates; none was
  available here). `android-build.yml` works around this by using
  `gradle/actions/setup-gradle` instead of `./gradlew`. For local
  builds, open `android/` in Android Studio (it will offer to generate
  the wrapper for you), or run `gradle wrapper --gradle-version 8.10.2`
  once if you have Gradle installed locally, then commit the result.

### Not implemented yet (do not assume these work)

- GitHub OAuth/App integration, repository creation, and pushing
  generated code (Section 7 of the spec)
- Render deployment integration (Section 8)
- The API-generation pipeline / isolated build workers (Sections 5–6)
- CVE/vulnerability intel, workflow automation — not part of this spec,
  mentioned here only to be clear they're absent
- Multi-user auth — this MVP uses one shared API key

These all need real credentials (a GitHub App, a Render API key) that
only you can provision, plus considerably more implementation work.
Treat this repo as the foundation to build those on, not a finished
product.

## Project layout

```
API-FORGE-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app + startup wiring
│   │   ├── config.py            Env-driven settings
│   │   ├── database.py          SQLite persistence (stdlib sqlite3)
│   │   ├── security.py          Shared API-key auth dependency
│   │   ├── schemas.py           Pydantic request/response models
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   └── projects.py
│   │   └── services/
│   │       ├── zip_analyzer.py  Real ZIP analysis (pure stdlib, tested)
│   │       └── storage.py       Local file storage for uploaded ZIPs
│   ├── tests/                   23 passing unit tests
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── android/
│   ├── app/src/main/java/com/apiforge/ai/
│   │   ├── MainActivity.kt
│   │   ├── ui/{theme,navigation,screens}/
│   │   ├── data/                Retrofit API client + models
│   │   └── viewmodel/           ProjectViewModel (upload+analyze flow)
│   ├── settings.gradle.kts, build.gradle.kts, gradle.properties
├── .github/workflows/
│   ├── backend-tests.yml
│   └── android-build.yml
└── docs/
```

## Run the backend locally

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit APP_SECRET_KEY if you like
uvicorn app.main:app --reload --port 8000
```

Test it:

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/v1/projects \
  -H "X-API-Key: dev-secret-change-me" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project"}'
```

## Run the backend tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

## Push to GitHub

```bash
cd API-FORGE-AI
git init                                   # only if not already a repo
git add .
git commit -m "API Forge AI: MVP backend + Android skeleton"
git branch -M main
git remote add origin https://github.com/<your-username>/API-FORGE-AI.git
git push -u origin main
```

## Build the Android APK via GitHub Actions

1. Push to `main` (triggers automatically), or run it manually:
   ```bash
   gh workflow run android-build.yml
   ```
2. Watch it:
   ```bash
   gh run watch
   ```
3. Download the APK once it succeeds:
   ```bash
   gh run download --name api-forge-ai-debug-apk
   ```

(`gh` is the GitHub CLI. Without it, use the Actions tab on GitHub —
the artifact is listed on the workflow run's summary page.)

See `docs/BACKEND_SETUP.md` and `docs/ANDROID_BUILD.md` for more detail.
