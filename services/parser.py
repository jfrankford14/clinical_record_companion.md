"""Placeholder parser and reconciler orchestration."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List
from uuid import uuid4

from google.cloud import storage

from .storage import read_gcs_text, write_gcs_text

_storage_client: storage.Client | None = None


KEYWORDS = {
    "medications": ["medication", "rx", "drug", "tablet", "capsule"],
    "problems": ["problem", "diagnosis", "condition", "issue"],
    "allergies": ["allergy", "sensitivity", "reaction"],
    "labs": ["lab", "result", "test", "panel"],
    "visits": ["encounter", "visit", "admission", "discharge"],
}


def _client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def parse_uploaded_xmls(raw_uris: List[str], parsed_bucket: str) -> List[str]:
    """Parse raw XML files and write lightweight JSON envelopes."""

    parsed_uris: List[str] = []
    for raw_uri in raw_uris:
        try:
            xml_text = read_gcs_text(raw_uri)
        except Exception as exc:  # pragma: no cover - depends on GCS state
            raise RuntimeError(f"Unable to read {raw_uri}: {exc}") from exc

        blob_name = _parsed_blob_name(raw_uri)
        dest_uri = f"gs://{parsed_bucket}/{blob_name}"
        snippet = xml_text.strip()[:8000]
        signals = _extract_signals(xml_text)
        payload = {
            "source_uri": raw_uri,
            "filename": Path(blob_name(raw_uri)).name,
            "signals": signals,
            "snippet": snippet,
        }
        write_gcs_text(dest_uri, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        parsed_uris.append(dest_uri)

    return parsed_uris


def reconcile_patient(session_parsed_folder: str) -> str:
    """Merge parsed artifacts into a patient-level JSON file."""

    bucket, prefix = _split_gs_folder(session_parsed_folder)
    prefix = prefix.rstrip("/") + "/"
    blobs = _client().list_blobs(bucket, prefix=prefix)
    documents: list[dict] = []
    aggregate = {key: [] for key in KEYWORDS.keys()}

    for blob in blobs:
        if not blob.name.endswith(".json") or blob.name.endswith("patient_reconciled.json"):
            continue
        text = blob.download_as_text(encoding="utf-8")
        doc = json.loads(text)
        documents.append({"filename": doc.get("filename"), "source_uri": doc.get("source_uri")})
        for key in KEYWORDS.keys():
            aggregate[key].extend(doc.get("signals", {}).get(key, []))

    deduped = {key: sorted(_dedupe(values)) for key, values in aggregate.items()}
    patient = {
        "documents": documents,
        "signals": deduped,
        "notes": "Reconciled placeholder data for Clinical Record Companion.",
    }

    reconciled_uri = f"gs://{bucket}/{prefix}patient_reconciled.json"
    write_gcs_text(reconciled_uri, json.dumps(patient, ensure_ascii=False, separators=(",", ":")))
    return reconciled_uri


def _parsed_blob_name(raw_uri: str) -> str:
    _, blob = _split_gs_folder(raw_uri)
    path = Path(blob)
    parent_parts = list(path.parts)
    if "raw" in parent_parts:
        idx = parent_parts.index("raw")
        parent_parts[idx] = "parsed"
    else:
        parent_parts.insert(-1, "parsed")
    new_parent = "/".join(parent_parts[:-1])
    stem = path.stem or f"doc-{uuid4().hex}"
    return f"{new_parent}/{stem}.json"


def _extract_signals(xml_text: str) -> dict[str, list[str]]:
    signals: dict[str, list[str]] = {key: [] for key in KEYWORDS.keys()}
    lines = [line.strip() for line in xml_text.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        for category, hints in KEYWORDS.items():
            if any(hint in lower for hint in hints):
                cleaned = re.sub(r"\s+", " ", line)
                if cleaned and cleaned not in signals[category]:
                    signals[category].append(cleaned[:280])
    return signals


def _dedupe(values: Iterable[str]) -> Iterable[str]:
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            yield value


def _split_gs_folder(gs_uri: str) -> tuple[str, str]:
    match = re.fullmatch(r"gs://([^/]+)/(.+)", gs_uri)
    if not match:
        raise ValueError(f"Invalid GCS URI: {gs_uri}")
    return match.group(1), match.group(2)


def blob_name(gs_uri: str) -> str:
    """Return the blob path for a ``gs://`` URI."""

    return _split_gs_folder(gs_uri)[1]
