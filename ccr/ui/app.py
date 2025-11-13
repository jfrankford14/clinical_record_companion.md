"""Minimal Streamlit UI for the Clinical Record Companion demo."""

from __future__ import annotations

import os
import uuid

import requests
import streamlit as st
from google.cloud import storage

RAW_BUCKET = os.getenv("RAW_BUCKET") or f"{os.getenv('PROJECT_ID', 'demo')}-ccda-raw"
PARSED_BUCKET = os.getenv("PARSED_BUCKET") or RAW_BUCKET.replace("-raw", "-parsed")
PARSE_FUNCTION_URL = os.getenv("PARSE_FUNCTION_URL", "")
RECONCILE_URL = os.getenv("RECONCILE_URL", "")

st.set_page_config(page_title="Clinical Record Companion", layout="wide")
st.title("Clinical Record Companion – Medication Reconciliation")

if not PARSE_FUNCTION_URL or not RECONCILE_URL:
    st.warning("Set PARSE_FUNCTION_URL and RECONCILE_URL environment variables to enable end-to-end execution.")

uploaded_a = st.file_uploader("Upload Facility A C-CDA", type=["xml", "XML"], key="a")
uploaded_b = st.file_uploader("Upload Facility B C-CDA", type=["xml", "XML"], key="b")

if st.button("Run Reconciliation"):
    if not uploaded_a or not uploaded_b:
        st.error("Please upload both Facility A and Facility B CCDAs.")
    elif not PARSE_FUNCTION_URL or not RECONCILE_URL:
        st.error("Missing endpoint configuration. Configure PARSE_FUNCTION_URL and RECONCILE_URL.")
    else:
        storage_client = storage.Client()
        a_uri = _upload_file(storage_client, uploaded_a, RAW_BUCKET, prefix="A")
        b_uri = _upload_file(storage_client, uploaded_b, RAW_BUCKET, prefix="B")

        with st.spinner("Parsing Facility A CCDA..."):
            parsed_a = _invoke_parse(PARSE_FUNCTION_URL, a_uri)
        with st.spinner("Parsing Facility B CCDA..."):
            parsed_b = _invoke_parse(PARSE_FUNCTION_URL, b_uri)

        with st.spinner("Reconciling medication lists..."):
            reconcile_payload = {
                "a_json_gcs": parsed_a["parsed_json_gcs"],
                "b_json_gcs": parsed_b["parsed_json_gcs"],
            }
            response = requests.post(RECONCILE_URL, json=reconcile_payload, timeout=60)
            response.raise_for_status()
            results = response.json()

        st.success("Reconciliation complete.")

        meds_col, allergies_col = st.columns(2)
        with meds_col:
            st.subheader("Unified Medication List")
            for med in results.get("unified_meds", []):
                st.markdown(f"**{med['name']}** — sources: {', '.join(med['sources'])}")
        with allergies_col:
            st.subheader("Allergies")
            st.json(results.get("unified_allergies", []))

        st.subheader("Discrepancies")
        st.table(results.get("discrepancies", []))

        st.subheader("Drug–Drug Interactions")
        st.table(results.get("dd_interactions", []))

        st.subheader("Allergy Conflicts")
        st.table(results.get("allergy_conflicts", []))


def _upload_file(client: storage.Client, file_uploader, bucket_name: str, prefix: str) -> str:
    bucket = client.bucket(bucket_name)
    blob_name = f"uploads/{prefix}-{uuid.uuid4().hex}.xml"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(file_uploader.getvalue(), content_type="application/xml")
    return f"gs://{bucket_name}/{blob_name}"


def _invoke_parse(url: str, gcs_uri: str) -> dict:
    response = requests.post(url, json={"gcs_uri": gcs_uri}, timeout=60)
    response.raise_for_status()
    return response.json()
