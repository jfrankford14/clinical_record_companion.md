# Streamlit demo (optional)

Lightweight interface that uploads two C-CDA XML files to Cloud Storage, invokes the `parse-ccda` Cloud Function, then calls the `reconcile` Cloud Run service to visualize unified medication/allergy insights.

## Setup

```bash
pip install -r requirements.txt
export PROJECT_ID=us-con-gcp-sbx-0001190-100925
export RAW_BUCKET=${PROJECT_ID}-ccda-raw
export PARSED_BUCKET=${PROJECT_ID}-ccda-parsed
export PARSE_FUNCTION_URL=https://<region>-<project>.cloudfunctions.net/parse-ccda
export RECONCILE_URL=https://<region>-run.googleapis.com/v1/projects/<project>/locations/<region>/services/reconcile
streamlit run app.py
```

Use sandbox credentials or `gcloud auth application-default login` to grant the app Cloud Storage access. Uploaded files land under `uploads/` prefixes to keep the bucket tidy.
