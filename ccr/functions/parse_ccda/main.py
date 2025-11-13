"""Cloud Function entrypoint for parsing C-CDA documents into normalized JSON."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

try:  # pragma: no cover - exercised in deployed environment
    from google.cloud import storage
except ModuleNotFoundError:  # pragma: no cover - allows local tests without dependency
    storage = None  # type: ignore[assignment]

# Configure module-level logger once. Cloud Functions already attaches handler.
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

NAMESPACES = {"hl7": "urn:hl7-org:v3"}

def parse_ccda(request):
    """HTTP Cloud Function entrypoint for C-CDA parsing.

    Args:
        request: flask.Request containing JSON payload {"gcs_uri": "gs://bucket/path.xml"}.

    Returns:
        (tuple) JSON dict with parsed_json_gcs key and HTTP status code.
    """

    try:
        request_json = request.get_json(silent=True) or {}
    except Exception:  # pragma: no cover - defensive for malformed payloads
        request_json = {}

    gcs_uri = request_json.get("gcs_uri")
    if not gcs_uri or not isinstance(gcs_uri, str) or not gcs_uri.startswith("gs://"):
        LOGGER.error("Invalid or missing gcs_uri in request: %s", gcs_uri)
        return ({"error": "Expected JSON body with gs:// gcs_uri"}, 400)

    LOGGER.info("Starting CCDA parse for URI: %s", gcs_uri)
    try:
        source_bucket, source_blob = _split_gcs_uri(gcs_uri)
        if storage is None:
            raise RuntimeError(
                "google-cloud-storage is required to run parse_ccda."
            )

        storage_client = storage.Client()
        xml_bytes = storage_client.bucket(source_bucket).blob(source_blob).download_as_bytes()
        root = ET.fromstring(xml_bytes)

        parsed_payload = _build_payload(root)

        destination_uri = _write_json(storage_client, gcs_uri, parsed_payload)
        LOGGER.info("Successfully parsed %s -> %s", gcs_uri, destination_uri)
        return ({"parsed_json_gcs": destination_uri}, 200)
    except Exception as exc:  # pragma: no cover - surfaced via logs
        LOGGER.exception("Failed to parse CCDA: %%s", exc)
        return ({"error": str(exc)}, 500)


def _split_gcs_uri(gcs_uri: str) -> tuple[str, str]:
    parsed = urlparse(gcs_uri)
    if parsed.scheme != "gs" or not parsed.netloc or not parsed.path:
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")
    return parsed.netloc, parsed.path.lstrip("/")


def _build_payload(root: ET.Element) -> Dict[str, Any]:
    """Assemble the normalized payload from a parsed XML root element."""

    return {
        "patient": _extract_patient(root),
        "encounter": _extract_encounter(root),
        "medications": _extract_medications(root),
        "allergies": _extract_allergies(root),
    }


def _get_parsed_bucket() -> str:
    """Derive the bucket used for parsed JSON payloads."""

    explicit_bucket = os.getenv("PARSED_BUCKET")
    if explicit_bucket:
        return explicit_bucket

    project_id = (
        os.getenv("PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
    )
    if not project_id:
        raise RuntimeError("Missing PROJECT_ID environment variable.")
    return f"{project_id}-ccda-parsed"


def _write_json(client: "storage.Client", source_uri: str, payload: Dict[str, Any]) -> str:
    source_bucket, source_blob = _split_gcs_uri(source_uri)
    parsed_bucket_name = _get_parsed_bucket()

    # Preserve the original folder path + filename, but swap extension for .json.
    filename = os.path.basename(source_blob)
    base_name = os.path.splitext(filename)[0]
    directory = os.path.dirname(source_blob)
    if directory and directory != ".":
        destination_blob = f"{directory}/{base_name}.json"
    else:
        destination_blob = f"{base_name}.json"

    bucket = client.bucket(parsed_bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_string(
        json.dumps(payload, ensure_ascii=False, indent=2),
        content_type="application/json",
    )

    return f"gs://{parsed_bucket_name}/{destination_blob}"


def _extract_patient(root: ET.Element) -> Dict[str, Optional[str]]:
    patient: Dict[str, Optional[str]] = {"id": None, "name": None}
    patient_role = root.find(".//hl7:recordTarget/hl7:patientRole", NAMESPACES)
    if patient_role is None:
        return patient

    patient_id_elem = patient_role.find("hl7:id", NAMESPACES)
    if patient_id_elem is not None:
        patient["id"] = (
            patient_id_elem.get("extension")
            or patient_id_elem.get("root")
        )

    name_elem = patient_role.find("hl7:patient/hl7:name", NAMESPACES)
    if name_elem is not None:
        given_names = [
            (child.text or "").strip()
            for child in name_elem.findall("hl7:given", NAMESPACES)
            if (child.text or "").strip()
        ]
        family_name = (name_elem.findtext("hl7:family", default="", namespaces=NAMESPACES) or "").strip()
        full_name = " ".join(part for part in given_names + ([family_name] if family_name else []) if part)
        patient["name"] = full_name or None

    return patient


def _extract_encounter(root: ET.Element) -> Dict[str, Optional[str]]:
    encounter: Dict[str, Optional[str]] = {"facility": None, "date": None}

    facility = _first_text(
        root,
        [
            ".//hl7:providerOrganization/hl7:name",
            ".//hl7:representedOrganization/hl7:name",
        ],
    )
    encounter["facility"] = facility or "Unknown Facility"

    effective_time = root.find(".//hl7:effectiveTime", NAMESPACES)
    if effective_time is not None:
        value = effective_time.get("value")
        if value:
            encounter["date"] = value[:8]
        else:
            low = effective_time.find("hl7:low", NAMESPACES)
            if low is not None and low.get("value"):
                encounter["date"] = low.get("value")[:8]

    return encounter


def _first_text(root: ET.Element, xpath_options: List[str]) -> Optional[str]:
    for xpath in xpath_options:
        element = root.find(xpath, NAMESPACES)
        if element is not None and (element.text or "").strip():
            return element.text.strip()
    return None


def _extract_medications(root: ET.Element) -> List[Dict[str, Optional[str]]]:
    medications: List[Dict[str, Optional[str]]] = []
    for med in root.findall(".//hl7:substanceAdministration", NAMESPACES):
        if med.get("classCode") and med.get("classCode").lower() == "immun":
            # Skip immunizations (common in CCDA but out of scope for med list).
            continue

        name = _extract_medication_name(med)
        if not name:
            continue

        dose_elem = med.find("hl7:doseQuantity", NAMESPACES)
        dose_value = dose_elem.get("value") if dose_elem is not None else None
        dose_unit = dose_elem.get("unit") if dose_elem is not None else None
        route_elem = med.find("hl7:routeCode", NAMESPACES)
        route = route_elem.get("displayName") if route_elem is not None else None

        medications.append(
            {
                "name": name,
                "dose": {
                    "value": dose_value,
                    "unit": dose_unit,
                } if dose_value or dose_unit else None,
                "route": route,
                "status": med.get("statusCode") or None,
            }
        )
    return medications


def _extract_medication_name(med_element: ET.Element) -> Optional[str]:
    # Common structures include manufacturedProduct manufacturedMaterial code/displayName
    name_elem = med_element.find(
        "hl7:consumable/hl7:manufacturedProduct/hl7:manufacturedMaterial/hl7:code",
        NAMESPACES,
    )
    if name_elem is not None:
        display = name_elem.get("displayName") or name_elem.get("code")
        if display:
            return display.strip()

    product_name_elem = med_element.find(
        "hl7:consumable/hl7:manufacturedProduct/hl7:manufacturedMaterial/hl7:name",
        NAMESPACES,
    )
    if product_name_elem is not None and (product_name_elem.text or "").strip():
        return product_name_elem.text.strip()

    fallback = med_element.find(
        "hl7:consumable/hl7:manufacturedProduct/hl7:manufacturedMaterial",
        NAMESPACES,
    )
    if fallback is not None:
        text_content = " ".join((fallback.text or "").split())
        if text_content:
            return text_content

    return None


def _extract_allergies(root: ET.Element) -> List[Dict[str, Optional[str]]]:
    allergies: List[Dict[str, Optional[str]]] = []

    allergy_section = None
    for section in root.findall(".//hl7:section", NAMESPACES):
        code_elem = section.find("hl7:code", NAMESPACES)
        if code_elem is not None and code_elem.get("code") == "48765-2":
            allergy_section = section
            break

    if allergy_section is None:
        return allergies

    for observation in allergy_section.findall(
        ".//hl7:observation[@classCode='OBS'][@moodCode='EVN']",
        NAMESPACES,
    ):
        substance = _extract_allergy_substance(observation)
        reaction = _extract_allergy_reaction(observation)
        severity = _extract_allergy_severity(observation)

        status_code = observation.find("hl7:statusCode", NAMESPACES)
        status = status_code.get("code") if status_code is not None else "active"

        allergies.append(
            {
                "substance": substance,
                "reaction": reaction,
                "severity": severity,
                "status": status,
            }
        )

    return allergies


def _extract_allergy_substance(observation: ET.Element) -> Optional[str]:
    participant = observation.find("hl7:participant/hl7:participantRole/hl7:playingEntity", NAMESPACES)
    if participant is not None:
        code_elem = participant.find("hl7:code", NAMESPACES)
        if code_elem is not None:
            candidate = code_elem.get("displayName") or code_elem.get("code")
            if candidate:
                return candidate.strip()
        name_elem = participant.find("hl7:name", NAMESPACES)
        if name_elem is not None and (name_elem.text or "").strip():
            return name_elem.text.strip()

    # value attribute is common for allergies
    value_elem = observation.find("hl7:value", NAMESPACES)
    if value_elem is not None:
        candidate = value_elem.get("displayName") or value_elem.get("code")
        if candidate:
            return candidate.strip()

    return None


def _extract_allergy_reaction(observation: ET.Element) -> Optional[str]:
    for entry in observation.findall("hl7:entryRelationship", NAMESPACES):
        reaction_obs = entry.find("hl7:observation", NAMESPACES)
        if reaction_obs is None:
            continue
        value_elem = reaction_obs.find("hl7:value", NAMESPACES)
        if value_elem is not None:
            candidate = value_elem.get("displayName") or value_elem.get("code")
            if candidate:
                return candidate.strip()
    return None


def _extract_allergy_severity(observation: ET.Element) -> Optional[str]:
    for nested_obs in observation.findall(".//hl7:observation", NAMESPACES):
        code_elem = nested_obs.find("hl7:code", NAMESPACES)
        if code_elem is not None and code_elem.get("code") == "SEV":
            value_elem = nested_obs.find("hl7:value", NAMESPACES)
            if value_elem is not None:
                candidate = value_elem.get("displayName") or value_elem.get("code")
                if candidate:
                    return candidate.strip()
    return None


def _load_local_file(path: str) -> Dict[str, Any]:
    """Parse a local CCDA file and return the normalized payload."""

    with open(path, "rb") as source:
        xml_bytes = source.read()
    root = ET.fromstring(xml_bytes)
    return _build_payload(root)


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a local CCDA XML file into the normalized JSON structure.",
    )
    parser.add_argument("path", help="Path to the CCDA XML file")
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to write the JSON payload. Prints to stdout if omitted.",
    )
    args = parser.parse_args()

    payload = _load_local_file(args.path)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as target:
            target.write(rendered)
        print(f"Wrote normalized payload to {args.output}")
    else:
        print(rendered)
