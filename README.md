# Clinical Record Companion demo

This repository contains a deployable, medication-focused slice of the Clinical Record Companion experience. It parses Continuity of Care Documents (C-CDA) into normalized JSON, reconciles medication/allergy differences between facilities, and provides assets for Vertex AI Agent Builder plus an optional Streamlit UI.

For component-level details see [`ccr/README.md`](ccr/README.md). The highlights are repeated below for convenience.

## Datasets & scenarios

Two curated data packs live under `data/` so a single build can validate the longitudinal diabetes journey and the focused medication-safety checks:

- **`data/diabetes/`** – 20 CCDAs that follow John Michael Martinez through a 2022–2024 diabetes journey. `manifest.json` pairs representative encounters (e.g., early vs late endocrinology) for smoke and scenario testing.
- **`data/med-safety-contra/`** – Targeted CCDAs for Warfarin + Amoxicillin DDIs, Sulfa allergy conflicts vs TMP-SMX, and duplicate sulfonylurea therapy. The README lists expected findings for each scenario.

`tests/test_scenarios.py` discovers every `data/**/manifest.json`, uploads the referenced CCDAs (when the GCP env vars are set), invokes `parse-ccda` and `/reconcile`, and asserts that each manifest’s DDIs, allergy conflicts, or discrepancy hints appear. When credentials, buckets, or endpoints are missing the test marks itself `xfail` instead of failing CI.

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

## Deploy workflow

1. Copy `ccr/infra/env.example` to `ccr/infra/.env` and edit values if needed.
2. Export the variables: `set -a && source ccr/infra/.env && set +a`.
3. Run `ccr/infra/deploy.sh`. The script enables GCP APIs, creates Cloud Storage buckets, deploys the Cloud Function (`parse-ccda`), and deploys the Cloud Run service (`reconcile`). It prints both HTTPS endpoints when finished.

Buckets created:
- `${PROJECT_ID}-ccda-raw`
- `${PROJECT_ID}-ccda-parsed`
- `${PROJECT_ID}-ref`

## Smoke tests

Set the shared environment, then run both data packs through the same parse ➜ reconcile flow:

```bash
export PROJECT_ID=us-con-gcp-sbx-0001190-100925
export RAW_BUCKET=$PROJECT_ID-ccda-raw
export PARSED_BUCKET=$PROJECT_ID-ccda-parsed
export PARSE_URL=https://<cloud-function-url>
export RECON_URL=https://<cloud-run-url>

# Diabetes example (existing CCDAs copied to the raw bucket)
curl -s -X POST "$PARSE_URL" -H "Content-Type: application/json" \
  -d "{\"gcs_uri\":\"gs://$RAW_BUCKET/16_Endocrinology___Starting_Insulin_Therapy.xml\"}" | tee A.json
curl -s -X POST "$PARSE_URL" -H "Content-Type: application/json" \
  -d "{\"gcs_uri\":\"gs://$RAW_BUCKET/18_Hospital_Discharge_Summary___Post_DKA.xml\"}" | tee B.json
A_JSON=$(jq -r '.parsed_json_gcs' A.json); B_JSON=$(jq -r '.parsed_json_gcs' B.json)
curl -s -X POST "$RECON_URL/reconcile" -H "Content-Type: application/json" \
  -d "{\"a_json_gcs\":\"$A_JSON\",\"b_json_gcs\":\"$B_JSON\"}" | jq .

# Med-safety example
curl -s -X POST "$PARSE_URL" -H "Content-Type: application/json" \
  -d "{\"gcs_uri\":\"gs://$RAW_BUCKET/msc-001_A_Facility.xml\"}" | tee M1.json
curl -s -X POST "$PARSE_URL" -H "Content-Type: application/json" \
  -d "{\"gcs_uri\":\"gs://$RAW_BUCKET/msc-001_B_Facility.xml\"}" | tee M2.json
M1_JSON=$(jq -r '.parsed_json_gcs' M1.json); M2_JSON=$(jq -r '.parsed_json_gcs' M2.json)
curl -s -X POST "$RECON_URL/reconcile" -H "Content-Type: application/json" \
  -d "{\"a_json_gcs\":\"$M1_JSON\",\"b_json_gcs\":\"$M2_JSON\"}" | jq .
```

## Vertex AI Agent Builder wiring

1. Add tools using schemas from `ccr/agent/tools.json`.
2. Paste the instructions from `ccr/agent/system_prompt.txt`.
3. Use the deployed endpoints for invocation.
4. Recommended prompts: "Parse the latest CCDAs and flag med discrepancies" or "Highlight drug interactions and allergy conflicts for this transfer."

A TODO for Vertex AI Search datastore `patient-data_1762901262843` lives in `ccr/agent/README.md` once access is granted.

## Optional UI

`ccr/ui/app.py` provides a Streamlit front-end to upload two CCDAs, invoke the Cloud Function and Cloud Run service, and view the results. Configure `PARSE_FUNCTION_URL` and `RECONCILE_URL` environment variables before running `streamlit run ccr/ui/app.py`.

## Developer checks

To validate the parsers and reconciliation helpers locally:

```bash
cd ccr
python -m venv .venv && source .venv/bin/activate
pip install -r functions/parse_ccda/requirements.txt -r services/reconcile/requirements.txt pytest
pytest
python -m compileall ..
```

The unit tests execute against the synthetic CCDA dataset in `data/diabetes/` and use built-in fallbacks when optional dependencies (FastAPI, Pydantic, pandas, or google-cloud-storage) are unavailable.

## Pre-push checklist

Before publishing updates to `init/ccr-demo`, run the quick checks below to keep the demo branch ready for deployment:

- `pytest -q` – validates parser and reconciliation regressions.
- `python -m compileall ccr` – ensures all modules are syntax-clean for Cloud Functions and Cloud Run builds.
- Review `ccr/infra/deploy.sh` for any environment variable changes that should be reflected in `infra/.env`.
- Confirm new reference data (CSV or prompts) is committed so deployment artifacts remain self-contained.

## Demo dataset and narrative

* Twenty synthetic CCDA files under `data/diabetes/` chronicle a type 2 diabetes journey across 2022–2024.
* The med-safety pack in `data/med-safety-contra/` expands coverage to allergy conflicts and contraindicated combinations validated by the scenario tests.
* Use the updated 3-minute walkthrough in `ccr/README.md` to align the story with the available data when presenting the demo.

## Local workspace quick-reference

Need to double-check you are inside the real repo, discover worktrees, or safely
push to GitHub? Follow [`LOCAL_WORKFLOW.md`](LOCAL_WORKFLOW.md) for:

- Sanity checks (`pwd`, `git rev-parse --show-toplevel`, `git status -sb`).
- Worktree discovery (`git worktree list`) so commands run in the right folder.
- Rescue steps if Codex saved files outside the repo, plus the canonical commit
  / push flow for `feature/unified-med-and-diabetes`.
