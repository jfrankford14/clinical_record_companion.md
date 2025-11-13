# CCDA Documents for Polypharmacy Patient with Drug Interactions

## Overview
This collection contains 20 CCDA (Consolidated Clinical Document Architecture) XML documents representing a 1-year journey of an elderly patient experiencing cascading medication-related adverse events due to drug-drug interactions, contraindications, and polypharmacy complications.

## Patient Information
- **Name:** Margaret "Maggie" Ann O'Brien
- **Date of Birth:** March 15, 1952 (72 years old)
- **Gender:** Female
- **Race/Ethnicity:** White, Not Hispanic or Latino
- **Timeline:** March 2023 - March 2024 (365 days)
- **Primary Diagnoses:** Atrial Fibrillation, Coronary Artery Disease, Hypertension, Osteoarthritis, Depression, Chronic Kidney Disease Stage 3-4

## Clinical Narrative - Cascade of Medication Complications

This case illustrates the **"prescribing cascade"** phenomenon where adverse drug reactions are misinterpreted as new medical conditions, leading to additional medications, which cause further adverse effects. It demonstrates real-world challenges of polypharmacy in elderly patients with multiple comorbidities.

## Document Timeline & Medication Disasters

### Phase 1: Baseline Stability (Documents 1-2) - Days 0-7

**1. Primary Care - Annual Wellness Visit** (03/01/2023)
- **Baseline Medications (5):**
  - Warfarin 5mg daily (for AFib)
  - Metoprolol 50mg BID (for AFib rate control)
  - Lisinopril 10mg daily (for hypertension)
  - Sertraline 50mg daily (for depression)
  - Acetaminophen PRN (for arthritis pain)
- **Status:** Stable, therapeutic INR, well-controlled conditions

**2. Lab - Baseline INR and Renal Panel** (03/08/2023)
- INR: 2.4 (therapeutic for AFib)
- Creatinine: 1.3, eGFR: 52 (Stage 3A CKD)
- All baseline labs stable

### Phase 2: First Cascade - NSAID + Warfarin (Documents 3-5) - Days 35-52

**TRIGGER EVENT #1: Ibuprofen Prescribed Despite Warfarin**

**3. Urgent Care - Worsening Knee Pain** (04/05/2023)
- Patient prescribed **ibuprofen 600mg TID** for arthritis pain
- **CONTRAINDICATION:** NSAIDs + warfarin = significantly increased GI bleeding risk
  - NSAIDs inhibit platelet function
  - NSAIDs cause gastric erosions
  - NSAIDs increase warfarin levels via protein binding displacement
- **Risk Score:** HAS-BLED increased from 2 to 4 (HIGH bleeding risk)

**4. Emergency Department - GI Bleeding** (04/19/2023)
- **PREDICTABLE CONSEQUENCE:** Upper GI hemorrhage
  - Hemoglobin dropped from 12.5 → 8.2 g/dL
  - INR 4.8 (supratherapeutic due to NSAID interaction)
  - Melena, hypotension, tachycardia
  - EGD showed gastric erosions and duodenal ulcer
- **Treatment:** ICU admission, blood transfusion, vitamin K, warfarin held
- **Medications Changed:**
  - Ibuprofen **DISCONTINUED**
  - Warfarin dose **REDUCED**
  - Omeprazole 40mg **ADDED** (PPI for ulcer healing)

**5. Hospital Discharge - Post GI Bleed** (04/22/2023)
- Warfarin restarted at 2.5mg (reduced dose)
- Omeprazole 40mg for gastroprotection
- Ferrous sulfate added for anemia

### Phase 3: Second Cascade - PPI + Clopidogrel (Documents 6-8) - Days 70-100

**TRIGGER EVENT #2: Cardiac Event Requires Clopidogrel, But Patient on PPI**

**6. Cardiology - AFib Management Post-Bleed** (05/10/2023)
- Review of old records reveals CAD with prior stent (2018)
- **Aspirin 81mg added** for cardioprotection
- Patient now on **dual antithrombotic therapy** (warfarin + aspirin)
- Continue omeprazole for GI protection

