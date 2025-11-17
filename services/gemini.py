"""Gemini helper for patient-level Q&A."""

from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any, Dict

from google.cloud import aiplatform

_SYSTEM_PROMPT = (
    "You are Clinical Record Companion, a clinical summarization and reasoning assistant. "
    "Answer clearly and concisely. If uncertain, state what else you need."
)

_aiplatform_lock = Lock()
_aiplatform_ready = False


def _ensure_initialized() -> None:
    global _aiplatform_ready
    if _aiplatform_ready:
        return
    with _aiplatform_lock:
        if _aiplatform_ready:
            return
        project = os.getenv("PROJECT_ID")
        location = os.getenv("REGION", "us-central1")
        aiplatform.init(project=project, location=location)
        _aiplatform_ready = True


def answer_question(
    question: str,
    patient_json: Dict[str, Any],
    model_name: str = "gemini-1.5-pro",
    max_context_chars: int = 60000,
) -> str:
    """Send a compact question + context prompt to Gemini."""

    _ensure_initialized()
    model = aiplatform.GenerativeModel(model_name)
    compact_context = _build_context(patient_json)
    context_payload = json.dumps(compact_context, ensure_ascii=False, separators=(",", ":"))
    truncated = False
    if len(context_payload) > max_context_chars:
        context_payload = context_payload[:max_context_chars]
        truncated = True

    prompt = (
        f"Question: {question.strip()}\n\n"
        f"Patient context: {context_payload}"
    )
    if truncated:
        prompt += "\n\nContext truncated to fit model limits."

    response = model.generate_content(
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        system_instruction=_SYSTEM_PROMPT,
        generation_config={"temperature": 0.2, "top_p": 0.9},
    )
    text = getattr(response, "text", None)
    if not text:
        candidates = getattr(response, "candidates", [])
        if candidates:
            parts = candidates[0].content.parts
            text = "\n".join(part.text for part in parts if getattr(part, "text", None))
    if not text:
        text = "No answer returned."

    answer_question.last_used_chars = len(context_payload)  # type: ignore[attr-defined]
    return text.strip()


def _build_context(patient_json: Dict[str, Any]) -> Dict[str, Any]:
    documents = patient_json.get("documents", [])
    signals = patient_json.get("signals") or patient_json.get("sections") or {}
    context = {
        "documents": documents,
        "medications": signals.get("medications", [])[:25],
        "problems": signals.get("problems", [])[:25],
        "allergies": signals.get("allergies", [])[:25],
        "labs": signals.get("labs", [])[:25],
        "visits": signals.get("visits", [])[:25],
        "notes": patient_json.get("notes", ""),
    }
    return context
