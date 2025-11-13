# Med-Safety & Contraindications Pack

This dataset exercises medication safety, contraindication, and allergy workflows that supplement the diabetes longitudinal journey. Each scenario ships with two CCDAs that represent distinct facilities or time points for the same patient so the parse ➜ reconcile pipeline can surface high-risk conditions.

## What this pack covers
- Clinically significant drug–drug interactions (DDIs) such as Warfarin combined with potent antibiotics.
- Allergy conflicts where a recorded intolerance should flag a prescribed or administered medication.
- Duplicate or diverging medication plans that should appear as discrepancies or dose variances during reconciliation.

## Scenario pairings
| Scenario ID | Files | Highlights |
|-------------|-------|------------|
| `msc-001` | `msc-001_A_Facility.xml` vs `msc-001_B_Facility.xml` | Warfarin is co-managed with a new Amoxicillin order that should trigger a moderate DDI warning and a recommendation to monitor INR closely. |
| `msc-002` | `msc-002_A_Facility.xml` vs `msc-002_B_Facility.xml` | Patient carries a Sulfa allergy in A; facility B prescribes Trimethoprim-sulfamethoxazole (TMP-SMX) which should raise an allergy conflict. |
| `msc-003` | `msc-003_A_Facility.xml` vs `msc-003_B_Facility.xml` | Demonstrates duplicate sulfonylurea therapy at different doses to ensure discrepancies capture duplicates/dose variance tags. |

## Expected findings (per scenario)
- **msc-001**
  - `dd_interactions` should include Warfarin + Amoxicillin with severity `moderate`.
  - `tags` should contain `ddi_detected`.
  - `recommendations` (agent side) should mention INR monitoring.
- **msc-002**
  - `allergy_conflicts` should surface Sulfa allergy vs TMP-SMX with `moderate` severity.
  - `tags` should contain `allergy_conflict`.
  - Reconciled allergies should cite the source facility/date for the allergy entry.
- **msc-003**
  - `discrepancies` should include entries noting duplicate sulfonylurea therapy or diverging doses.
  - `tags` should contain `med_discrepancy`.
  - No DDIs or allergy conflicts are expected if medications are otherwise compatible.

> **Note:** Placeholder CCDAs can be swapped for actual HL7 C-CDA files as they become available. Keep manifest entries in sync with the file names uploaded to Cloud Storage.
