# CCDA Documents for Diabetes Patient Journey

## Overview
This collection contains 20 CCDA (Consolidated Clinical Document Architecture) XML documents representing a 3-year progressive journey of a diabetes patient from well-controlled to poorly controlled disease with complications.

## Patient Information
- **Name:** John Michael Martinez
- **Date of Birth:** August 20, 1967 (55 years old at diagnosis)
- **Gender:** Male
- **Race/Ethnicity:** Hispanic/Latino (Mexican)
- **Diagnosis:** Type 2 Diabetes Mellitus
- **Timeline:** January 2022 - November 2024 (36 months)

## Document Timeline

### Year 1: Well-Controlled Phase (Documents 1-6)
HbA1c progression: 6.8% → 6.5%

1. **01_PrimaryCare_Initial_Diagnosis.xml** (01/15/2022)
   - Source: Chicago Family Medicine Clinic
   - Initial diabetes diagnosis
   - Started Metformin 500mg BID, Lisinopril 10mg daily
   - HbA1c: Not yet measured, Glucose: Elevated
   - BP: 148/92, Weight: 95kg, BMI: 31

2. **02_LabFacility_Initial_HbA1c.xml** (01/18/2022)
   - Source: Quest Diagnostics - Chicago North
   - First comprehensive metabolic panel
   - HbA1c: 6.8%, Glucose: 138 mg/dL
   - Lipid panel: Total Chol 225, LDL 145, HDL 42, Trig 190
   - Kidney function: Normal (Creatinine 1.0, eGFR 92)

3. **03_Endocrinology_Consultation___Initial_Specialist_Visit.xml** (02/14/2022)
   - Source: Illinois Diabetes & Endocrine Center
   - First endocrinology consultation
   - Diabetes education provided
   - Continue current medications

4. **04_Primary_Care___3_Month_Follow_up_Visit.xml** (04/15/2022)
   - Source: Chicago Family Medicine Clinic
   - Good response to treatment
   - Weight: 93kg (lost 2kg), BMI: 30.4
   - BP improved: 138/85, Glucose: 118 mg/dL

5. **05_Laboratory_Report___6_Month_Labs.xml** (07/13/2022)
   - Source: Quest Diagnostics
   - Excellent control achieved
   - **HbA1c: 6.5%** (best control)
   - Weight: 92kg, Glucose: 110 mg/dL

6. **06_Ophthalmology___Diabetic_Eye_Screening.xml** (08/13/2022)
   - Source: Chicago Eye Institute
   - First diabetic retinopathy screening
   - **Result: No retinopathy detected**
   - Recommend annual screening

### Year 2: Moderate Decline Phase (Documents 7-13)
HbA1c progression: 7.4% → 8.1%

7. **07_Primary_Care___9_Month_Visit,_Weight_Gain_Noted.xml** (10/11/2022)
   - Source: Chicago Family Medicine Clinic
   - Weight regain noted: 98kg, BMI: 32.0
   - BP rising: 145/90, Glucose: 145 mg/dL
   - Dietary counseling provided

8. **08_Laboratory_Report___12_Month_Labs,_HbA1c_Rising.xml** (01/15/2023)
   - Source: Quest Diagnostics
   - Control worsening
   - **HbA1c: 7.4%** (rising from 6.5%)
   - Lipids worsening, new diagnosis: Hyperlipidemia
   - Kidney function declining: eGFR 88

9. **09_Endocrinology___Medication_Adjustment_Visit.xml** (02/09/2023)
   - Source: Illinois Diabetes & Endocrine Center
   - **Medication escalation:**
     - Metformin increased to 1000mg BID
     - Added Glipizide 5mg daily
     - Lisinopril increased to 20mg daily
     - Added Atorvastatin 20mg daily

10. **10_Primary_Care___15_Month_Medication_Titration.xml** (04/10/2023)
    - Source: Chicago Family Medicine Clinic
    - Adjusting to new medications
    - Weight: 99kg, Glucose: 148 mg/dL
    - BP improved: 140/86

11. **11_Laboratory_Report___18_Month_Labs,_Further_Increase.xml** (07/14/2023)
    - Source: LabCorp Chicago
    - Continued deterioration
    - **HbA1c: 8.1%** (further rise)
    - Weight: 100kg, BMI: 32.7
    - Kidney: CKD Stage 2 (eGFR 82)

12. **12_Cardiology_Consultation___Hypertension_Management.xml** (08/10/2023)
    - Source: Northwestern Heart Center
    - Hypertension not well controlled
    - ECG: Normal sinus rhythm
    - Added Amlodipine 5mg daily

