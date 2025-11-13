import os
import json
import base64
from google.cloud import storage

storage_client = storage.Client()
PARSED_BUCKET = os.getenv("PARSED_BUCKET")

def _read(gcs_uri):
    assert gcs_uri.startswith("gs://")
    b, p = gcs_uri[5:].split("/", 1)
    return storage_client.bucket(b).blob(p).download_as_text()

def _write(gcs_uri, text, content_type="application/json"):
    b, p = gcs_uri[5:].split("/", 1)
    storage_client.bucket(b).blob(p).upload_from_string(text, content_type=content_type)

def parse_ccda(request):
    req = request.get_json(silent=True) or {}
    src = req.get("gcs_uri")
    if not src:
        return ({"error": "missing gcs_uri"}, 400)

    # Don’t parse yet — just prove the pipeline works
    xml = _read(src)
    payload = {
        "source_xml_gcs": src,
        "medications": [],
        "allergies": [],
        "meta": {"bytes": len(xml)}
    }

    out = f"gs://{PARSED_BUCKET}/{src.split('/')[-1].rsplit('.', 1)[0]}.json" if PARSED_BUCKET else src.rsplit('.', 1)[0] + ".json"
    _write(out, json.dumps(payload))
    return ({"parsed_json_gcs": out}, 200)
