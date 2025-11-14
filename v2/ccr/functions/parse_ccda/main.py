import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from google.cloud import storage
from lxml import etree

PARSED_BUCKET = os.getenv("PARSED_BUCKET")
_storage_client: storage.Client | None = None
NS = {
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

logger = logging.getLogger("parse_ccda_v2")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _log_event(event: str, **fields: object) -> None:
    log_payload = {"event": event, **fields}
    logger.info(json.dumps(log_payload))


def _client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client()
    return _storage_client


def _read(gcs_uri: str) -> str:
    if not gcs_uri.startswith("gs://"):
        raise ValueError("Expected gs:// URI")
    bucket_name, blob_path = gcs_uri[5:].split("/", 1)
    return _client().bucket(bucket_name).blob(blob_path).download_as_text()


def _write(gcs_uri: str, text: str, content_type: str = "application/json") -> None:
    bucket_name, blob_path = gcs_uri[5:].split("/", 1)
    _client().bucket(bucket_name).blob(blob_path).upload_from_string(text, content_type=content_type)


def _response_contract(out_uri: Optional[str], summary: Optional[Dict[str, int]] = None) -> Dict[str, object]:
    summary_payload = summary or {"med_count": 0, "allergy_count": 0, "problem_count": 0}
    return {
        "parsed_json_gcs": out_uri or "",
        "summary": summary_payload,
    }


def _output_uri_for_source(src: str) -> str:
    base_name = src.split("/")[-1].rsplit(".", 1)[0] + ".json"
    if PARSED_BUCKET:
        return f"gs://{PARSED_BUCKET}/{base_name}"
    bucket, _ = src[5:].split("/", 1)
    return f"gs://{bucket}/{base_name}"


def _parse_xml(xml_text: str) -> etree._Element:
    parser = etree.XMLParser(recover=True)
    return etree.fromstring(xml_text.encode("utf-8"), parser=parser)


def _find_section(root: etree._Element, code: str) -> Optional[etree._Element]:
    for section in root.findall(".//cda:section", namespaces=NS):
        code_el = section.find("cda:code", namespaces=NS)
        if code_el is not None and code_el.get("code") == code:
            return section
    return None


def _clean(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    stripped = text.strip()
    return stripped or None


def _normalize_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) < 8:
        return None
    return f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]}"


def _extract_period_text(entry: etree._Element) -> Optional[str]:
    period = entry.find("cda:effectiveTime/cda:period", namespaces=NS)
    if period is None:
        period = entry.find(".//cda:effectiveTime[@xsi:type='PIVL_TS']/cda:period", namespaces=NS)
    if period is None:
        return None
    value = period.get("value") or ""
    unit = period.get("unit") or ""
    return _clean(" ".join(part for part in [value, unit] if part))


def _extract_dates(effective_time: Optional[etree._Element]) -> Tuple[Optional[str], Optional[str]]:
    if effective_time is None:
        return (None, None)
    start = effective_time.find("cda:low", namespaces=NS)
    end = effective_time.find("cda:high", namespaces=NS)
    start_val = start.get("value") if start is not None else effective_time.get("value")
    end_val = end.get("value") if end is not None else None
    return _normalize_date(start_val), _normalize_date(end_val)


