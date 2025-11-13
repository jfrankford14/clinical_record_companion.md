import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ccr.functions.parse_ccda import main as parse_main


def load_root(filename: str) -> ET.Element:
    path = Path(__file__).resolve().parents[1] / "data" / "diabetes" / filename
    return ET.parse(path).getroot()


def test_extract_patient_and_encounter_details():
    root = load_root("01_PrimaryCare_Initial_Diagnosis.xml")

    patient = parse_main._extract_patient(root)
    encounter = parse_main._extract_encounter(root)

    assert patient == {
        "id": "555-77-8888",
        "name": "John Michael Martinez",
    }
    assert encounter["facility"] == "Chicago Family Medicine Clinic"
    assert encounter["date"] == "20220115"


def test_extract_medications_includes_metformin_and_lisinopril():
    root = load_root("01_PrimaryCare_Initial_Diagnosis.xml")

    meds = parse_main._extract_medications(root)
    names = {entry["name"] for entry in meds}

    assert "Metformin 500 MG Oral Tablet" in names
    assert "Lisinopril 10 MG Oral Tablet" in names

    metformin = next(item for item in meds if item["name"] == "Metformin 500 MG Oral Tablet")
    assert metformin["dose"] == {"value": "500", "unit": "mg"}
    assert metformin["route"] == "Oral"


def test_extract_allergies_returns_penincillin_history():
    root = load_root("01_PrimaryCare_Initial_Diagnosis.xml")

    allergies = parse_main._extract_allergies(root)
    assert allergies, "Expected at least one allergy entry"

    penicillin = next(item for item in allergies if item["substance"] == "Penicillin")
    assert penicillin["reaction"] == "Hives"
    assert penicillin["severity"] == "Moderate"
    assert penicillin["status"] == "completed"


def test_build_payload_matches_individual_extractors():
    root = load_root("01_PrimaryCare_Initial_Diagnosis.xml")

    aggregate = parse_main._build_payload(root)

    assert aggregate["patient"] == parse_main._extract_patient(root)
    assert aggregate["encounter"] == parse_main._extract_encounter(root)
    assert aggregate["medications"] == parse_main._extract_medications(root)
    assert aggregate["allergies"] == parse_main._extract_allergies(root)
