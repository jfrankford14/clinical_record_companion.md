Clinical Record Companion (Local Demo)

Overview
- Parses synthetic C-CDA XML to structured JSON
- Reconciles medications and allergies across facilities
- Detects potential drug–drug interactions from a local CSV knowledge base
- Flags allergy–drug conflicts
- Provides a simple CLI for summaries, discrepancies, interactions, conflicts, and handoff notes

Why local?
- Matches PRD constraints: no external APIs, sandbox-friendly, synthetic data only
- Mirrors the Vertex AI Agent pattern with modular parsing, grounding, reasoning, and an audit trail

Quick Start
1) Ensure Python 3.9+ is available
2) From repo root, run examples:
   - Summarize meds/allergies
     python -m clinical_record_companion summarize --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml
   - Show discrepancies (added/removed/changed)
     python -m clinical_record_companion discrepancies --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml
   - List potential interactions
     python -m clinical_record_companion interactions --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml --kb clinical-record-companion/data/reference/MedicationKnowledgeBase.csv
   - Check allergy conflicts
     python -m clinical_record_companion conflicts --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml --crosswalk clinical-record-companion/data/reference/AllergyCrosswalk.csv
   - Generate handoff summary
     python -m clinical_record_companion handoff --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml --kb clinical-record-companion/data/reference/MedicationKnowledgeBase.csv --crosswalk clinical-record-companion/data/reference/AllergyCrosswalk.csv

Testing
- Run unit tests (Windows PowerShell):
  $env:PYTHONPATH = "clinical-record-companion"; python -m unittest -v


Data
- Synthetic C-CDA pairs sized for demo
- Reference CSVs for interactions and allergy crosswalks
- Provider directory to tag facility provenance

Agent Capabilities (Local Demo)
- Grounding: Each medication/allergy retains facility/source provenance
- Reasoning: Deterministic rules for discrepancies, interactions, and conflicts
- Audit trail: Outputs include which facility/file contributed each item

Limitations
- Simplified C-CDA parser tailored to included samples (no full standard coverage)
- Local rules simulate what a production system would do via Vertex AI + Document AI

Files of interest
- src entry: clinical_record_companion/agent_cli.py
- parser: clinical_record_companion/ccda_parser.py
- reasoning: clinical_record_companion/insights.py
- reference loaders: clinical_record_companion/knowledge_base.py
- synthetic data: clinical-record-companion/data/synthetic/
- reference data: clinical-record-companion/data/reference/

GCP Import Options
- Cloud Shell or Vertex AI Workbench
  - git clone this repo and run the Quick Start commands from the repo root.
  - Artifacts are written to clinical-record-companion/exports/.
- Cloud Run (containerized)
  - Build: docker build -t cr-companion:demo .
  - Run locally: docker run --rm -it -v %cd%:/work -w /work cr-companion:demo python -m clinical_record_companion export --records clinical-record-companion/data/synthetic/record_a.xml clinical-record-companion/data/synthetic/record_b.xml --kb clinical-record-companion/data/reference/MedicationKnowledgeBase.csv --crosswalk clinical-record-companion/data/reference/AllergyCrosswalk.csv --out clinical-record-companion/exports
  - Push to Artifact Registry and deploy a job or service if desired.
- Vertex AI Search (grounding)
  - Use clinical-record-companion/exports/search_docs.ndjson as a seed corpus for a Data Store.
  - Each line is one document with a section and text payload suitable for quick demos.

Repo Hygiene
- .gitignore prevents committing local exports and caches.
- requirements.txt is intentionally minimal (stdlib only).
- GitHub Actions CI runs unit tests on pushes and PRs.
