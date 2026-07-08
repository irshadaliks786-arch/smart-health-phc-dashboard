# PHC/CHC Health Ops — Hackathon rebuild (updated norms)

Rebuilt from the original `healthcare-extension` solution (Code for Communities
hackathon) to match the revised rules:

| Norm (as given) | How it's met |
|---|---|
| Sirf Google ke tools | Storage = Firebase/Firestore. AI = Gemini (`google-generativeai`). Deployment = Google Cloud Run. No other cloud/LLM SDK anywhere in the codebase. |
| Koi bhi non-Google LLM/tool nahi | Only `google-generativeai` is imported for AI; core analytics (KPI, forecasting, redistribution) is plain deterministic Python, not AI at all. |
| Deterministic UX | Every panel is an explicit `loading → success \| error` state machine (`useFetchState.js`) with a fixed-size skeleton per state — no random content, no layout shift, no indefinite spinners. |
| AI output + guardrails | `/api/insights` (Gemini) is schema-validated, entity-checked against real PHC/district IDs, length-capped, and has a deterministic template fallback if the model fails/hallucinates — see `backend/app/gemini_guardrails.py`. |
| Skeleton UI | `frontend/src/skeletons/Skeleton.jsx` — fixed-dimension shimmer placeholders matching each panel's real layout exactly. |
| FastAPI backend | `backend/` — FastAPI + pandas over the same pipeline outputs as the original solution. |
| React frontend | `frontend/` — Vite + React, no UI framework lock-in. |
| Firebase storage | `backend/app/data_store.py` reads Firestore when `USE_FIRESTORE=true`; `backend/scripts/seed_firestore.py` pushes the CSV outputs there. Falls back to the bundled CSV cache otherwise, so the app runs with zero cloud credentials for local dev/judging. |
| Docker, live URL | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` for local; `DEPLOY.md` for a live Cloud Run URL. |

## Project layout

```
backend/            FastAPI app (deterministic analytics API + guardrailed Gemini insights)
  app/
    main.py          FastAPI entrypoint, routers, CORS
    config.py        settings (all Google integrations are opt-in via env vars)
    data_store.py     Firestore-or-CSV data layer
    gemini_guardrails.py   the one AI surface, with validation + fallback
    schemas.py        pydantic response contracts
    routers/          districts, phcs, forecasts, redistribution, insights
    data_cache/        bundled CSV snapshot (from the original pipeline's 02_Outputs/)
  scripts/seed_firestore.py   push CSVs into Firestore
  Dockerfile
frontend/            React (Vite) SPA
  src/
    lib/api.js, useFetchState.js
    skeletons/Skeleton.jsx
    components/       DistrictSummary, PhcTable, RedistributionList, InsightsPanel
  Dockerfile
docker-compose.yml
DEPLOY.md            Cloud Run deployment (live URL)
```

The original data-generation/ETL/forecasting scripts (`00_Scripts/`) aren't
touched — this rebuild consumes their `02_Outputs/*.csv`. Re-run that pipeline
whenever you want fresh numbers, then either replace `backend/app/data_cache/`
or re-run `seed_firestore.py`.

## Run it locally — fastest path (no Google credentials needed)

```bash
docker compose up --build
```
- Backend: http://localhost:8080 (docs at `/docs`)
- Frontend: http://localhost:3000

This runs fully deterministic: analytics from the bundled CSVs, AI insights
from the deterministic fallback template (Gemini disabled by default).

## Run it locally — without Docker

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# frontend (new terminal)
cd frontend
npm install
cp .env.example .env      # VITE_API_BASE_URL=http://localhost:8080
npm run dev                # http://localhost:5173
```

## Turning on live Google services

```bash
cd backend
cp .env.example .env
# edit .env:
#   USE_FIRESTORE=true, FIREBASE_PROJECT_ID=..., GOOGLE_APPLICATION_CREDENTIALS set in shell
#   USE_GEMINI=true, GEMINI_API_KEY=...
python scripts/seed_firestore.py     # one-time: push CSVs into Firestore
```
Restart the backend — `/api/*` now reads Firestore and `/api/insights` calls
Gemini (still guardrailed; falls back automatically if the call fails).

## Live deployment (Google Cloud Run)

See `DEPLOY.md` for the full `gcloud`/Docker sequence to get a public URL
backed entirely by Google infrastructure.
