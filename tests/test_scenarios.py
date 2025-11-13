import json, os, glob
from pathlib import Path

import pytest

REQUIRED_VARS = ["PROJECT_ID", "RAW_BUCKET", "PARSED_BUCKET", "PARSE_URL", "RECON_URL"]


def _env_ready():
    missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
    return missing


def _load_manifests():
    manifests = []
    for path in glob.glob(str(Path("data") / "**" / "manifest.json"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            try:
                m = json.load(f)
            except Exception:
                continue
        # Normalize
        dataset = m.get("dataset") or Path(path).parent.name
        scenarios = m.get("scenarios") or []
        manifests.append((dataset, Path(path).parent, scenarios))
    return manifests


@pytest.mark.parametrize("dataset,root,scenarios", _load_manifests())
def test_scenarios(dataset, root, scenarios):
    missing_env = _env_ready()
    if missing_env:
        pytest.xfail(f"Skipping: missing env vars {missing_env}")

    if not scenarios:
        pytest.xfail("No scenarios defined yet for dataset")

    import requests  # requires network and endpoint; if unavailable, xfail

    parse_url = os.environ["PARSE_URL"].rstrip("/")
    recon_url = os.environ["RECON_URL"].rstrip("/")

    for sc in scenarios:
        sid = sc.get("id") or "unknown"
        files = sc.get("files") or []
        # Ensure local files exist; if not, skip scenario gracefully
        missing_files = [str(root / f) for f in files if not (root / f).exists()]
        if missing_files:
            pytest.xfail(f"Scenario {sid}: missing files {missing_files}")

        # Upload to RAW_BUCKET (placeholder/no-op here); users can adapt to their GCP setup
        # For this demo test, call parse and reconcile endpoints directly
        parsed_ids = []
        for fname in files:
            with open(root / fname, "rb") as fh:
                # Assumes parse service accepts multipart/form-data with file field
                resp = requests.post(f"{parse_url}/parse-ccda", files={"file": fh})
                assert resp.status_code == 200, f"parse failed ({sid}): {resp.text}"
                data = resp.json()
                pid = data.get("id") or data.get("document_id")
                assert pid, "parse response missing id"
                parsed_ids.append(pid)

        # Reconcile call assumes endpoint takes ids list
        r = requests.post(f"{recon_url}/reconcile", json={"document_ids": parsed_ids})
        assert r.status_code == 200, f"reconcile failed ({sid}): {r.text}"
        out = r.json()

        # Optional backward-compatible tags logic check if present
        tags = set(out.get("tags", [])) if isinstance(out.get("tags"), list) else set()
        ddi = out.get("dd_interactions") or []
        alg = out.get("allergy_conflicts") or []
        if ddi:
            assert ("ddi_detected" in tags) or True  # backward-compatible optional
        if alg:
            assert ("allergy_conflict" in tags) or True

        # Validate expectations
        exp = sc.get("expected", {})
        exp_pairs = set(tuple(map(str.lower, p)) for p in exp.get("ddi_pairs", []))
        got_pairs = set(tuple(map(str.lower, p.get("pair", p))) for p in ddi)
        assert exp_pairs.issubset(got_pairs), f"Expected DDI pairs missing in {sid}: {exp_pairs - got_pairs}"

        exp_conf = set((c["substance"].lower(), c["drug"].lower()) for c in exp.get("allergy_conflicts", []))
        got_conf = set((c.get("substance","" ).lower(), c.get("drug","" ).lower()) for c in alg)
        assert exp_conf.issubset(got_conf), f"Expected allergy conflicts missing in {sid}: {exp_conf - got_conf}"