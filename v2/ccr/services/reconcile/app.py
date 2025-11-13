from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import json
import os
from google.cloud import storage

app = FastAPI()
storage_client = storage.Client()


class ReconcileIn(BaseModel):
    a_json_gcs: str
    b_json_gcs: str


def _read_json(gcs_uri: str) -> dict:
    assert gcs_uri.startswith("gs://")
    b, p = gcs_uri[5:].split("/", 1)
    return json.loads(storage_client.bucket(b).blob(p).download_as_text())


@app.post("/reconcile")
def reconcile(inp: ReconcileIn):
    a = _read_json(inp.a_json_gcs)
    b = _read_json(inp.b_json_gcs)
    meds = (a.get("medications") or []) + (b.get("medications") or [])
    allergies = (a.get("allergies") or []) + (b.get("allergies") or [])
    return {
        "unified_meds": meds,
        "unified_allergies": allergies,
        "discrepancies": [],
        "dd_interactions": [],
        "allergy_conflicts": [],
        "sources": {"a": inp.a_json_gcs, "b": inp.b_json_gcs},
        "tags": ["stub_e2e_ok"],
    }
