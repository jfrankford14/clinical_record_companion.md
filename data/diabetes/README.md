Diabetes CCDA Dataset

Overview
- Contains ~20 C-CDA XML files representing encounters across facilities for a diabetes-focused cohort.
- Used to test parsing, unification, and downstream safety checks.

Expected Format
- File type: XML (C-CDA)
- Encoding: UTF-8
- Suggested names: diabetes_01.xml .. diabetes_20.xml (or source-based names)

Usage
- Example commands (from repo root):
  python -m clinical_record_companion summarize --records data/diabetes/diabetes_01.xml data/diabetes/diabetes_02.xml
  python -m clinical_record_companion export --records data/diabetes/diabetes_01.xml data/diabetes/diabetes_02.xml --kb data/reference/MedicationKnowledgeBase.csv --crosswalk data/reference/AllergyCrosswalk.csv --out exports

Provenance
- Synthetic/demo data only. Do not include PHI.