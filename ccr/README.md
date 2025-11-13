# Clinical Record Companion demo

Minimal, production-lean implementation of the Clinical Record Companion focused on medication safety and reconciliation across Continuity of Care Documents (C-CDA).

## Architecture

```
+---------------------+        +-------------------------+        +-----------------------+
| Raw CCDA bucket     |        | Cloud Function (Gen2)   |        | Cloud Run (FastAPI)   |
| gs://<proj>-ccda-raw|--POST->| parse-ccda              |--JSON->| reconcile             |
+---------------------+        |  - Extract meds/allergies|        |  - Merge A vs B       |
                                |  - Write parsed JSON     |        |  - DDI + allergy flags|
                                +-------------------------+        +-----------+-----------+
                                                                              |
                                                                              v
                                                               Vertex AI Agent Builder tools
                                                               + optional Streamlit front-end
```

* Parsed JSON objects are written to `gs://<proj>-ccda-parsed/*`. Both the agent and the Streamlit UI call these services.

## Deploy

1. Copy `infra/env.example` to `.env` and edit as needed.
2. Source the file: `set -a && source infra/.env && set +a` (or export the variables manually).
3. Run the deployment helper:

   ```bash
   cd ccr/infra
   ./deploy.sh
   ```

   The script enables required services, creates the raw/parsed/reference buckets, deploys the Cloud Function, and deploys the Cloud Run service. It prints the HTTPS endpoints for both at the end.

## Smoke tests

After deployment, substitute the printed endpoints and a sample file path.

```bash
# Trigger the parser
gcloud functions call parse-ccda \
  --gen2 \
  --region=us-central1 \
  --data='{ "gcs_uri": "gs://us-con-gcp-sbx-0001190-100925-ccda-raw/demo/01_PrimaryCare_Initial_Diagnosis.xml" }'

# Or via curl against the HTTPS URL
curl -X POST "https://<function-endpoint>" \
  -H "Content-Type: application/json" \
  -d '{"gcs_uri":"gs://us-con-gcp-sbx-0001190-100925-ccda-raw/demo/01_PrimaryCare_Initial_Diagnosis.xml"}'

# Reconcile two parsed JSON blobs
curl -X POST "https://<cloud-run-url>/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
        "a_json_gcs": "gs://us-con-gcp-sbx-0001190-100925-ccda-parsed/demo/01_PrimaryCare_Initial_Diagnosis.json",
        "b_json_gcs": "gs://us-con-gcp-sbx-0001190-100925-ccda-parsed/demo/09_Endocrinology___Medication_Adjustment_Visit.json"
      }'
```

The reconcile service returns unified medications, allergies, discrepancies, DDI hits, and allergy conflicts.

## Wire up Vertex AI Agent Builder

1. In Agentspace, open the Gemini Enterprise agent.
2. Add a tool for the Cloud Function using the schema from `agent/tools.json` (`parse_ccda`).
3. Add a second tool pointing to the Cloud Run service (`reconcile_records`).
4. Paste `agent/system_prompt.txt` into the system instructions.
5. Provide the HTTPS endpoints output by `deploy.sh`. Start testing with prompts such as:
   - "Parse the latest external CCDAs and summarize medication discrepancies with sources."
   - "Highlight any drug interactions or allergy conflicts before prescribing."

> **Note:** Vertex AI Search datastore `patient-data_1762901262843` is not yet wired in. See `agent/README.md` for the future enhancement placeholder.

## Optional Streamlit UI

* App: `ui/app.py`
* Configure environment variables `PROJECT_ID`, `RAW_BUCKET`, `PARSE_FUNCTION_URL`, and `RECONCILE_URL`.
* Run locally with `streamlit run ccr/ui/app.py` to upload two CCDAs and visualize the reconciliation output.

## Local validation & tests

The repository includes lightweight tests to guard the CCDA parsing helpers and reconciliation logic.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r functions/parse_ccda/requirements.txt -r services/reconcile/requirements.txt pytest
pytest

# Optional: confirm all modules compile cleanly
python -m compileall ..
```

For environments without direct internet access, the reconciliation service falls back to Python's `csv` module if `pandas` is missing, and local unit tests stub FastAPI/Pydantic while keeping production deployments unchanged.

## Test data quick reference

The repository contains a longitudinal synthetic diabetes journey (`data/diabetes/*.xml`) spanning 20 encounters from 2022–2024 across primary care, endocrinology, labs, emergency visits, and pharmacy follow-ups. Files are ordered chronologically: `01_...xml` through `20_...xml`. Each file includes medication and allergy updates relevant to medication reconciliation (e.g., insulin titration, sulfonylurea additions, antibiotic courses).

## Updated 3-minute demo script

**Goal:** Show how Clinical Record Companion accelerates medication reconciliation using the provided 20-file diabetes journey.

1. **Set the stage (0:00–0:30)**
   - "We just received 20 C-CDA packets for Maria Gonzales, a patient with type 2 diabetes transferring to our clinic. They span primary care, endocrinology, labs, and pharmacy visits from early 2022 through late 2024."
   - "I'll drop the first two records—`01_PrimaryCare_Initial_Diagnosis.xml` and `02_LabFacility_Initial_HbA1c.xml`—into the raw bucket to show the workflow."

2. **Trigger parsing (0:30–1:15)**
   - Execute the Cloud Function call (via `deploy.sh` output URL) for each file: "The function extracts patient identifiers, encounter dates, meds like Metformin initiation, and Penicillin allergy entries. It saves structured JSON back to `gs://<project>-ccda-parsed/...`."
   - Mention that repeating the call for files `03` through `20` takes seconds thanks to automation.

3. **Run reconciliation (1:15–2:00)**
   - Pick two contrasting encounters—e.g., `09_Endocrinology___Medication_Adjustment_Visit.json` vs `12_Emergency_Department___DKA_Visit.json`—and call the Cloud Run `/reconcile` endpoint.
   - Highlight the output: "Unified meds show basal-bolus insulin from the endo visit and the ED's short-term antibiotics. Discrepancies flag that the ED list still includes Sulfonylurea even though endocrinology discontinued it." Mention DDIs (Warfarin + Amoxicillin example) if present.

4. **Agent perspective (2:00–2:30)**
   - In Vertex AI Agent Builder, show the agent calling `parse_ccda` for two facilities and then `reconcile_records`. "The agent cites North Valley Hospital (March 2023) vs Southside Clinic (April 2023) while summarizing med conflicts."

5. **Close with value (2:30–3:00)**
   - "Instead of manually reading 20 XML files, clinicians get a clean diff, flagged interactions, and allergy conflicts in under a minute."
   - "Once Vertex AI Search access is granted, we can ground additional context like labs and care plans using datastore `patient-data_1762901262843`."

Use this script alongside the provided prompts to stay aligned with the curated dataset.