**7. Emergency Department - Chest Pain, NSTEMI** (06/04/2023)
- **NSTEMI** (troponin 0.82 ng/mL)
- EKG shows ST depressions
- **NEW CRITICAL INTERACTION:**
  - Patient needs **clopidogrel 75mg** (dual antiplatelet therapy post-stent)
  - Now on **TRIPLE antithrombotic therapy** (warfarin + aspirin + clopidogrel)
  - **BUT:** Patient on omeprazole 40mg which **reduces clopidogrel effectiveness by ~50%**
  - Mechanism: Omeprazole inhibits CYP2C19, preventing conversion of clopidogrel to active metabolite
- **Medications:** Aspirin increased to 325mg, clopidogrel 300mg load → 75mg daily

**8. Cardiology Discharge - Triple Therapy Issues** (06/09/2023)
- Cardiac catheterization: Drug-eluting stent placed in LAD
- **CRITICAL MEDICATION CHANGE:** Omeprazole **SWITCHED to pantoprazole 40mg**
  - Pantoprazole has minimal CYP2C19 interaction with clopidogrel
- **Problem:** Patient on triple antithrombotic therapy (very high bleeding risk)
- Atorvastatin 80mg **ADDED** for post-MI management
- Metoprolol formulation changed to succinate ER

### Phase 4: Third Cascade - Statin + Diltiazem (Documents 9-11) - Days 125-133

**TRIGGER EVENT #3: Multiple Drug Interactions Cause Rhabdomyolysis**

**9. Primary Care - Muscle Pain and Weakness** (07/04/2023)
- Patient reports severe muscle pain, weakness
- **Diltiazem 120mg added** for additional AFib rate control
- **DANGEROUS INTERACTION:** Atorvastatin 80mg + Diltiazem
  - Diltiazem inhibits CYP3A4, increasing atorvastatin levels 3-4 fold
  - Additional risk factors: CKD (reduced clearance), sertraline (may increase myopathy risk)
- Labs: CK 2,800 U/L (critically elevated)
- Creatinine 1.8 (worsening)

**10. Emergency Department - Rhabdomyolysis, AKI** (07/06/2023)
- **SEVERE RHABDOMYOLYSIS:** CK 18,500 U/L
- **Acute Kidney Injury:** Creatinine 2.8 mg/dL (from baseline 1.3)
- Myoglobinuria, hyperkalemia (5.8)
- **Medications Changed:**
  - Atorvastatin **DISCONTINUED**
  - Diltiazem **DISCONTINUED**
  - Lisinopril **HELD** (due to AKI)
  - Warfarin dose **REDUCED** (INR 3.5)
- Treatment: Aggressive IV hydration, nephrology consult

**11. Hospital Discharge - Recovered from Rhabdomyolysis** (07/12/2023)
- CK improved to 450, creatinine 1.9 (partial recovery)
- **eGFR now 32** (progressed to Stage 3B CKD)
- **Safer alternatives started:**
  - Rosuvastatin 10mg (lower myopathy risk than atorvastatin)
  - Metoprolol dose increased for rate control (instead of diltiazem)
- Aspirin **DISCONTINUED** (reduce triple therapy to dual: warfarin + clopidogrel)
- **Medication count: 8 drugs**

### Phase 5: Fourth Cascade - SSRI + Anticoagulants (Documents 12-13) - Days 160-195

**TRIGGER EVENT #4: SSRI Increases Bleeding Risk**

**12. Psychiatry - Depression Management** (08/08/2023)
- Patient reports worsening depression, easy bruising
- **SSRI-Anticoagulant Interaction:**
  - Sertraline inhibits platelet function (serotonin in platelets)
  - Sertraline inhibits CYP2C9, increasing warfarin levels
  - Combined with warfarin + clopidogrel = VERY HIGH bleeding risk
- **Medication Change:** Sertraline **SWITCHED to mirtazapine 15mg**
  - Mirtazapine has no antiplatelet effect
  - Also helps with sleep and appetite

**13. Primary Care - Weight Gain, Uncontrolled BP** (09/12/2023)
- **MIRTAZAPINE ADVERSE EFFECT:** 6kg weight gain in 6 weeks
- Blood pressure elevated: 168/98 (was 135/80)
- **Cascading problems:**
  - Weight gain worsens hypertension
  - Weight gain increases cardiac risk post-MI
  - Can't use diltiazem (caused rhabdomyolysis)
  - Limited antihypertensive options with CKD
- **Amlodipine 5mg ADDED** for BP control
- Creatinine now 2.1, **eGFR 28 (Stage 4 CKD)**
- Anemia of CKD developing (Hgb 9.8)
- **Medication count: 8-9 drugs with multiple PRN meds**

