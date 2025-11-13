from __future__ import annotations

import datetime as _dt
import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET


def _text(el: Optional[ET.Element]) -> str:
    return (el.text or "").strip() if el is not None else ""


def _attr(el: Optional[ET.Element], name: str) -> str:
    return el.get(name, "") if el is not None else ""


def _norm_med_name(name: str) -> str:
    return " ".join(name.lower().split())


def _parse_date(value: str) -> Optional[str]:
    # Accept YYYYMMDD or YYYY-MM-DD; return ISO YYYY-MM-DD
    if not value:
        return None
    v = value.strip()
    try:
        if len(v) == 8 and v.isdigit():
            return _dt.datetime.strptime(v, "%Y%m%d").date().isoformat()
        return _dt.date.fromisoformat(v).isoformat()
    except Exception:
        return None


@dataclass
class Medication:
    name: str
    dose: Optional[str] = None
    route: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    source_facility: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class Allergy:
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    type: Optional[str] = None
    source_facility: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class ParsedRecord:
    patient: Dict[str, Any]
    facility: Dict[str, Any]
    medications: List[Medication]
    allergies: List[Allergy]
    problems: List[Dict[str, Any]]
    source_file: str

    def to_json(self) -> Dict[str, Any]:
        return {
            "patient": self.patient,
            "facility": self.facility,
            "medications": [asdict(m) for m in self.medications],
            "allergies": [asdict(a) for a in self.allergies],
            "problems": self.problems,
            "source_file": self.source_file,
        }


def parse_ccda(xml_path: str) -> ParsedRecord:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Facility (look under author/assignedAuthor/representedOrganization or custodian)
    fac_el = root.find(".//author/assignedAuthor/representedOrganization")
    if fac_el is None:
        fac_el = root.find(".//custodian/assignedCustodian/representedCustodianOrganization")
    facility = {
        "id": _attr(fac_el.find("id"), "root") if fac_el is not None else "",
        "name": _text(fac_el.find("name")) if fac_el is not None else "",
    }

    # Patient (simple demo fields)
    patient_el = root.find(".//recordTarget/patientRole/patient")
    name_el = patient_el.find("name") if patient_el is not None else None
    patient = {
        "given": _text(name_el.find("given")) if name_el is not None else "",
        "family": _text(name_el.find("family")) if name_el is not None else "",
        "birthDate": _attr(patient_el.find("birthTime"), "value") if patient_el is not None else "",
        "gender": _attr(patient_el.find("administrativeGenderCode"), "code") if patient_el is not None else "",
    }

    # Medications
    meds: List[Medication] = []
    for sec in root.findall(".//component/section"):
        code = sec.find("code")
        code_val = _attr(code, "code")
        title = _text(sec.find("title")).lower()
        is_med = code_val == "10160-0" or "medication" in title
        is_allergy = code_val == "48765-2" or "allerg" in title
        is_problem = code_val == "11450-4" or "problem" in title

        if is_med:
            for entry in sec.findall("entry"):
                sa = entry.find("substanceAdministration")
                if sa is None:
                    continue
                name_el = sa.find(".//manufacturedLabeledDrug/name")
                name = _text(name_el)
                if not name:
                    continue
                dose_el = sa.find("doseQuantity")
                dose = _attr(dose_el, "value")
                route = _attr(sa.find("routeCode"), "code")
                status = _attr(sa.find("statusCode"), "code")
                start = _parse_date(_attr(sa.find("effectiveTime/low"), "value"))
                end = _parse_date(_attr(sa.find("effectiveTime/high"), "value"))
                meds.append(
                    Medication(
                        name=name,
                        dose=dose,
                        route=route,
                        status=status or "active",
                        start_date=start,
                        end_date=end,
                        source_facility=facility.get("id") or facility.get("name"),
                        source_file=os.path.basename(xml_path),
                    )
                )

    # Allergies
    allergies: List[Allergy] = []
    for sec in root.findall(".//component/section"):
        code = sec.find("code")
        code_val = _attr(code, "code")
        title = _text(sec.find("title")).lower()
        is_allergy = code_val == "48765-2" or "allerg" in title
        if is_allergy:
            for entry in sec.findall("entry"):
                obs = entry.find("observation")
                if obs is None:
                    continue
                typ = _attr(obs.find("value"), "code")
                # Substance name variations
                code_el = obs.find(".//participantRole/playingEntity/code")
                sub = _attr(code_el, "displayName") or _text(
                    obs.find(".//participantRole/playingEntity/name")
                )
                reaction = _text(obs.find(".//entryRelationship/observation/text"))
                sev = _text(obs.find(".//severity/translation/displayName")) or _attr(
                    obs.find(".//interpretationCode"), "displayName"
                )
                if sub:
                    allergies.append(
                        Allergy(
                            substance=sub,
                            reaction=reaction or None,
                            severity=sev or None,
                            type=typ or None,
                            source_facility=facility.get("id") or facility.get("name"),
                            source_file=os.path.basename(xml_path),
                        )
                    )

    # Problems (optional, minimal)
    problems: List[Dict[str, Any]] = []
    for sec in root.findall(".//component/section"):
        code = sec.find("code")
        code_val = _attr(code, "code")
        title = _text(sec.find("title")).lower()
        is_problem = code_val == "11450-4" or "problem" in title or "diagnos" in title
        if is_problem:
            for entry in sec.findall("entry"):
                obs = entry.find("observation")
                if obs is None:
                    continue
                name = _text(obs.find(".//value")) or _text(obs.find(".//text"))
                problems.append({
                    "name": name,
                    "source_facility": facility.get("id") or facility.get("name"),
                    "source_file": os.path.basename(xml_path),
                })

    return ParsedRecord(
        patient=patient,
        facility=facility,
        medications=meds,
        allergies=allergies,
        problems=problems,
        source_file=os.path.basename(xml_path),
    )


def parse_many(paths: List[str]) -> List[ParsedRecord]:
    return [parse_ccda(p) for p in paths]


def dumps_pretty(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
