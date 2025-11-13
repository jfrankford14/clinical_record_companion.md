"""End-to-end scenario tests that exercise every dataset manifest."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List
from urllib import error, request

import pytest


def _discover_scenarios() -> List[Dict[str, object]]:
    cases: List[Dict[str, object]] = []
    data_root = Path("data")
    for manifest_path in sorted(data_root.rglob("manifest.json")):
        manifest = json.loads(manifest_path.read_text())
        dataset = manifest.get("dataset") or manifest_path.parent.name
        for scenario in manifest.get("scenarios", []):
            cases.append(
                {
                    "dataset": dataset,
                    "dataset_dir": manifest_path.parent,
                    "scenario": scenario,
                }
            )
    return cases


SCENARIO_CASES = _discover_scenarios()


def _case_id(case: Dict[str, object]) -> str:
    scenario = case["scenario"]
    return f"{case['dataset']}::{scenario['id']}"


@pytest.mark.parametrize("case", SCENARIO_CASES, ids=_case_id)
def test_manifest_scenarios(case: Dict[str, object]):
    required_env = ["PROJECT_ID", "RAW_BUCKET", "PARSED_BUCKET", "PARSE_URL", "RECON_URL"]
    missing = [name for name in required_env if not os.getenv(name)]
    if missing:
        pytest.xfail(f"Scenario tests require env vars: {', '.join(missing)}")

    try:  # pragma: no cover - optional dependency for CI
        from google.cloud import storage  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        pytest.xfail("google-cloud-storage dependency not installed for scenario tests")

    project_id = os.environ["PROJECT_ID"]
    raw_bucket_name = os.environ["RAW_BUCKET"]
    parse_url = os.environ["PARSE_URL"].rstrip("/")
    recon_url = os.environ["RECON_URL"].rstrip("/")

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(raw_bucket_name)

    scenario = case["scenario"]
    dataset_dir = case["dataset_dir"]
    uploaded_uris: List[str] = []
    for file_name in scenario["files"]:
        local_path = Path(dataset_dir) / file_name
        if not local_path.exists():
            pytest.xfail(f"Missing CCDA file for scenario {scenario['id']}: {local_path}")
        blob_name = f"scenarios/{case['dataset']}/{scenario['id']}/{local_path.name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_path))
        uploaded_uris.append(f"gs://{raw_bucket_name}/{blob_name}")

    parsed_jsons: List[str] = []
    for uri in uploaded_uris:
        response = _post_json(parse_url, {"gcs_uri": uri})
        parsed_uri = response.get("parsed_json_gcs")
        if not parsed_uri:
            pytest.fail(f"parse_ccda response missing parsed_json_gcs for {uri}: {response}")
        parsed_jsons.append(parsed_uri)

    recon_response = _post_json(
        f"{recon_url}/reconcile",
        {"a_json_gcs": parsed_jsons[0], "b_json_gcs": parsed_jsons[1]},
    )

    _assert_expectations(scenario, recon_response)
    print(
        f"Scenario {scenario['id']} ({case['dataset']}) => "
        f"DDIs: {len(recon_response.get('dd_interactions', []))}, "
        f"Allergy conflicts: {len(recon_response.get('allergy_conflicts', []))}, "
        f"Discrepancies: {len(recon_response.get('discrepancies', []))}"
    )


def _assert_expectations(scenario: Dict[str, object], response: Dict[str, object]) -> None:
    expected = scenario.get("expected", {})
    expected_ddi = [tuple(sorted(map(str.lower, pair))) for pair in expected.get("ddi_pairs", [])]
    observed_ddi = [
        tuple(sorted((entry.get("drug_a", "").lower(), entry.get("drug_b", "").lower())))
        for entry in response.get("dd_interactions", [])
    ]
    for pair in expected_ddi:
        assert pair in observed_ddi, f"Missing DDI pair {pair} for scenario {scenario['id']}"

    expected_allergy = [
        (item.get("substance", "").lower(), item.get("drug", "").lower())
        for item in expected.get("allergy_conflicts", [])
    ]
    observed_allergy = [
        (entry.get("substance", "").lower(), entry.get("linked_drug", "").lower())
        for entry in response.get("allergy_conflicts", [])
    ]
    for conflict in expected_allergy:
        assert (
            conflict in observed_allergy
        ), f"Missing allergy conflict {conflict} for scenario {scenario['id']}"

    for needle in expected.get("discrepancies_contains", []) or []:
        if not any(needle.lower() in (entry.get("name", "").lower()) for entry in response.get("discrepancies", [])):
            pytest.fail(f"Expected discrepancy containing '{needle}' for scenario {scenario['id']}")


def _post_json(url: str, payload: Dict[str, object]) -> Dict[str, object]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
    except error.HTTPError as exc:  # pragma: no cover - surfaced only when endpoints fail
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AssertionError(f"HTTP {exc.code} calling {url}: {detail}") from exc
    except error.URLError as exc:  # pragma: no cover - surfaced only when network fails
        raise AssertionError(f"Failed to reach {url}: {exc}") from exc

    return json.loads(data or "{}")
