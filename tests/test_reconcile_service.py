import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ccr.services.reconcile import app as reconcile_app


def test_merge_medications_deduplicates_and_marks_discrepancies():
    record_a = {
        "medications": [
            {"name": "Metformin 500 MG Oral Tablet"},
            {"name": "Warfarin"},
        ]
    }
    record_b = {
        "medications": [
            {"name": "metformin 500 mg oral tablet"},
            {"name": "Amoxicillin"},
        ]
    }

    unified, discrepancies = reconcile_app._merge_medications(record_a, record_b)

    unified_names = {entry["name"] for entry in unified}
    assert unified_names == {"Metformin 500 MG Oral Tablet", "Warfarin", "Amoxicillin"}

    discrepancy_map = {(entry["name"], entry["only_in"]) for entry in discrepancies}
    assert ("Warfarin", "A") in discrepancy_map
    assert ("Amoxicillin", "B") in discrepancy_map


def test_detect_ddi_uses_reference_csv(tmp_path):
    unified = [
        {"name": "Warfarin"},
        {"name": "Amoxicillin"},
    ]

    interactions = reconcile_app._detect_ddi(unified)
    assert any(
        interaction["drug_a"] == "Warfarin" and interaction["drug_b"] == "Amoxicillin"
        for interaction in interactions
    )


def test_detect_allergy_conflicts_flags_crosswalk_matches():
    allergies = [
        {"substance": "Penicillin"},
    ]
    unified = [
        {"name": "Amoxicillin"},
    ]

    conflicts = reconcile_app._detect_allergy_conflicts(allergies, unified)
    assert conflicts == [
        {
            "substance": "Penicillin",
            "linked_drug": "Amoxicillin",
            "severity": "moderate",
        }
    ]


def test_derive_tags_reflects_all_result_sets():
    tags = reconcile_app._derive_tags(
        dd_interactions=[{"drug_a": "Warfarin", "drug_b": "Amoxicillin"}],
        allergy_conflicts=[{"substance": "Penicillin", "linked_drug": "Amoxicillin"}],
        discrepancies=[{"name": "Metformin", "only_in": "A"}],
    )

    assert tags == ["ddi_detected", "allergy_conflict", "med_discrepancy"]
