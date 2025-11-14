import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v2.ccr.functions.parse_ccda import main as parse_main

FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


def _load_expected(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_build_parsed_document_matches_golden_basic():
    payload = parse_main.build_parsed_document(_load_fixture("ccda_basic.xml"), "gs://demo/basic.xml")
    expected = _load_expected("ccda_basic_expected.json")

    assert payload["medications"] == expected["medications"]
    assert payload["allergies"] == expected["allergies"]
    assert payload["problems"] == expected["problems"]
    assert payload["summary"] == {
        "med_count": len(expected["medications"]),
        "allergy_count": len(expected["allergies"]),
        "problem_count": len(expected["problems"]),
    }


def test_build_parsed_document_matches_golden_secondary():
    payload = parse_main.build_parsed_document(_load_fixture("ccda_secondary.xml"), "gs://demo/secondary.xml")
    expected = _load_expected("ccda_secondary_expected.json")

    assert payload["medications"] == expected["medications"]
    assert payload["allergies"] == expected["allergies"]
    assert payload["problems"] == expected["problems"]


def test_build_parsed_document_handles_malformed_xml():
    payload = parse_main.build_parsed_document(_load_fixture("ccda_malformed.xml"), "gs://demo/bad.xml")

    assert payload["medications"] == []
    assert payload["allergies"] == []
    assert payload["provenance"]["source_document"]["gcs_uri"] == "gs://demo/bad.xml"


def test_parse_ccda_response_contract(monkeypatch: pytest.MonkeyPatch):
    class DummyRequest:
        def __init__(self, body: dict):
            self._body = body

        def get_json(self, silent: bool = True):  # noqa: FBT002
            return self._body

    xml_text = _load_fixture("ccda_basic.xml")
    writes: dict = {}

    monkeypatch.setattr(parse_main, "_read", lambda _: xml_text)

    def fake_write(uri: str, text: str, content_type: str = "application/json") -> None:  # noqa: ARG001
        writes["uri"] = uri
        writes["text"] = text

    monkeypatch.setattr(parse_main, "_write", fake_write)
    response, status = parse_main.parse_ccda(DummyRequest({"gcs_uri": "gs://demo/basic.xml"}))

    assert status == 200
    assert "parsed_json_gcs" in response
    assert "summary" in response
    assert response["summary"]["med_count"] == 1
    assert writes["uri"].endswith("basic.json")