### Phase 6: Polypharmacy Crisis (Documents 14-16) - Days 220-250

**TRIGGER EVENT #5: Medication Confusion and Falls**

**14. Geriatrics Consultation - Polypharmacy Review** (10/07/2023)
- **BEERS Criteria violations:**
  - Multiple CNS-active medications
  - Anticoagulation in elderly with CKD and prior bleeding
  - High anticholinergic burden
- **Cognitive screening:** MoCA 22/30 (mild impairment)
- Patient confused about medication changes
- Taking "old pills" found at home (medication errors)
- **Fall risk:** Elevated (orthostatic hypotension from metoprolol, cognitive impairment)
- **Current medication count: 9 active prescriptions**

**15. Emergency Department - Fall with Head Injury** (11/01/2023)
- Patient fell at home, struck head
- **SUBDURAL HEMATOMA** (2cm on CT)
- INR 2.9 on warfarin + clopidogrel
- **CRITICAL SITUATION:**
  - High-risk AFib (CHADSVASc 5) needs anticoagulation for stroke prevention
  - Recent MI with stent needs antiplatelet for clot prevention
  - BUT: Intracranial hemorrhage while on anticoagulation
  - Recurrent falls = high risk for repeat bleeding
- **Emergency intervention:** Warfarin and clopidogrel **HELD**, vitamin K + PCC given
- ICU admission for neuro monitoring

**16. Palliative Care - Goals of Care Discussion** (11/06/2023)
- Family meeting with multidisciplinary team
- **Patient's goals:** Quality of life over longevity
- **Decisions made:**
  - **DEPRESCRIBING:** Warfarin and clopidogrel permanently discontinued
  - Accept increased stroke risk per patient preference
  - **Medication simplification** - reduced to 6 essential medications
  - Home health services, fall prevention
  - **Advance directives:** DNR/DNI status
  - Declines dialysis planning
- **Final medication list (simplified):**
  - Metoprolol 100mg daily (reduced dose)
  - Lisinopril 5mg daily
  - Amlodipine 5mg daily
  - Pantoprazole 20mg daily (reduced)
  - Mirtazapine 7.5mg at bedtime (reduced)
  - Acetaminophen PRN

### Phase 7: Consequences of Medication Changes (Documents 17-20) - Days 280-365

**17. Primary Care - Follow-up After Deprescribing** (12/26/2023)
- Patient reports **feeling "much better"** with fewer medications
- Lost 2kg (less mirtazapine)
- No medication confusion
- No falls since discharge
- BP better controlled
- **BUT:** No anticoagulation for high-risk AFib
- Subdural hematoma stable on imaging
- CKD stable (Cr 2.2, eGFR 29)

**18. Cardiology - AFib and CAD Management Without Anticoagulation** (01/25/2024)
- **High stroke risk:** CHADSVASc 5 = 6.7% annual stroke risk
- **Off all anticoagulation and antiplatelet agents**
- 7 months post-stent (typically needs 12 months dual antiplatelet)
- Discussed Left Atrial Appendage Closure device - patient declines
- Patient understands and accepts stroke risk
- Echo stable, AFib rate-controlled

**19. Emergency Department - Transient Ischemic Attack** (02/24/2024)
- **PREDICTABLE CONSEQUENCE:** TIA (20 minutes right-sided weakness, slurred speech)
- Multiple old lacunar infarcts on MRI
- No anticoagulation for 3 months
- **DIFFICULT DECISION:** Restart anticoagulation despite bleeding history?
- After extensive discussion, patient agrees to trial of:
  - **Apixaban 2.5mg BID** (DOAC with dose reduction for age/weight/CKD)
  - Safer than warfarin (no INR monitoring, less drug interactions, lower ICH risk)
- **Medication count back up to 7**

**20. Comprehensive Medication Reconciliation - One Year Summary** (03/01/2024)
- **Annual review** - 12 months of medication-related complications
- **Final medication regimen (7 drugs):**
  1. Apixaban 2.5mg BID (anticoagulation)
  2. Metoprolol 100mg daily (rate control)
  3. Lisinopril 5mg daily (BP)
  4. Amlodipine 5mg daily (BP)
  5. Pantoprazole 20mg daily (GI protection)
  6. Mirtazapine 7.5mg bedtime (depression)
  7. Acetaminophen PRN (pain)