13. **13_Podiatry___First_Foot_Exam,_Mild_Neuropathy.xml** (09/09/2023)
    - Source: Chicago Foot & Ankle Specialists
    - Monofilament testing: Decreased sensation
    - **New diagnosis: Peripheral neuropathy**
    - Foot care education provided

### Year 3: Poor Control with Complications (Documents 14-20)
HbA1c progression: 9.2% → 8.5%

14. **14_Emergency_Department___Hypoglycemic_Episode.xml** (10/29/2023)
    - Source: Northwestern Memorial Hospital - ED
    - **Hypoglycemic episode:** Glucose 42 mg/dL
    - Confusion, diaphoresis, tremors
    - Treated with D50, symptoms resolved
    - Medication non-compliance discussed

15. **15_Laboratory_Report___24_Month_Labs,_Poor_Control.xml** (01/15/2024)
    - Source: Quest Diagnostics
    - Severe hyperglycemia
    - **HbA1c: 9.2%** (worst control)
    - Glucose: 245 mg/dL, Weight: 102kg
    - CKD Stage 2: eGFR 68
    - **Microalbuminuria:** 85 mg

16. **16_Endocrinology___Starting_Insulin_Therapy.xml** (02/04/2024)
    - Source: Illinois Diabetes & Endocrine Center
    - **Insulin initiated:**
     - Insulin Glargine 20 Units daily (basal)
     - Insulin Lispro with meals (bolus)
     - Discontinued Glipizide
    - Intensive diabetes education

17. **17_Hospital_Admission___Diabetic_Ketoacidosis_(DKA).xml** (03/25/2024)
    - Source: Northwestern Memorial Hospital
    - **DKA admission to ICU**
    - Glucose: 485 mg/dL, pH: 7.21, elevated ketones
    - Nausea, vomiting, altered mental status
    - Treated with IV fluids and insulin drip

18. **18_Hospital_Discharge_Summary___Post_DKA.xml** (03/30/2024)
    - Source: Northwestern Memorial Hospital
    - 5-day hospitalization
    - Transitioned to subcutaneous insulin
    - Insulin Glargine increased to 30 Units
    - Insulin Lispro: 8-12 Units with meals
    - Extensive diabetes self-management education

19. **19_Ophthalmology___Diabetic_Retinopathy_Detected.xml** (06/13/2024)
    - Source: Chicago Eye Institute
    - Fundoscopy + OCT performed
    - **New diagnosis: Mild nonproliferative diabetic retinopathy**
    - Microaneurysms and dot-blot hemorrhages
    - No macular edema (yet)
    - Plan: Monitor every 3-4 months

20. **20_Primary_Care___Complex_Care_Coordination.xml** (08/22/2024)
    - Source: Chicago Family Medicine Clinic
    - Complex multi-specialty coordination
    - HbA1c: 8.5% (improved from 9.2% but still poor)
    - Weight: 99kg, Glucose: 195 mg/dL
    - **Multiple specialists:** Endocrine, Cardiology, Ophthalmology, Podiatry, Nephrology
    - Added Aspirin 81mg for cardiovascular protection
    - Social work referral for adherence support

## Healthcare Sources Represented
The 20 documents represent various healthcare settings:
- **Primary Care:** 5 visits (Chicago Family Medicine Clinic)
- **Endocrinology:** 3 visits (Illinois Diabetes & Endocrine Center)
- **Laboratory:** 4 reports (Quest Diagnostics, LabCorp)
- **Ophthalmology:** 2 visits (Chicago Eye Institute)
- **Cardiology:** 1 visit (Northwestern Heart Center)
- **Podiatry:** 1 visit (Chicago Foot & Ankle Specialists)
- **Emergency Department:** 1 visit (Northwestern Memorial Hospital ED)
- **Hospital Inpatient:** 2 documents (Admission + Discharge for DKA)

## EHR Vendor Variety
Documents follow different vendor templates simulating real-world health information exchange:
- Quest Diagnostics (Lab system)
- LabCorp (Lab system)
- Various Epic/Cerner-style ambulatory templates
- Hospital inpatient documentation
- Emergency department documentation
- Specialty clinic notes

## Clinical Progression Summary

### Problems/Diagnoses
**Initial (Month 1):**
- Diabetes Mellitus Type 2
- Essential Hypertension
- Obesity

**Added during journey:**
- Hyperlipidemia (Month 12)
- Peripheral Neuropathy (Month 20)
- Chronic Kidney Disease Stage 2 (Month 24)
- History of Hypoglycemia (Month 22)
- History of Diabetic Ketoacidosis (Month 26)
- Diabetic Retinopathy (Month 29)

