import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v2.ccr.services.reconcile import app as reconcile_app
from v2.ccr.services.reconcile import logic

REF_PATH = PROJECT_ROOT / "v2" / "ccr" / "services" / "reconcile" / "refs" / "MedicationKnowledgeBase.csv"
_DDI_REFERENCE = logic.load_ddi_reference(REF_PATH)
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def test_merge_medications_prefers_recent_and_tracks_discrepancies():
    record_a = {"medications": [{"name": "Metformin", "start_date": "2020-01-01"}]}
    record_b = {"medications": [{"name": "Metformin", "start_date": "2021-01-01"}, {"name": "Warfarin"}]}

    unified, delta = logic.merge_medications(record_a, record_b)

    assert any(entry["start_date"] == "2021-01-01" for entry in unified if entry["name"] == "Metformin")
    assert "Warfarin" in delta["only_in_b"]


def test_detect_ddi_uses_reference_csv():
    meds = [{"name": "Warfarin"}, {"name": "Amoxicillin"}]
    dd_interactions = logic.detect_ddi(meds, _DDI_REFERENCE)
    assert any(interaction["severity"] == "moderate" for interaction in dd_interactions)


def test_detect_allergy_conflicts():
    allergies = [{"substance": "Penicillin", "severity": "severe"}]
    meds = [{"name": "Penicillin VK"}]
    conflicts = logic.detect_allergy_conflicts(allergies, meds)
    assert conflicts == [
        {
            "substance": "Penicillin",
            "linked_drug": "Penicillin VK",
            "severity": "severe",
            "reaction": None,
        }
    ]


def test_reconcile_records_includes_all_sections():
    record_a = {"medications": [{"name": "Metformin"}], "allergies": []}
    record_b = {"medications": [], "allergies": [{"substance": "Penicillin"}]}

    result = logic.reconcile_records(record_a, record_b, _DDI_REFERENCE)

    assert result["unified_meds"]
    assert result["unified_allergies"]
    assert "med_lists" in result["discrepancies"]


def test_service_endpoint_detects_conflicts(monkeypatch):
    record_a = json.loads((FIXTURES / "parsed_record_a.json").read_text())
    record_b = json.loads((FIXTURES / "parsed_record_b.json").read_text())

    def fake_read_json(uri: str):
        return record_a if uri.endswith("a.json") else record_b

    monkeypatch.setattr(reconcile_app, "_read_json", fake_read_json)
    data = reconcile_app.reconcile(
        reconcile_app.ReconcileIn(a_json_gcs="gs://demo/a.json", b_json_gcs="gs://demo/b.json")
    )
    assert data["dd_interactions"], "Expected DDI hits"
    assert data["allergy_conflicts"], "Expected allergy conflict hits"
    assert data["discrepancies"]["med_lists"]["only_in_a"] or data["discrepancies"]["med_lists"]["only_in_b"]
    assert data["sources"] == {"a": "gs://demo/a.json", "b": "gs://demo/b.json"}
    assert data["version"] == "v2_mvp"