- **Conditions:** AFib, CAD, HTN, OA, Depression, CKD Stage 4, Anemia
- **Advance directives:** DNR/DNI, no dialysis
- Focus on quality of life and symptom management

## Summary of Drug-Drug Interactions and Contraindications

### 1. **NSAID + Warfarin → GI Bleeding**
- **Interaction:** Ibuprofen contraindicated with warfarin
- **Mechanisms:**
  - NSAIDs inhibit platelet aggregation
  - NSAIDs cause gastric mucosal damage
  - NSAIDs displace warfarin from protein binding (increases free warfarin)
- **Consequence:** Life-threatening upper GI hemorrhage
- **Prevention:** Use acetaminophen or topical NSAIDs for arthritis pain in patients on anticoagulants

### 2. **PPI (Omeprazole) + Clopidogrel → Reduced Antiplatelet Effect**
- **Interaction:** Omeprazole reduces clopidogrel efficacy by ~50%
- **Mechanism:** Omeprazole inhibits CYP2C19 enzyme needed to convert clopidogrel prodrug to active metabolite
- **Consequence:** Increased risk of stent thrombosis, MI, stroke
- **Solution:** Switch to pantoprazole (minimal CYP2C19 interaction) or use H2 blocker

### 3. **Statin (Atorvastatin) + CYP3A4 Inhibitor (Diltiazem) → Rhabdomyolysis**
- **Interaction:** Diltiazem increases atorvastatin levels 3-4 fold
- **Mechanism:** Diltiazem inhibits CYP3A4, reducing statin metabolism
- **Additional risk factors:** CKD (reduced clearance), age, other medications
- **Consequence:** Severe rhabdomyolysis with CK >18,000, acute kidney injury
- **Prevention:** Use rosuvastatin or pravastatin (not metabolized by CYP3A4) with diltiazem, or use different rate control agent

### 4. **SSRI (Sertraline) + Warfarin + Clopidogrel → Increased Bleeding**
- **Interaction:** Triple whammy for bleeding risk
- **Mechanisms:**
  - Sertraline depletes serotonin in platelets (impairs platelet function)
  - Sertraline inhibits CYP2C9 (increases warfarin levels)
  - Combined with warfarin + clopidogrel = extreme bleeding risk
- **Consequence:** Easy bruising, increased risk of major bleeding
- **Solution:** Switch to mirtazapine (no antiplatelet effect)

### 5. **Mirtazapine → Weight Gain → Worsening Hypertension**
- **Adverse Effect:** Significant weight gain (appetite stimulation)
- **Consequence:** Weight gain worsens BP control, increases cardiac risk
- **Management Challenge:** Need additional antihypertensive (amlodipine) which adds to polypharmacy

### 6. **Polypharmacy + Cognitive Decline → Medication Errors → Falls**
- **Interaction:** Complexity of regimen exceeds patient's cognitive capacity
- **Consequences:**
  - Taking wrong medications
  - Taking discontinued medications
  - Falls (multifactorial: orthostatic hypotension from metoprolol, CNS effects)
  - Subdural hematoma while on anticoagulation

### 7. **Anticoagulation (Warfarin/Clopidogrel) + Falls → Intracranial Hemorrhage**
- **Interaction:** High bleeding risk (HAS-BLED 5) + mechanical trauma
- **Consequence:** Subdural hematoma requiring anticoagulation reversal
- **Dilemma:** High stroke risk without anticoagulation vs high bleeding risk with anticoagulation

### 8. **Stopping Anticoagulation (Warfarin) + High Stroke Risk → TIA**
- **Risk:** CHADSVASc 5 = 6.7% annual stroke risk
- **Consequence:** TIA within 3 months of stopping anticoagulation
- **Resolution:** Restart anticoagulation with safer DOAC (apixaban)

## Medication Count Progression

| Timepoint | Active Medications | Peak Daily Pills | Major Complexity |
|-----------|-------------------|------------------|------------------|
| Baseline (Day 0) | 5 | 7 | Warfarin monitoring |
| Post-GI Bleed (Day 52) | 7 | 10 | INR + iron |
| Post-MI Triple Therapy (Day 100) | 9 | 13 | Warfarin + 2 antiplatelet |
| Post-Rhabdo Peak (Day 125) | 10 | 14 | CKD dosing |
| After Deprescribing (Day 250) | 6 | 7 | Simplified |
| Final (Day 365) | 7 | 9 | DOAC (easier) |