### Medication Evolution
**Phase 1 (Months 1-12):**
- Metformin 500mg BID
- Lisinopril 10mg daily

**Phase 2 (Months 12-24):**
- Metformin 1000mg BID (increased)
- Glipizide 5-10mg daily (added, then increased)
- Lisinopril 20mg daily (increased)
- Amlodipine 5-10mg daily (added)
- Atorvastatin 20-40mg daily (added, then increased)

**Phase 3 (Months 24-36):**
- Metformin 1000mg BID
- Insulin Glargine 20-35 Units daily (added, progressively increased)
- Insulin Lispro 8-15 Units with meals (added)
- Lisinopril 20mg daily
- Amlodipine 10mg daily
- Atorvastatin 40mg daily
- Aspirin 81mg daily (added)

### Lab Value Trends
| Timepoint | HbA1c | Glucose (mg/dL) | Weight (kg) | BMI | Creatinine | eGFR |
|-----------|-------|-----------------|-------------|-----|------------|------|
| Month 0.2 | 6.8%  | 138             | 95          | 31.0| 1.0        | 92   |
| Month 6   | 6.5%  | 110             | 92          | 30.0| 1.0        | 92   |
| Month 12  | 7.4%  | 155             | 98          | 32.0| 1.1        | 88   |
| Month 18  | 8.1%  | 172             | 100         | 32.7| 1.2        | 82   |
| Month 24  | 9.2%  | 245             | 102         | 33.3| 1.4        | 68   |
| Month 36  | 8.5%  | 195             | 99          | 32.3| -          | -    |

## CCDA Format Specifications
All documents conform to:
- **Standard:** HL7 CDA R2 (CCDA 2.1)
- **Encoding:** UTF-8 XML
- **Template version:** 2015-08-01 extension
- **Code systems used:**
  - LOINC (2.16.840.1.113883.6.1) - Document types, lab tests, vitals
  - SNOMED-CT (2.16.840.1.113883.6.96) - Clinical terms, diagnoses
  - RxNorm (2.16.840.1.113883.6.88) - Medications
  - CDC Race/Ethnicity (2.16.840.1.113883.6.238) - Demographics
  - NUCC Provider Taxonomy (2.16.840.1.113883.6.101) - Provider specialties

### Key CCDA Sections Included:
- Allergies and Adverse Reactions (Template: 2.16.840.1.113883.10.20.22.2.6.1)
- Problem List (Template: 2.16.840.1.113883.10.20.22.2.5.1)
- Medications (Template: 2.16.840.1.113883.10.20.22.2.1.1)
- Laboratory Results (Template: 2.16.840.1.113883.10.20.22.2.3.1)
- Vital Signs (Template: 2.16.840.1.113883.10.20.22.2.4.1)
- Procedures (Template: 2.16.840.1.113883.10.20.22.2.7.1)

## Use Cases
These documents can be used for:
1. **Interoperability Testing:** Testing health information exchange systems
2. **Clinical Decision Support:** Training AI/ML models on diabetes progression
3. **Quality Measures:** Diabetes care quality metric calculations
4. **EHR Testing:** Validating CCDA import/export functionality
5. **Education:** Teaching clinical documentation and diabetes management
6. **Analytics:** Studying patterns of diabetes progression and complications

## Key Clinical Takeaways
This patient journey demonstrates:
- Progressive loss of glycemic control despite medication escalation
- Development of typical diabetes complications (neuropathy, retinopathy, nephropathy)
- Medication non-adherence challenges
- Need for multi-specialty care coordination in advanced diabetes
- Importance of lifestyle modifications (weight management, dietary adherence)
- Progression from oral medications to insulin therapy
- Acute complications (hypoglycemia, DKA) requiring emergency care

## Technical Notes
- All OIDs (Object Identifiers) are standard HL7/healthcare identifiers
- Document IDs are unique (DOC001-DOC020)
- Timestamps follow HL7 format (YYYYMMDDHHMMSS-TTTT)
- All medications use valid RxNorm codes
- All diagnoses use valid SNOMED-CT codes
- All lab tests use valid LOINC codes

## Generation Information
- **Generated:** November 10, 2025
- **Generator:** Python script + manual CCDA templates
- **Base Date:** January 15, 2022
- **Duration:** 36 months (900 days)
- **Format:** CCDA 2.1 (2015-08-01 templates)

---
*These are synthetic documents created for testing and educational purposes. All patient information is fictional.*