def _extract_medications(root: etree._Element) -> List[Dict[str, Optional[str]]]:
    section = _find_section(root, "10160-0")
    if section is None:
        return []
    medications: List[Dict[str, Optional[str]]] = []
    for entry in section.findall(".//cda:substanceAdministration", namespaces=NS):
        code_el = entry.find(".//cda:manufacturedMaterial/cda:code", namespaces=NS)
        name = (
            (code_el.get("displayName") if code_el is not None else None)
            or _clean(entry.findtext(".//cda:manufacturedMaterial/cda:name", namespaces=NS))
            or "Unknown medication"
        )
        rxnorm_code = code_el.get("code") if code_el is not None else None
        dose = entry.find("cda:doseQuantity", namespaces=NS)
        strength = None
        if dose is not None:
            value = dose.get("value") or ""
            unit = dose.get("unit") or ""
            strength = _clean(" ".join(part for part in [value, unit] if part))
        route_el = entry.find("cda:routeCode", namespaces=NS)
        route = None
        if route_el is not None:
            route = route_el.get("displayName") or route_el.get("code")
        frequency = _extract_period_text(entry)
        start_date, end_date = _extract_dates(entry.find("cda:effectiveTime", namespaces=NS))
        status_el = entry.find("cda:statusCode", namespaces=NS)
        status_val = (status_el.get("code") if status_el is not None else "") or "unknown"
        status_map = {
            "active": "active",
            "completed": "completed",
            "completed-withdrawn": "completed",
            "suspended": "completed",
        }
        status = status_map.get(status_val.lower(), "unknown")
        medications.append(
            {
                "rxnorm_code": _clean(rxnorm_code),
                "name": name,
                "strength": strength,
                "route": _clean(route),
                "frequency": frequency,
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
            }
        )
    return medications


def _extract_allergies(root: etree._Element) -> List[Dict[str, Optional[str]]]:
    section = _find_section(root, "48765-2")
    if section is None:
        return []
    allergies: List[Dict[str, Optional[str]]] = []
    for observation in section.findall(".//cda:observation", namespaces=NS):
        substance_el = observation.find(".//cda:participant//cda:code", namespaces=NS)
        code = substance_el.get("code") if substance_el is not None else None
        substance = (
            (substance_el.get("displayName") if substance_el is not None else None)
            or observation.findtext(".//cda:participant//cda:playingEntity/cda:name", namespaces=NS)
        )
        substance = _clean(substance)
        if not substance:
            continue
        reaction = observation.findtext(
            ".//cda:entryRelationship[@typeCode='MFST']//cda:text",
            namespaces=NS,
        )
        if not reaction:
            reaction = observation.findtext(
                ".//cda:entryRelationship[@typeCode='MFST']//cda:value",
                namespaces=NS,
            )
        severity = observation.findtext(
            ".//cda:entryRelationship[@typeCode='SUBJ']//cda:text",
            namespaces=NS,
        )
        if not severity:
            severity = observation.findtext(
                ".//cda:entryRelationship[@typeCode='SUBJ']//cda:value",
                namespaces=NS,
            )
        allergies.append(
            {
                "code": _clean(code),
                "substance": substance,
                "reaction": _clean(reaction),
                "severity": _clean(severity),
            }
        )
    return allergies


def _extract_problems(root: etree._Element) -> List[Dict[str, Optional[str]]]:
    section = _find_section(root, "11450-4")
    if section is None:
        return []
    problems: List[Dict[str, Optional[str]]] = []
    for observation in section.findall(".//cda:observation", namespaces=NS):
        code_el = observation.find("cda:value", namespaces=NS)
        description = None
        code_val = None
        if code_el is not None:
            description = code_el.get("displayName") or code_el.text
            code_val = code_el.get("code")
        description = _clean(description) or _clean(observation.findtext("cda:text", namespaces=NS))
        if not description:
            continue
        onset_date, _ = _extract_dates(observation.find("cda:effectiveTime", namespaces=NS))
        status_el = observation.find("cda:statusCode", namespaces=NS)
        status = _clean(status_el.get("code") if status_el is not None else None)
        problems.append(
            {
                "code": _clean(code_val),
                "description": description,
                "onset_date": onset_date,
                "status": status,
            }
        )
    return problems