## Risk Scores Throughout Journey

### HAS-BLED Score (Bleeding Risk on Anticoagulation)
- **Baseline:** 2 (moderate risk)
  - Age >65 (+1)
  - Labile INR (+1)
- **After NSAID:** 4 (high risk)
  - Added: Prior bleed (+1), NSAID use (+1)
- **Triple Therapy:** 5 (very high risk)
  - Added: Abnormal renal function (+1)
- **Post-Subdural Hematoma:** 6 (extreme risk)
  - Added: Prior stroke/ICH (+1)

### CHADSVASc Score (Stroke Risk in AFib)
- **Throughout:** 5 (high risk = 6.7% annual stroke risk)
  - CHF/LV dysfunction (+1)
  - Hypertension (+1)
  - Age 65-74 (+1)
  - Diabetes (0)
  - Stroke/TIA (+2 after Day 340)
  - Vascular disease (+1 for CAD)
  - Female sex (+1)

## Prescribing Cascade Illustration

```
Initial Condition: Arthritis Pain
    ↓
Ibuprofen prescribed (contraindicated with warfarin)
    ↓
GI Bleeding → Omeprazole added
    ↓
MI (partly due to omeprazole-clopidogrel interaction?)
    ↓
Atorvastatin 80mg + Clopidogrel + Aspirin added
    ↓
Diltiazem added for rate control
    ↓
Rhabdomyolysis (atorvastatin-diltiazem interaction)
    ↓
Acute Kidney Injury → Multiple medication adjustments
    ↓
Sertraline + anticoagulants → Increased bleeding risk
    ↓
Switch to Mirtazapine
    ↓
Weight gain from mirtazapine → Worsening hypertension
    ↓
Amlodipine added
    ↓
Polypharmacy (10 medications) → Confusion → Medication errors
    ↓
Fall → Subdural hematoma (on anticoagulation)
    ↓
Stop anticoagulation
    ↓
TIA (stroke risk from AFib)
    ↓
Restart anticoagulation (apixaban)
```

## Key Clinical Lessons

### 1. **Beware the Prescribing Cascade**
- Treating side effects with new medications can create endless loop
- Always ask: "Is this a new condition or a drug side effect?"

### 2. **Know Major Drug Interactions**
- **NSAIDs + anticoagulants** = GI bleeding
- **PPIs + clopidogrel** = reduced efficacy
- **Statins + CYP3A4 inhibitors** = myopathy/rhabdomyolysis
- **SSRIs + anticoagulants** = increased bleeding

### 3. **Polypharmacy in Elderly**
- Each additional medication increases:
  - Adverse drug events
  - Drug interactions
  - Medication errors
  - Falls
  - Cognitive burden
- **Deprescribing is as important as prescribing**

### 4. **Risk vs Benefit with Anticoagulation**
- Not all patients benefit equally
- Must consider:
  - Stroke risk (CHADSVASc)
  - Bleeding risk (HAS-BLED)
  - Fall risk
  - Cognitive status
  - Patient preferences
  - Quality of life

### 5. **Medication Reconciliation is Critical**
- At every transition of care
- After every new prescription
- Especially in elderly patients
- Involve pharmacists

### 6. **DOACs May Be Safer Than Warfarin in Elderly**
- Less drug-food interactions
- No INR monitoring (less complexity)
- Lower intracranial hemorrhage risk
- **BUT:** Requires dose adjustment for renal function
- **AND:** More expensive

### 7. **Goals of Care Discussions**
- Essential in complex elderly patients
- May choose symptom management over disease-directed therapy
- Deprescribing can improve quality of life

## CCDA Format Specifications

All documents conform to:
- **Standard:** HL7 CDA R2 (CCDA 2.1)
- **Encoding:** UTF-8 XML
- **Template version:** 2015-08-01 extension

### Code Systems Used:
- **LOINC** (2.16.840.1.113883.6.1) - Document types, lab tests
- **SNOMED-CT** (2.16.840.1.113883.6.96) - Clinical terms, diagnoses
- **RxNorm** (2.16.840.1.113883.6.88) - Medications
- **CDC Race/Ethnicity** (2.16.840.1.113883.6.238) - Demographics

