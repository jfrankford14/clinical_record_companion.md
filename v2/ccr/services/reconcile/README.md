# reconcile (v2)

FastAPI service that consumes two parsed CCDA JSON documents from GCS, merges medication and
allergy lists, and emits discrepancy data, drug-drug interactions, and allergy conflicts.

## Local development

- `make test`
- `make typecheck`
- `make smoke-local-reconcile A=tests/fixtures/parsed_record_a.json B=tests/fixtures/parsed_record_b.json`
- `uvicorn v2.ccr.services.reconcile.app:app --reload`

## Deployment

```
gcloud run deploy reconcile-v2 \
  --source=v2/ccr/services/reconcile \
  --region=us-central1 \
  --allow-unauthenticated
```

### Smoke test

```bash
curl -s -X POST "https://reconcile-v2-${REGION}-${PROJECT}.a.run.app/reconcile" \
  -H 'Content-Type: application/json' \
  -d '{"a_json_gcs":"gs://${BUCKET}/a.json","b_json_gcs":"gs://${BUCKET}/b.json"}' | jq
```

## Agent Builder wiring

1. Import `v2/ccr/infra/openapi/combined.json`.
2. Point `/reconcile` at the Cloud Run URL with service-account auth (grant Storage Object Viewer access to the
   parsed bucket).
3. Tag the action set with `v2_mvp` so downstream workflows can key off the safety logic metadata.
