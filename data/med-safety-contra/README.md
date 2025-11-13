Medication Safety (Contraindications) Dataset

Overview
- Two C-CDA XML files representing facilities A and B for the same patient.
- Intended for discrepancy detection and contraindication checks.

Files to add
- A_Facility.xml
- B_Facility.xml

Usage
- Example commands (from repo root):
  python -m clinical_record_companion discrepancies --records data/med-safety-contra/A_Facility.xml data/med-safety-contra/B_Facility.xml
  python -m clinical_record_companion interactions --records data/med-safety-contra/A_Facility.xml data/med-safety-contra/B_Facility.xml --kb data/reference/MedicationKnowledgeBase.csv
  python -m clinical_record_companion conflicts --records data/med-safety-contra/A_Facility.xml data/med-safety-contra/B_Facility.xml --crosswalk data/reference/AllergyCrosswalk.csv

Provenance
- Synthetic/demo data only. Do not include PHI.