#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

: "${PROJECT_ID:?Set PROJECT_ID in your environment or in env.example}"
REGION="${REGION:-us-central1}"
RAW_BUCKET="${RAW_BUCKET:-${PROJECT_ID}-ccda-raw}"
PARSED_BUCKET="${PARSED_BUCKET:-${PROJECT_ID}-ccda-parsed}"
REF_BUCKET="${REF_BUCKET:-${PROJECT_ID}-ref}"
CLOUD_FUNCTION_NAME="${CLOUD_FUNCTION_NAME:-parse-ccda}"
CLOUD_RUN_NAME="${CLOUD_RUN_NAME:-reconcile}"

printf "\n==> Configuring project %s in region %s\n" "$PROJECT_ID" "$REGION"
gcloud config set project "$PROJECT_ID" >/dev/null

echo "==> Enabling required services"
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  eventarc.googleapis.com

function ensure_bucket() {
  local bucket="$1"
  if gsutil ls -b "gs://${bucket}" >/dev/null 2>&1; then
    echo "Bucket gs://${bucket} already exists"
  else
    gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://${bucket}"
  fi
}

echo "==> Creating storage buckets if missing"
ensure_bucket "$RAW_BUCKET"
ensure_bucket "$PARSED_BUCKET"
ensure_bucket "$REF_BUCKET"

echo "==> Deploying Cloud Function ${CLOUD_FUNCTION_NAME}"
gcloud functions deploy "$CLOUD_FUNCTION_NAME" \
  --gen2 \
  --runtime=python311 \
  --region="$REGION" \
  --source="${ROOT_DIR}/functions/parse_ccda" \
  --entry-point=parse_ccda \
  --trigger-http \
  --set-env-vars="PROJECT_ID=${PROJECT_ID},PARSED_BUCKET=${PARSED_BUCKET}" \
  --allow-unauthenticated

echo "==> Deploying Cloud Run service ${CLOUD_RUN_NAME}"
gcloud run deploy "$CLOUD_RUN_NAME" \
  --region="$REGION" \
  --source="${ROOT_DIR}/services/reconcile" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --allow-unauthenticated

PARSE_URL=$(gcloud functions describe "$CLOUD_FUNCTION_NAME" --region="$REGION" --format='value(serviceConfig.uri)')
RUN_URL=$(gcloud run services describe "$CLOUD_RUN_NAME" --region="$REGION" --format='value(status.url)')

echo "\nDeployment complete."
echo "parse-ccda URL: ${PARSE_URL}"
echo "reconcile URL: ${RUN_URL}"
echo "Remember to upload reference CSVs to ${REF_BUCKET} if you wish to share them across environments."
