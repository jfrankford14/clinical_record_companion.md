# reconcile Cloud Run service

FastAPI service that reads two parsed C-CDA JSON payloads from Cloud Storage, merges them into a unified medication/allergy picture, and surfaces discrepancies, drug–drug interaction (DDI) alerts, and allergy conflicts.

## Running locally

```bash
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=~/path/to/key.json  # if needed for GCS access
uvicorn app:app --reload
```

> **Note:** For offline unit tests the service gracefully falls back to Python's built-in `csv` module when `pandas` is unavailable, and stub FastAPI/Pydantic classes let pure functions execute without the full web stack. Deployments should still include the listed requirements.

Call the API with:

```bash
curl -X POST "http://localhost:8000/reconcile" \
  -H "Content-Type: application/json" \
  -d '{"a_json_gcs":"gs://bucket/a.json","b_json_gcs":"gs://bucket/b.json"}'
```

## Container build (Cloud Run)

```bash
gcloud run deploy reconcile \
  --source=. \
  --region=${REGION:-us-central1} \
  --allow-unauthenticated
```

To restrict later, replace `--allow-unauthenticated` with `--no-allow-unauthenticated` and grant the desired service account the `roles/run.invoker` role.

## Response payload

```json
{
  "unified_meds": [
    {"name": "Metformin", "sources": ["A", "B"]}
  ],
  "unified_allergies": [
    {"substance": "Penicillin", "reaction": "Rash", "severity": "moderate", "status": "active", "source": "A"}
  ],
  "discrepancies": [
    {"name": "Gliburide", "only_in": "B"}
  ],
  "dd_interactions": [
    {"drug_a": "Warfarin", "drug_b": "Amoxicillin", "severity": "moderate", "note": "May increase bleeding risk"}
  ],
  "allergy_conflicts": [
    {"substance": "Penicillin", "linked_drug": "Amoxicillin", "severity": "moderate"}
  ],
  "sources": {"A": "North Valley Hospital", "B": "Southside Clinic"},
  "tags": ["ddi_detected", "allergy_conflict", "med_discrepancy"]
}
```
