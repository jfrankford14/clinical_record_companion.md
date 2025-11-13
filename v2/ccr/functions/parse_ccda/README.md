# parse_ccda (v2)

This Cloud Function ingests a C-CDA XML document from GCS, performs a lenient parse using `lxml`,
and emits a normalized JSON structure with medications, allergies, problems, encounters, labs,
and provenance metadata.

## Local testing

- `make test` → run the full pytest suite, including parser and service fixtures.
- `make typecheck` → `python -m compileall v2` to ensure there are no syntax errors before deployment.
- `make smoke-local-parse INPUT=data/diabetes/01_PrimaryCare_Initial_Diagnosis.xml OUTPUT=/tmp/parsed.json` → wrap the
  CLI helper in `scripts/local_parse.sh` for fast iteration without GCS.

## Deployment

```
gcloud functions deploy parse-ccda-v2 \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=v2/ccr/functions/parse_ccda \
  --entry-point=parse_ccda \
  --trigger-http \
  --set-env-vars=PARSED_BUCKET=${PARSED_BUCKET}
```

### Smoke test

```bash
curl -s -X POST "https://parse-ccda-v2-${REGION}-${PROJECT}.cloudfunctions.net/parse_ccda" \
  -H 'Content-Type: application/json' \
  -d '{"gcs_uri":"gs://${BUCKET}/sample.xml"}' | jq
```

## Agent Builder wiring

1. Import `v2/ccr/infra/openapi/combined.json` into Agent Builder.
2. Map the `/` operation to the deployed `parse-ccda-v2` URL and enable service-account auth with read access to the
   source bucket and write access to `${PARSED_BUCKET}`.
3. Save and test the action to verify the `parsed_json_gcs` + `summary` contract.
