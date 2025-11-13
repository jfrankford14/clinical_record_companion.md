from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .ccda_parser import ParsedRecord, Medication, Allergy
from .knowledge_base import Interaction, AllergyLink


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


@dataclass
class UnifiedPatient:
    patient: Dict
    facilities: List[Dict]
    medications: List[Medication]
    allergies: List[Allergy]


def unify_records(records: List[ParsedRecord]) -> UnifiedPatient:
    patient = {}
    facilities = []
    meds: Dict[str, Medication] = {}
    allergies: Dict[str, Allergy] = {}

    for r in records:
        # Prefer earliest non-empty patient fields
        for k, v in r.patient.items():
            if v and not patient.get(k):
                patient[k] = v
        facilities.append(r.facility)
        for m in r.medications:
            key = _norm(m.name)
            # Keep the most active/most recent if duplicates
            cur = meds.get(key)
            if cur is None:
                meds[key] = m
            else:
                # Prefer active; otherwise keep the one with a start_date
                if (cur.status or "").lower() != "active" and (m.status or "").lower() == "active":
                    meds[key] = m
                elif not cur.start_date and m.start_date:
                    meds[key] = m
        for a in r.allergies:
            key = _norm(a.substance)
            if key not in allergies:
                allergies[key] = a

    return UnifiedPatient(
        patient=patient,
        facilities=facilities,
        medications=list(meds.values()),
        allergies=list(allergies.values()),
    )


def med_discrepancies(a: List[Medication], b: List[Medication]) -> Dict[str, List[Tuple[str, str]]]:
    # Returns dict with added, removed, changed (tuples: name, detail)
    map_a = { _norm(m.name): m for m in a }
    map_b = { _norm(m.name): m for m in b }

    added, removed, changed = [], [], []
    for k, mb in map_b.items():
        if k not in map_a:
            added.append((mb.name, (mb.dose or "")))
        else:
            ma = map_a[k]
            if (ma.dose or "") != (mb.dose or ""):
                changed.append((mb.name, f"dose {ma.dose or '?'} → {mb.dose or '?'}"))
    for k, ma in map_a.items():
        if k not in map_b:
            removed.append((ma.name, (ma.dose or "")))

    return {"added": added, "removed": removed, "changed": changed}


def find_interactions(meds: List[Medication], kb: List[Interaction]) -> List[Dict]:
    names = [_norm(m.name) for m in meds]
    out = []
    for inter in kb:
        if inter.a in names and inter.b in names:
            out.append({
                "pair": (inter.a, inter.b),
                "severity": inter.severity,
                "note": inter.note,
            })
    return out


def allergy_conflicts(allergies: List[Allergy], meds: List[Medication], crosswalk: List[AllergyLink]) -> List[Dict]:
    alset = {_norm(a.substance) for a in allergies}
    mset = {_norm(m.name) for m in meds}
    out = []
    for link in crosswalk:
        if link.substance in alset and link.drug in mset:
            out.append({
                "substance": link.substance,
                "drug": link.drug,
                "severity": link.severity,
            })
    return out


def summarize(unified: UnifiedPatient) -> str:
    meds = ", ".join(sorted({f"{m.name} {m.dose or ''}".strip() for m in unified.medications})) or "None"
    algs = ", ".join(sorted({a.substance for a in unified.allergies})) or "None"
    given = unified.patient.get("given") or ""
    family = unified.patient.get("family") or ""
    name = (given + " " + family).strip() or "Patient"
    return f"{name} current meds: {meds}. Known allergies: {algs}."


def handoff_summary(unified: UnifiedPatient, interactions: List[Dict], conflicts: List[Dict]) -> str:
    meds = ", ".join(sorted({m.name for m in unified.medications})) or "none"
    algs = ", ".join(sorted({a.substance for a in unified.allergies})) or "none"
    parts = [
        f"Unified view shows meds: {meds}; allergies: {algs}.",
    ]
    if interactions:
        top = "; ".join([f"{p['pair'][0]} x {p['pair'][1]} ({p['severity']})" for p in interactions])
        parts.append(f"Potential interactions: {top}.")
    if conflicts:
        top = "; ".join([f"{c['drug']} vs {c['substance']} ({c['severity']})" for c in conflicts])
        parts.append(f"Allergy-drug conflicts: {top}.")
    parts.append("Recommend verifying allergy status, reconciling meds, and updating chart.")
    return " ".join(parts)
