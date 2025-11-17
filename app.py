from __future__ import annotations

import json
import logging
import os
import re
import uuid
from typing import List, Optional

import requests
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import exceptions
from pydantic import BaseModel, Field

from services import gemini, parser
from services import storage as storage_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "demo-project")
REGION = os.getenv("REGION", "us-central1")
RAW_BUCKET = os.getenv("RAW_BUCKET", f"{PROJECT_ID}-ccda-raw")
PARSED_BUCKET = os.getenv("PARSED_BUCKET", f"{PROJECT_ID}-ccda-parsed")
VERTEX_MODEL = os.getenv("VERTEX_MODEL", "gemini-1.5-pro")
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "60000"))
FACADE_URL = os.getenv("FACADE_URL", "").rstrip("/")
PARSE_URL = os.getenv("PARSE_URL")
RECON_URL = os.getenv("RECON_URL")

openapi_tags = [
    {"name": "ui", "description": "Patient session helpers used by the CRC web UI."},
    {"name": "summaries", "description": "Summaries that compare two CCDA files."},
]

app = FastAPI(title="Clinical Record Companion", openapi_tags=openapi_tags)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ParseRequest(BaseModel):
    session_id: str = Field(..., description="Patient session identifier")


class CompareRequest(BaseModel):
    a_uri: str
    b_uri: str


class AskRequest(BaseModel):
    session_id: str
    question: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/ui/upload", tags=["ui"])
async def ui_upload(
    files: Optional[List[UploadFile]] = File(default=None),
    files_alt: Optional[List[UploadFile]] = File(default=None, alias="files[]"),
    session_id: Optional[str] = Form(None),
):
    uploads = files_alt or files
    if not uploads:
        raise HTTPException(status_code=400, detail="Upload at least one CCDA file.")

    normalized_session = _normalize_session_id(session_id)
    raw_folder = f"sessions/{normalized_session}/raw"

    uploaded = []
    for file in uploads:
        filename = _safe_filename(file.filename)
        if not filename:
            filename = f"upload-{uuid.uuid4().hex}.xml"
        dest_path = f"{raw_folder}/{filename}"
        uri = storage_service.upload_file(file, RAW_BUCKET, dest_path)
        uploaded.append(uri)

    return {
        "session_id": normalized_session,
        "count": len(uploaded),
        "raw_uris": uploaded,
    }


@app.post("/ui/parse", tags=["ui"])
async def ui_parse(body: ParseRequest):
    session_id = _normalize_session_id(body.session_id)
    raw_prefix = f"sessions/{session_id}/raw"
    raw_uris = storage_service.list_session_objects(RAW_BUCKET, raw_prefix, ".xml")
    if not raw_uris:
        raise HTTPException(status_code=404, detail="No raw CCDAs found for this session.")

    parsed_uris = parser.parse_uploaded_xmls(raw_uris, PARSED_BUCKET)
    parsed_folder_uri = f"gs://{PARSED_BUCKET}/sessions/{session_id}/parsed/"
    reconciled_uri = parser.reconcile_patient(parsed_folder_uri)

    return {
        "parsed_uris": parsed_uris,
        "reconciled_uri": reconciled_uri,
    }


@app.get("/ui/session", tags=["ui"])
async def ui_session(session_id: str):
    normalized_session = _normalize_session_id(session_id)
    raw_uris = storage_service.list_session_objects(RAW_BUCKET, f"sessions/{normalized_session}/raw", ".xml")
    parsed_uris = storage_service.list_session_objects(PARSED_BUCKET, f"sessions/{normalized_session}/parsed", ".json")
    parsed_uris = [uri for uri in parsed_uris if not uri.endswith("patient_reconciled.json")]
    return {
        "session_id": normalized_session,
        "raw_uris": raw_uris,
        "parsed_uris": parsed_uris,
    }


@app.post("/ui/compare", tags=["ui"])
async def ui_compare(body: CompareRequest):
    if FACADE_URL:
        response = requests.post(f"{FACADE_URL}/summarize", json=body.dict(), timeout=90)
        response.raise_for_status()
        return response.json()
    return summarize(body)