### Key Sections:
- Allergies and Adverse Reactions (2.16.840.1.113883.10.20.22.2.6.1)
- Problem List (2.16.840.1.113883.10.20.22.2.5.1)
- Medications (2.16.840.1.113883.10.20.22.2.1.1)
- Laboratory Results (2.16.840.1.113883.10.20.22.2.3.1)
- Vital Signs (2.16.840.1.113883.10.20.22.2.4.1)
- Assessment and Plan (2.16.840.1.113883.10.20.22.2.9)

## Use Cases

These documents are valuable for:

1. **Clinical Decision Support Systems**
   - Training AI to detect drug-drug interactions
   - Identifying prescribing cascades
   - Flagging contraindications

2. **Medication Safety Research**
   - Studying patterns of adverse drug events
   - Analyzing polypharmacy complications
   - Evaluating deprescribing interventions

3. **Medical Education**
   - Teaching pharmacotherapy principles
   - Illustrating real-world medication management challenges
   - Training in geriatric medicine

4. **Quality Improvement**
   - Developing medication reconciliation protocols
   - Implementing BEERS Criteria checks
   - Creating anticoagulation management pathways

5. **EHR System Testing**
   - Testing drug interaction alerts
   - Validating medication reconciliation modules
   - Evaluating clinical decision support tools

6. **Health Information Exchange**
   - Testing CCDA import/export functionality
   - Validating medication list reconciliation across systems
   - Ensuring adverse reaction documentation

## Healthcare Settings Represented

The 20 documents span multiple care settings:
- **Primary Care:** 4 visits (annual wellness, follow-ups, medication reviews)
- **Emergency Department:** 5 visits (GI bleed, MI, rhabdomyolysis, fall/ICH, TIA)
- **Hospital Inpatient:** 3 admissions (GI bleed, rhabdomyolysis, subdural hematoma)
- **Cardiology:** 3 consultations (AFib management, post-MI care, reassessment)
- **Laboratory:** 1 standalone report (baseline labs)
- **Urgent Care:** 1 visit (knee pain - inappropriate NSAID prescription)
- **Geriatrics:** 1 consultation (polypharmacy review)
- **Psychiatry:** 1 consultation (depression management, SSRI interaction)
- **Palliative Care:** 1 consultation (goals of care, deprescribing)

## Major Medications Featured

### Anticoagulants/Antiplatelets:
- Warfarin (vitamin K antagonist)
- Clopidogrel (P2Y12 inhibitor)
- Aspirin (antiplatelet)
- Apixaban (DOAC/Factor Xa inhibitor)

### Cardiovascular:
- Metoprolol (beta blocker)
- Diltiazem (calcium channel blocker - DISCONTINUED due to interaction)
- Lisinopril (ACE inhibitor)
- Amlodipine (calcium channel blocker)

### Lipid-Lowering:
- Atorvastatin 80mg (DISCONTINUED due to rhabdomyolysis)
- Rosuvastatin 10mg (safer alternative)

### GI Protection:
- Omeprazole (SWITCHED due to clopidogrel interaction)
- Pantoprazole (safer PPI alternative)

### Psychiatric:
- Sertraline (SSRI - DISCONTINUED due to bleeding risk)
- Mirtazapine (tetracyclic antidepressant - alternative)

### Pain Management:
- Ibuprofen (NSAID - DISCONTINUED due to GI bleeding)
- Acetaminophen (safer alternative for elderly)

## Technical Notes

- All OIDs (Object Identifiers) follow HL7 standards
- Document IDs: CON001-CON020
- Timestamps: HL7 format (YYYYMMDDHHMMSS-TTTT)
- RxNorm codes: Valid for all medications
- SNOMED-CT codes: Valid for all diagnoses
- LOINC codes: Valid for all labs and document types
- Medication status tracked (Active, Discontinued, Suspended)

## Generation Information

- **Generated:** November 10, 2025
- **Generator:** Python script with CCDA 2.1 templates
- **Base Date:** March 1, 2023
- **Duration:** 365 days (1 year)
- **Format:** CCDA 2.1 (2015-08-01 templates)

---

*These are synthetic documents created for testing, education, and clinical decision support development. All patient information is fictional. The clinical scenarios are based on real-world patterns of medication-related adverse events in elderly patients with polypharmacy.*