def _extract_encounters(root: etree._Element) -> List[Dict[str, Optional[str]]]:
    section = _find_section(root, "46240-8")
    if section is None:
        return []
    encounters: List[Dict[str, Optional[str]]] = []
    type_map = {
        "emergency department": "ED",
        "inpatient": "Inpatient",
        "outpatient": "Outpatient",
        "laboratory": "Lab",
        "specialty clinic": "Specialty",
    }
    for encounter in section.findall(".//cda:encounter", namespaces=NS):
        effective = encounter.find("cda:effectiveTime", namespaces=NS)
        date, _ = _extract_dates(effective)
        facility = encounter.findtext(".//cda:participant//cda:name", namespaces=NS)
        code_el = encounter.find("cda:code", namespaces=NS)
        enc_type = None
        if code_el is not None:
            label = code_el.get("displayName") or code_el.text or ""
            enc_type = type_map.get(label.strip().lower(), None)
        encounters.append(
            {
                "date": date,
                "facility": _clean(facility),
                "type": enc_type or "unknown",
            }
        )
    return encounters


def _extract_labs(root: etree._Element) -> List[Dict[str, Optional[str]]]:
    section = _find_section(root, "30954-2")
    if section is None:
        return []
    labs: List[Dict[str, Optional[str]]] = []
    for observation in section.findall(".//cda:observation", namespaces=NS):
        code_el = observation.find("cda:code", namespaces=NS)
        loinc = code_el.get("code") if code_el is not None else None
        name = (code_el.get("displayName") if code_el is not None else None) or _clean(
            observation.findtext("cda:text", namespaces=NS)
        )
        if not name:
            continue
        value_el = observation.find("cda:value", namespaces=NS)
        value = None
        unit = None
        if value_el is not None:
            value = value_el.get("value") or value_el.text
            unit = value_el.get("unit")
        date, _ = _extract_dates(observation.find("cda:effectiveTime", namespaces=NS))
        labs.append(
            {
                "loinc": _clean(loinc),
                "name": name,
                "value": _clean(value),
                "unit": _clean(unit),
                "date": date,
            }
        )
    return labs


def build_parsed_document(xml_text: str, source_uri: str) -> Dict[str, object]:
    root = _parse_xml(xml_text)
    medications = _extract_medications(root)
    allergies = _extract_allergies(root)
    problems = _extract_problems(root)
    encounters = _extract_encounters(root)
    labs = _extract_labs(root)
    payload: Dict[str, object] = {
        "medications": medications,
        "allergies": allergies,
        "problems": problems,
        "encounters": encounters,
        "labs": labs,
        "provenance": {
            "source_document": {
                "gcs_uri": source_uri,
                "size_bytes": len(xml_text.encode("utf-8")),
                "parsed_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    }
    payload["summary"] = {
        "med_count": len(medications),
        "allergy_count": len(allergies),
        "problem_count": len(problems),
    }
    return payload


def parse_ccda(request):
    req = request.get_json(silent=True) or {}
    src = req.get("gcs_uri")
    if not src:
        _log_event("missing_gcs_uri")
        response = _response_contract(None)
        response["error"] = "missing gcs_uri"
        return (response, 400)

    out_uri = _output_uri_for_source(src)
    try:
        xml = _read(src)
        _log_event("download_success", source=src)
        payload = build_parsed_document(xml, src)
        _write(out_uri, json.dumps(payload, separators=(",", ":")))
        _log_event(
            "parse_success",
            source=src,
            destination=out_uri,
            med_count=payload["summary"]["med_count"],
            allergy_count=payload["summary"]["allergy_count"],
            problem_count=payload["summary"]["problem_count"],
        )
        return (_response_contract(out_uri, payload["summary"]), 200)
    except Exception as exc:  # noqa: BLE001
        _log_event("parse_failure", source=src, error=str(exc))
        response = _response_contract(None)
        response["error"] = "failed to parse document"
        return (response, 500)


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Parse a CCDA file locally.")
    parser.add_argument("--local-file", required=True, help="Path to the CCDA XML file")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()
    xml_text = Path(args.local_file).read_text(encoding="utf-8")
    payload = build_parsed_document(xml_text, f"file://{Path(args.local_file).resolve()}")
    serialized = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    else:
        print(serialized)


if __name__ == "__main__":
    _cli()
