#!/usr/bin/env bash
# Deploy the GridPulse container to Cloud Run.
#
# Run this from Google Cloud Shell (reliable Google-network connectivity), or any machine
# whose network can reach the Cloud Run / Cloud Build / Resource Manager APIs:
#
#     git clone https://github.com/Auenchanters/Gen-ai-2 && cd Gen-ai-2
#     bash infra/deploy_cloudrun.sh
#
# Assumes the BigQuery forecast table is already loaded (infra/load_bigquery.py, which
# infra/deploy.sh runs). Idempotent — safe to re-run.
set -euo pipefail
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

PROJECT="${PROJECT:-gen-ai-2-500107}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-gridpulse}"
DATASET="${DATASET:-gridpulse}"
SA_NAME="gridpulse-run"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"

gcloud config set project "${PROJECT}"

echo ">> Enabling APIs"
gcloud services enable \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  aiplatform.googleapis.com bigquery.googleapis.com

echo ">> Runtime service account + roles (idempotent)"
gcloud iam service-accounts create "${SA_NAME}" --display-name="GridPulse Cloud Run" 2>/dev/null || true
for ROLE in roles/bigquery.dataViewer roles/bigquery.jobUser roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA}" --role="${ROLE}" --condition=None >/dev/null
done

echo ">> Granting the build (default compute) service account build permissions"
# New projects ship the default compute SA with no roles, so Cloud Build (used by
# `run deploy --source`) can't read the source bucket or push the image. Grant the
# minimum needed for source builds.
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')"
BUILD_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for ROLE in roles/cloudbuild.builds.builder roles/storage.objectViewer \
            roles/artifactregistry.writer roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${BUILD_SA}" --role="${ROLE}" --condition=None >/dev/null
done

echo ">> Deploying to Cloud Run (builds the Dockerfile via Cloud Build)"
gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --service-account "${SA}" \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "USE_BIGQUERY=1,USE_GEMINI=1,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET},GEMINI_MODEL=gemini-2.5-flash"

echo ">> Service URL:"
gcloud run services describe "${SERVICE}" --region "${REGION}" --format='value(status.url)'
