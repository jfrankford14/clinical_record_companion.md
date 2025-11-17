"""Helpers for interacting with Google Cloud Storage."""

from __future__ import annotations

import re
from typing import List
from uuid import uuid4

from fastapi import UploadFile
from google.cloud import storage

_storage_client: storage.Client | None = None


def _client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def ensure_session(prefix: str) -> str:
    """Return a normalized session folder path.

    Parameters
    ----------
    prefix: str
        The parent folder for sessions (e.g., "sessions").
    """

    cleaned = prefix.strip("/") or "sessions"
    return f"{cleaned}/{uuid4().hex}/"


def upload_file(file: UploadFile, bucket: str, dest_path: str) -> str:
    """Upload ``file`` to ``gs://bucket/dest_path`` and return the URI."""

    blob_path = dest_path.lstrip("/")
    bucket_ref = _client().bucket(bucket)
    blob = bucket_ref.blob(blob_path)
    contents = file.file.read()
    blob.upload_from_string(contents, content_type=file.content_type or "application/octet-stream")
    file.file.seek(0)
    return f"gs://{bucket}/{blob_path}"


def list_session_objects(bucket: str, session: str, suffix: str) -> List[str]:
    """List objects within ``session`` that end with ``suffix``."""

    prefix = session.strip("/")
    if prefix and not prefix.endswith("/"):
        prefix = f"{prefix}/"
    blobs = _client().list_blobs(bucket, prefix=prefix)
    uris = [f"gs://{bucket}/{blob.name}" for blob in blobs if blob.name.endswith(suffix)]
    return sorted(uris)


def read_gcs_text(gs_uri: str) -> str:
    """Read an object as UTF-8 text from ``gs://`` URI."""

    bucket, blob_name = _split_gs_uri(gs_uri)
    blob = _client().bucket(bucket).blob(blob_name)
    return blob.download_as_text(encoding="utf-8")


def write_gcs_text(gs_uri: str, text: str) -> None:
    """Write UTF-8 text to ``gs://`` URI."""

    bucket, blob_name = _split_gs_uri(gs_uri)
    blob = _client().bucket(bucket).blob(blob_name)
    blob.upload_from_string(text, content_type="application/json")


def _split_gs_uri(gs_uri: str) -> tuple[str, str]:
    match = re.fullmatch(r"gs://([^/]+)/(.+)", gs_uri)
    if not match:
        raise ValueError(f"Invalid GCS URI: {gs_uri}")
    return match.group(1), match.group(2)
