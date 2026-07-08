# Deploy — Google Cloud Run (live URL)

Norms compliance: deployment uses **only Google infra** — Cloud Run (containers),
Artifact Registry (image storage), and optionally Firestore/Gemini. No other
cloud/PaaS is used anywhere in this guide.

Prereqs: a GCP project with billing enabled, and the `gcloud` CLI installed
and authenticated (`gcloud auth login`).

## 0. One-time setup

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=asia-south1        # Mumbai — closest to Haryana PHC network

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  firestore.googleapis.com

gcloud artifacts repositories create healthcare-hackathon \
  --repository-format=docker --location=$REGION
```

## 1. Deploy the backend

```bash
cd backend
gcloud builds submit \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/backend

gcloud run deploy healthcare-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/backend \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars USE_FIRESTORE=false,USE_GEMINI=false
```

Grab the printed Service URL (e.g. `https://healthcare-backend-xxxx-el.a.run.app`) —
you'll need it in step 2. This works with no keys at all (deterministic CSV
cache + deterministic insight fallback). To turn on live Google AI/storage:

```bash
gcloud run deploy healthcare-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/backend \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars USE_FIRESTORE=true,FIREBASE_PROJECT_ID=$PROJECT_ID,USE_GEMINI=true,GEMINI_API_KEY=$GEMINI_API_KEY
```
(Cloud Run's default service account already has project credentials, so
`GOOGLE_APPLICATION_CREDENTIALS` doesn't need to be set explicitly on Cloud Run
itself — only for local/manual `seed_firestore.py` runs.)

If you enabled Firestore, seed it once from your machine:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export FIREBASE_PROJECT_ID=$PROJECT_ID
python backend/scripts/seed_firestore.py
```

## 2. Deploy the frontend

The frontend needs the backend URL baked in at build time (Vite env vars are
compile-time), so build the image locally with `docker` and push it —
straightforward, and keeps Docker in the loop as required:

```bash
cd ../frontend
export BACKEND_URL=$(gcloud run services describe healthcare-backend --region $REGION --format='value(status.url)')

gcloud auth configure-docker ${REGION}-docker.pkg.dev

docker build --build-arg VITE_API_BASE_URL=$BACKEND_URL \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/frontend .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/frontend

gcloud run deploy healthcare-frontend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/healthcare-hackathon/frontend \
  --region $REGION \
  --allow-unauthenticated
```

Grab this Service URL too — that's your **live URL** to submit to the hackathon.

## 3. Lock down CORS (optional, recommended before submission)

```bash
export FRONTEND_URL=$(gcloud run services describe healthcare-frontend --region $REGION --format='value(status.url)')
gcloud run services update healthcare-backend \
  --region $REGION \
  --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL
```

## Why Cloud Run specifically

- It's Google's own container hosting product — satisfies "google ke tools use
  krne hai sirf" for the deployment leg, same as Firestore/Gemini for the app leg.
- Pay-per-request, scales to zero — fine for a hackathon demo budget.
- Reads `$PORT` at runtime, which both Dockerfiles in this repo already respect.
