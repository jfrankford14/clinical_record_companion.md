

Datasets & Scenarios
- Diabetes: place ~20 CCDA XML files under data/diabetes/ and define scenarios in data/diabetes/manifest.json.
- Medication safety (contraindications): use data/med-safety-contra/manifest.json and upload A_Facility.xml/B_Facility.xml.

Unified run (single build)
- Build once (Dockerfile included) and run tests or scenarios across both datasets.
- Pytest env vars: PROJECT_ID, RAW_BUCKET, PARSED_BUCKET, PARSE_URL, RECON_URL.
- If any are missing, tests in tests/test_scenarios.py xfail gracefully with a reason.

Example
  pytest -q tests/test_scenarios.py
