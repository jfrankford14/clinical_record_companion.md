from fastapi import FastAPI
import requests, os

app = FastAPI()

PARSE_URL = os.environ["PARSE_URL"]       # Cloud Function full URL
RECON_URL = os.environ["RECON_URL"]       # Cloud Run base URL (no trailing slash)

def id_token(audience: str) -> str:
    # Works in Cloud Run / GCE env; falls back silently for local
    try:
        import google.auth.transport.requests, google.oauth2.id_token
        req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(req, audience)
    except Exception:
        return ""

@app.post("/summarize")
def summarize(body: dict):
    a_uri, b_uri = body["a_uri"], body["b_uri"]

    # Call parse twice
    p_hdr = {"Authorization": f"Bearer {id_token(PARSE_URL)}",
             "Content-Type": "application/json"}
    a_out = requests.post(PARSE_URL, json={"gcs_uri": a_uri}, headers=p_hdr).json()
    b_out = requests.post(PARSE_URL, json={"gcs_uri": b_uri}, headers=p_hdr).json()
    a_json, b_json = a_out["parsed_json_gcs"], b_out["parsed_json_gcs"]

    # Call reconcile
    r_hdr = {"Authorization": f"Bearer {id_token(RECON_URL)}",
             "Content-Type": "application/json"}
    r = requests.post(f"{RECON_URL}/reconcile",
                      json={"a_json_gcs": a_json, "b_json_gcs": b_json},
                      headers=r_hdr).json()

    # Simple friendly output
    bullets = []
    for m in r.get("unified_meds", []):
        bullets.append(f"{m['name']} — {m.get('strength')}, {m.get('route')} {m.get('frequency')} (start {m.get('start_date')})")

    return {
        "inputs": {"a_uri": a_uri, "b_uri": b_uri},
        "med_summary": bullets[:8],
        "dd_interactions": r.get("dd_interactions", []),
        "allergy_conflicts": r.get("allergy_conflicts", []),
        "sources": r.get("sources", {}),
        "tags": r.get("tags", []),
        "version": "facade_v1"
    }