@app.post("/ui/ask", tags=["ui"])
async def ui_ask(body: AskRequest):
    session_id = _normalize_session_id(body.session_id)
    parsed_folder_uri = f"gs://{PARSED_BUCKET}/sessions/{session_id}/parsed/"
    reconciled_uri = f"{parsed_folder_uri}patient_reconciled.json"

    try:
        patient_text = storage_service.read_gcs_text(reconciled_uri)
    except exceptions.NotFound:
        parsed_uris = storage_service.list_session_objects(PARSED_BUCKET, f"sessions/{session_id}/parsed", ".json")
        if not parsed_uris:
            raise HTTPException(status_code=404, detail="Parse the CCDAs before asking questions.")
        parser.reconcile_patient(parsed_folder_uri)
        patient_text = storage_service.read_gcs_text(reconciled_uri)

    patient_json = json.loads(patient_text)
    answer = gemini.answer_question(body.question, patient_json, model_name=VERTEX_MODEL, max_context_chars=MAX_CONTEXT_CHARS)
    used_chars = getattr(gemini.answer_question, "last_used_chars", 0)
    return {"answer": answer, "used_chars": used_chars}


@app.post("/summarize", tags=["summaries"])
def summarize(body: CompareRequest):
    if PARSE_URL and RECON_URL:
        return _remote_summarize(body.a_uri, body.b_uri)
    return _local_summarize(body.a_uri, body.b_uri)


def _remote_summarize(a_uri: str, b_uri: str) -> dict:
    headers = {
        "Content-Type": "application/json",
    }
    token = _fetch_id_token(PARSE_URL)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    parse_body = {"gcs_uri": None}
    parse_results = {}
    for label, uri in ("a", a_uri), ("b", b_uri):
        parse_body["gcs_uri"] = uri
        resp = requests.post(PARSE_URL, json=parse_body, headers=headers, timeout=90)
        resp.raise_for_status()
        parse_results[label] = resp.json()["parsed_json_gcs"]

    recon_headers = {"Content-Type": "application/json"}
    recon_token = _fetch_id_token(RECON_URL)
    if recon_token:
        recon_headers["Authorization"] = f"Bearer {recon_token}"
    recon_resp = requests.post(
        f"{RECON_URL}/reconcile",
        json={"a_json_gcs": parse_results["a"], "b_json_gcs": parse_results["b"]},
        headers=recon_headers,
        timeout=90,
    )
    recon_resp.raise_for_status()
    return recon_resp.json()


def _local_summarize(a_uri: str, b_uri: str) -> dict:
    parsed = parser.parse_uploaded_xmls([a_uri, b_uri], PARSED_BUCKET)
    docs = [json.loads(storage_service.read_gcs_text(uri)) for uri in parsed]
    med_summaries = []
    for doc in docs:
        meds = doc.get("signals", {}).get("medications") or doc.get("snippet", "")
        med_summaries.append({"filename": doc.get("filename"), "medications": meds[:5] if isinstance(meds, list) else meds})
    return {
        "version": "local-placeholder",
        "inputs": {"a_uri": a_uri, "b_uri": b_uri},
        "documents": med_summaries,
    }


def _fetch_id_token(audience: Optional[str]) -> str:
    if not audience:
        return ""
    try:
        from google.auth.transport import requests as ga_requests
        from google.oauth2 import id_token as google_id_token

        request = ga_requests.Request()
        return google_id_token.fetch_id_token(request, audience)
    except Exception as exc:  # pragma: no cover - relies on runtime
        logger.debug("ID token fetch skipped: %s", exc)
        return ""


def _normalize_session_id(session_id: Optional[str]) -> str:
    if not session_id:
        return uuid.uuid4().hex
    cleaned = session_id.strip().strip("/")
    if cleaned.lower().startswith("sessions/"):
        cleaned = cleaned.split("/", 1)[1]
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", cleaned)
    cleaned = cleaned.strip("-_")
    return cleaned or uuid.uuid4().hex


def _safe_filename(filename: Optional[str]) -> str:
    if not filename:
        return ""
    name = os.path.basename(filename)
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)
