"""FastAPI service that reconciles two parsed C-CDA JSON payloads."""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import csv

try:  # pragma: no cover - exercised when deployed
    import pandas as pd  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - allows local testing without dependency
    pd = None  # type: ignore[assignment]

try:  # pragma: no cover - exercised when deployed
    from fastapi import FastAPI, HTTPException
except ModuleNotFoundError:  # pragma: no cover - allows local testing without dependency
    FastAPI = None  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[override]
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

try:  # pragma: no cover - exercised when deployed
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover - allows local testing without dependency
    class BaseModel:  # type: ignore[override]
        """Minimal stand-in for Pydantic BaseModel used in local tests."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

    def Field(default=None, **kwargs):  # type: ignore[override]
        if "default_factory" in kwargs:
            return kwargs["default_factory"]()
        return default

try:  # pragma: no cover - exercised when deployed
    from google.cloud import storage  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - allows local testing without dependency
    storage = None  # type: ignore[assignment]

LOGGER = logging.getLogger("reconcile")
logging.basicConfig(level=logging.INFO)

if FastAPI is not None:
    app = FastAPI(title="Clinical Record Companion - Reconcile")
else:  # pragma: no cover - enables importing module without FastAPI installed

    class _FastAPIStub:
        def post(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    app = _FastAPIStub()


class ReconcileRequest(BaseModel):
    a_json_gcs: str = Field(..., description="gs:// URI for facility A parsed JSON")
    b_json_gcs: str = Field(..., description="gs:// URI for facility B parsed JSON")


class MedicationEntry(BaseModel):
    name: str
    sources: List[str]


class DiscrepancyEntry(BaseModel):
    name: str
    only_in: str


class InteractionEntry(BaseModel):
    drug_a: str
    drug_b: str
    severity: str
    note: Optional[str] = None


class AllergyConflictEntry(BaseModel):
    substance: str
    linked_drug: str
    severity: Optional[str] = None


class ReconcileResponse(BaseModel):
    unified_meds: List[MedicationEntry]
    unified_allergies: List[Dict[str, object]]
    discrepancies: List[DiscrepancyEntry]
    dd_interactions: List[InteractionEntry]
    allergy_conflicts: List[AllergyConflictEntry]
    sources: Dict[str, Optional[str]]
    tags: List[str] = Field(default_factory=list)


@app.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(payload: ReconcileRequest) -> ReconcileResponse:
    _validate_gcs_uri(payload.a_json_gcs)
    _validate_gcs_uri(payload.b_json_gcs)

    if storage is None:
        raise HTTPException(
            status_code=500,
            detail="google-cloud-storage dependency is not available",
        )

    storage_client = storage.Client()
    record_a = _load_json(storage_client, payload.a_json_gcs)
    record_b = _load_json(storage_client, payload.b_json_gcs)

    unified_meds, discrepancies = _merge_medications(record_a, record_b)
    dd_interactions = _detect_ddi(unified_meds)
    unified_allergies = _merge_allergies(record_a, record_b)
    allergy_conflicts = _detect_allergy_conflicts(unified_allergies, unified_meds)

    tags = _derive_tags(dd_interactions, allergy_conflicts, discrepancies)

    response = ReconcileResponse(
        unified_meds=[MedicationEntry(**entry) for entry in unified_meds],
        unified_allergies=unified_allergies,
        discrepancies=[DiscrepancyEntry(**entry) for entry in discrepancies],
        dd_interactions=[InteractionEntry(**entry) for entry in dd_interactions],
        allergy_conflicts=[AllergyConflictEntry(**entry) for entry in allergy_conflicts],
        sources={
            "A": _get_facility(record_a),
            "B": _get_facility(record_b),
        },
        tags=tags,
    )
    return response


def _validate_gcs_uri(uri: str) -> None:
    parsed = urlparse(uri)
    if parsed.scheme != "gs" or not parsed.netloc or not parsed.path:
        raise HTTPException(status_code=400, detail=f"Invalid GCS URI: {uri}")


def _load_json(client: "storage.Client", uri: str) -> Dict[str, object]:
    parsed = urlparse(uri)
    bucket_name, blob_name = parsed.netloc, parsed.path.lstrip("/")
    blob = client.bucket(bucket_name).blob(blob_name)
    data = blob.download_as_text()
    return json.loads(data)


def _normalize_med_name(name: str) -> str:
    return name.strip().lower()


def _merge_medications(record_a: Dict[str, object], record_b: Dict[str, object]) -> Tuple[List[Dict[str, object]], List[Dict[str, str]]]:
    meds_a = record_a.get("medications") or []
    meds_b = record_b.get("medications") or []

    unified: Dict[str, Dict[str, object]] = {}

    for med, source in ((meds_a, "A"), (meds_b, "B")):
        for entry in med:
            name = entry.get("name")
            if not name:
                continue
            key = _normalize_med_name(name)
            stored = unified.setdefault(
                key,
                {
                    "name": name,
                    "sources": [],
                },
            )
            if source not in stored["sources"]:
                stored["sources"].append(source)

    discrepancies: List[Dict[str, str]] = []
    for med_list, source in ((meds_a, "A"), (meds_b, "B")):
        for entry in med_list:
            name = entry.get("name")
            if not name:
                continue
            key = _normalize_med_name(name)
            if len(unified.get(key, {}).get("sources", [])) == 1 and unified[key]["sources"][0] == source:
                discrepancies.append({"name": unified[key]["name"], "only_in": source})

    unified_meds = sorted(unified.values(), key=lambda x: x["name"].lower())
    return unified_meds, discrepancies


def _merge_allergies(record_a: Dict[str, object], record_b: Dict[str, object]) -> List[Dict[str, object]]:
    combined: List[Dict[str, object]] = []
    for record, label in ((record_a, "A"), (record_b, "B")):
        for allergy in record.get("allergies", []) or []:
            entry = dict(allergy)
            entry.setdefault("status", "active")
            entry["source"] = label
            combined.append(entry)
    return combined


def _get_facility(record: Dict[str, object]) -> Optional[str]:
    encounter = record.get("encounter") or {}
    facility = encounter.get("facility") if isinstance(encounter, dict) else None
    return facility


def _detect_ddi(unified_meds: List[Dict[str, object]]) -> List[Dict[str, object]]:
    knowledge_rows = _load_med_knowledge()
    present = {entry["name"].strip(): entry for entry in unified_meds if entry.get("name")}
    present_lower = {_normalize_med_name(name): name for name in present}

    interactions: List[Dict[str, object]] = []
    for row in knowledge_rows:
        drug_a = (row.get("drug_a") or "").strip()
        drug_b = (row.get("drug_b") or "").strip()
        if not drug_a or not drug_b:
            continue
        if _normalize_med_name(drug_a) in present_lower and _normalize_med_name(drug_b) in present_lower:
            interactions.append(
                {
                    "drug_a": present_lower[_normalize_med_name(drug_a)],
                    "drug_b": present_lower[_normalize_med_name(drug_b)],
                    "severity": row.get("severity", "unknown"),
                    "note": row.get("note"),
                }
            )
    return interactions


def _detect_allergy_conflicts(allergies: List[Dict[str, object]], unified_meds: List[Dict[str, object]]) -> List[Dict[str, object]]:
    crosswalk_rows = _load_allergy_crosswalk()
    allergy_terms = {
        _normalize_med_name(allergy.get("substance", "")): allergy.get("substance")
        for allergy in allergies
        if allergy.get("substance")
    }
    meds_lower = {_normalize_med_name(entry["name"]): entry["name"] for entry in unified_meds}

    conflicts: List[Dict[str, object]] = []
    for row in crosswalk_rows:
        substance = (row.get("substance") or "").strip()
        linked_drug = (row.get("linked_drug") or "").strip()
        if _normalize_med_name(substance) in allergy_terms and _normalize_med_name(linked_drug) in meds_lower:
            conflicts.append(
                {
                    "substance": allergy_terms[_normalize_med_name(substance)] or substance,
                    "linked_drug": meds_lower[_normalize_med_name(linked_drug)],
                    "severity": row.get("severity"),
                }
            )
    return conflicts


def _derive_tags(
    dd_interactions: List[Dict[str, object]],
    allergy_conflicts: List[Dict[str, object]],
    discrepancies: List[Dict[str, str]],
) -> List[str]:
    tags: List[str] = []
    if dd_interactions:
        tags.append("ddi_detected")
    if allergy_conflicts:
        tags.append("allergy_conflict")
    if discrepancies:
        tags.append("med_discrepancy")
    return tags


@lru_cache(maxsize=1)
def _load_med_knowledge() -> List[Dict[str, str]]:
    path = os.path.join(os.path.dirname(__file__), "refs", "MedicationKnowledgeBase.csv")
    if pd is not None:
        frame = pd.read_csv(path)
        return frame.to_dict(orient="records")

    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=1)
def _load_allergy_crosswalk() -> List[Dict[str, str]]:
    path = os.path.join(os.path.dirname(__file__), "refs", "AllergyCrosswalk.csv")
    if pd is not None:
        frame = pd.read_csv(path)
        return frame.to_dict(orient="records")

    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
