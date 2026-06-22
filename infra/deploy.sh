#!/usr/bin/env bash
# Deploy GridPulse to Google Cloud: BigQuery dataset + GCS bucket + Cloud Run service.
# Idempotent — safe to re-run. Requires: gcloud, bq, and `uv` for local data generation.
set -euo pipefail

# Run non-interactively (auto-confirm Artifact Registry repo creation, etc.).
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

PROJECT="${PROJECT:-gen-ai-2-500107}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-gridpulse}"
DATASET="${DATASET:-gridpulse}"
BUCKET="gs://${PROJECT}-gridpulse"
SA_NAME="gridpulse-run"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
PYTHON_CMD="${PYTHON_CMD:-uv run --extra cloud python}"

echo ">> Using project ${PROJECT} (region ${REGION})"
gcloud config set project "${PROJECT}"

echo ">> Enabling required APIs"
gcloud services enable \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  bigquery.googleapis.com storage.googleapis.com aiplatform.googleapis.com

echo ">> Creating GCS bucket (idempotent)"
gcloud storage buckets create "${BUCKET}" --location="${REGION}" 2>/dev/null || true

echo ">> Generating data + forecast locally (GPU auto-used if available)"
${PYTHON_CMD} -m pipeline.generate_data --days 14 --meters-per-zone 80
${PYTHON_CMD} -m pipeline.accelerate
${PYTHON_CMD} -m pipeline.train

echo ">> Uploading raw data to Cloud Storage"
gcloud storage cp data/readings.parquet data/weather.parquet "${BUCKET}/raw/"

echo ">> Loading forecast into BigQuery (Python client; creates the dataset if needed)"
${PYTHON_CMD} infra/load_bigquery.py --project "${PROJECT}" --dataset "${DATASET}" --location "${REGION}"

echo ">> Creating least-privilege service account (idempotent)"
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="GridPulse Cloud Run" 2>/dev/null || true
for ROLE in roles/bigquery.dataViewer roles/bigquery.jobUser roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA}" --role="${ROLE}" --condition=None >/dev/null
done

echo ">> Deploying to Cloud Run (builds the Dockerfile via Cloud Build)"
gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --service-account "${SA}" \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "USE_BIGQUERY=1,USE_GEMINI=1,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET},GEMINI_MODEL=gemini-2.5-flash"

echo ">> Deployed. Service URL:"
gcloud run services describe "${SERVICE}" --region "${REGION}" --format='value(status.url)'
