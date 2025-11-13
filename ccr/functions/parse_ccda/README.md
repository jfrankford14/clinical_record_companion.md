# parse-ccda Cloud Function

Parses Continuity of Care Documents (C-CDA) stored in Cloud Storage into a concise JSON representation used by the reconciliation service and Vertex AI Agent Builder.

## Deployment

```bash
gcloud functions deploy parse-ccda \
  --gen2 \
  --runtime=python311 \
  --region=${REGION:-us-central1} \
  --source=. \
  --entry-point=parse_ccda \
  --trigger-http \
  --set-env-vars=PROJECT_ID=${PROJECT_ID} \
  --allow-unauthenticated
```

Set `PARSED_BUCKET` if you want to override the default destination bucket name of `${PROJECT_ID}-ccda-parsed`.

## Request format

```json
{"gcs_uri": "gs://<PROJECT>-ccda-raw/path/to/file.xml"}
```

## Response format

```json
{"parsed_json_gcs": "gs://<PROJECT>-ccda-parsed/path/to/file.json"}
```

The Cloud Function writes the JSON to the parsed bucket and returns its URI. Logs only reference the source and destination URIs so no patient data appears in log entries.

## Local CLI helper

For quick experiments without deploying to Cloud Functions you can call the module directly:

```bash
python -m ccr.functions.parse_ccda.main data/diabetes/01_PrimaryCare_Initial_Diagnosis.xml \
  --output /tmp/initial_diagnosis.json
```

The helper reuses the same extraction logic as the Cloud Function. If `--output` is omitted, the normalized JSON is printed to stdout instead of being written to disk.
