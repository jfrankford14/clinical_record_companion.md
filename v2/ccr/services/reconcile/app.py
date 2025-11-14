from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - prefer real FastAPI when available
    from fastapi import FastAPI, HTTPException
except ModuleNotFoundError:  # noqa: PERF203 - lightweight fallback for tests
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str = ""):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class FastAPI:  # type: ignore[override]
        def __init__(self):
            self._routes = {}

        def get(self, path: str):
            def decorator(func):
                self._routes[("GET", path)] = func
                return func

            return decorator

        def post(self, path: str):
            def decorator(func):
                self._routes[("POST", path)] = func
                return func

            return decorator


try:  # pragma: no cover - prefer real Pydantic when available
    from pydantic import BaseModel
except ModuleNotFoundError:  # noqa: PERF203
    class BaseModel:  # type: ignore[override]
        def __init__(self, **data):
            for field in getattr(self, "__annotations__", {}):
                setattr(self, field, data.get(field))

        def model_dump(self) -> Dict[str, object]:
            return {field: getattr(self, field) for field in getattr(self, "__annotations__", {})}

from google.cloud import storage

from v2.ccr.services.reconcile import logic

logger = logging.getLogger("reconcile_v2_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _log_event(event: str, **fields: object) -> None:
    logger.info(json.dumps({"event": event, **fields}))


app = FastAPI()
REF_PATH = Path(__file__).resolve().parent / "refs" / "MedicationKnowledgeBase.csv"
if not REF_PATH.exists():
    raise FileNotFoundError("MedicationKnowledgeBase.csv is required for safety checks")
_DDI_REFERENCE = logic.load_ddi_reference(REF_PATH)
_storage_client: storage.Client | None = None


class ReconcileIn(BaseModel):
    a_json_gcs: str
    b_json_gcs: str


def _client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def _read_json(gcs_uri: str) -> dict:
    if not gcs_uri.startswith("gs://"):
        raise ValueError("Expected gs:// URI")
    bucket_name, blob_path = gcs_uri[5:].split("/", 1)
    blob = _client().bucket(bucket_name).blob(blob_path)
    return json.loads(blob.download_as_text())


@app.get("/healthz")
def healthz() -> Dict[str, object]:
    return {"ok": True, "version": "v2"}


@app.post("/reconcile")
def reconcile(inp: ReconcileIn):
    _log_event("reconcile_request", source_a=inp.a_json_gcs, source_b=inp.b_json_gcs)
    try:
        record_a = _read_json(inp.a_json_gcs)
        record_b = _read_json(inp.b_json_gcs)
        result = logic.reconcile_records(record_a, record_b, _DDI_REFERENCE)
    except Exception as exc:  # noqa: BLE001
        _log_event("reconcile_failure", source_a=inp.a_json_gcs, source_b=inp.b_json_gcs, error=str(exc))
        raise HTTPException(status_code=500, detail="failed to reconcile payloads") from exc
    response = {
        **result,
        "sources": {"a": inp.a_json_gcs, "b": inp.b_json_gcs},
        "tags": ["v2_mvp"],
        "version": "v2_mvp",
    }
    _log_event(
        "reconcile_success",
        source_a=inp.a_json_gcs,
        source_b=inp.b_json_gcs,
        med_count=len(response["unified_meds"]),
        allergy_count=len(response["unified_allergies"]),
        dd_interaction_count=len(response["dd_interactions"]),
    )
    return response


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run reconciliation locally without GCS")
    parser.add_argument("a_json", help="Path to parsed JSON A")
    parser.add_argument("b_json", help="Path to parsed JSON B")
    args = parser.parse_args()
    record_a = json.loads(Path(args.a_json).read_text(encoding="utf-8"))
    record_b = json.loads(Path(args.b_json).read_text(encoding="utf-8"))
    result = logic.reconcile_records(record_a, record_b, _DDI_REFERENCE)
    result.update({"sources": {"a": args.a_json, "b": args.b_json}, "tags": ["v2_mvp"], "version": "v2_mvp"})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
