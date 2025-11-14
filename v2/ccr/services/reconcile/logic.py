from __future__ import annotations

import csv
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List


def _normalize_name(value: str | None) -> str:
    return (value or "").strip().lower()


def load_ddi_reference(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: List[Dict[str, str]] = []
        for row in reader:
            drug_a = (row.get("DrugA") or "").strip()
            drug_b = (row.get("DrugB") or "").strip()
            if not drug_a or not drug_b:
                continue
            rows.append(
                {
                    "drug_a": drug_a.lower(),
                    "drug_b": drug_b.lower(),
                    "severity": (row.get("Severity") or "unknown").strip(),
                    "note": (row.get("Note") or "").strip(),
                    "label_a": drug_a,
                    "label_b": drug_b,
                }
            )
        return rows


def merge_medications(a: Dict[str, object], b: Dict[str, object]) -> tuple[List[Dict[str, object]], Dict[str, List[str]]]:
    list_a = list(a.get("medications") or [])
    list_b = list(b.get("medications") or [])
    index: Dict[tuple[str, str], Dict[str, object]] = {}
    origins: Dict[tuple[str, str], List[str]] = {}
    for label, items in (("A", list_a), ("B", list_b)):
        for idx, entry in enumerate(items):
            code = _normalize_name(str(entry.get("rxnorm_code") or ""))
            name = _normalize_name(str(entry.get("name") or ""))
            key = (code, name or f"{label}_{idx}")
            candidate = index.get(key)
            if candidate is None:
                index[key] = dict(entry)
            else:
                index[key] = _prefer_recent(candidate, entry)
                index[key] = _fill_missing(index[key], entry)
            origins.setdefault(key, []).append(label)
    unified = [entry for _, entry in sorted(index.items(), key=lambda item: item[0][1])]
    only_in_a: List[str] = []
    only_in_b: List[str] = []
    for key, entry in index.items():
        labels = set(origins.get(key, []))
        if labels == {"A"}:
            only_in_a.append(entry.get("name") or "")
        elif labels == {"B"}:
            only_in_b.append(entry.get("name") or "")
    return unified, {"only_in_a": only_in_a, "only_in_b": only_in_b}


def merge_allergies(a: Dict[str, object], b: Dict[str, object]) -> List[Dict[str, object]]:
    list_a = list(a.get("allergies") or [])
    list_b = list(b.get("allergies") or [])
    index: Dict[tuple[str, str], Dict[str, object]] = {}
    for label, items in (("A", list_a), ("B", list_b)):
        for idx, entry in enumerate(items):
            code = _normalize_name(str(entry.get("code") or ""))
            name = _normalize_name(str(entry.get("substance") or ""))
            key = (code, name or f"{label}_{idx}")
            if key not in index:
                index[key] = dict(entry)
            else:
                index[key] = _fill_missing(index[key], entry)
    return [entry for _, entry in sorted(index.items(), key=lambda item: item[0][1])]


def detect_allergy_conflicts(allergies: Iterable[Dict[str, object]], meds: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    conflicts: List[Dict[str, object]] = []
    med_list = list(meds)
    for allergy in allergies:
        substance = _normalize_name(str(allergy.get("substance") or ""))
        if not substance:
            continue
        for med in med_list:
            med_name = _normalize_name(str(med.get("name") or ""))
            if substance and substance in med_name:
                conflicts.append(
                    {
                        "substance": allergy.get("substance"),
                        "linked_drug": med.get("name"),
                        "severity": allergy.get("severity"),
                        "reaction": allergy.get("reaction"),
                    }
                )
    return conflicts


def detect_ddi(meds: List[Dict[str, object]], rules: List[Dict[str, str]]) -> List[Dict[str, object]]:
    matches: List[Dict[str, object]] = []
    for med_a, med_b in combinations(meds, 2):
        name_a = _normalize_name(str(med_a.get("name") or ""))
        name_b = _normalize_name(str(med_b.get("name") or ""))
        if not name_a or not name_b:
            continue
        for rule in rules:
            drug_a = rule["drug_a"]
            drug_b = rule["drug_b"]
            if not drug_a or not drug_b:
                continue
            forward = drug_a in name_a and drug_b in name_b
            reverse = drug_a in name_b and drug_b in name_a
            if forward or reverse:
                matches.append(
                    {
                        "drug_a": med_a.get("name"),
                        "drug_b": med_b.get("name"),
                        "severity": rule["severity"],
                        "note": rule["note"],
                    }
                )
                break
    return matches


def build_discrepancies(med_delta: Dict[str, List[str]]) -> Dict[str, object]:
    return {
        "med_lists": {
            "only_in_a": med_delta.get("only_in_a", []),
            "only_in_b": med_delta.get("only_in_b", []),
        }
    }


def reconcile_records(record_a: Dict[str, object], record_b: Dict[str, object], rules: List[Dict[str, str]]) -> Dict[str, object]:
    unified_meds, med_delta = merge_medications(record_a, record_b)
    unified_allergies = merge_allergies(record_a, record_b)
    allergy_conflicts = detect_allergy_conflicts(unified_allergies, unified_meds)
    dd_interactions = detect_ddi(unified_meds, rules)
    return {
        "unified_meds": unified_meds,
        "unified_allergies": unified_allergies,
        "discrepancies": build_discrepancies(med_delta),
        "dd_interactions": dd_interactions,
        "allergy_conflicts": allergy_conflicts,
    }


def _prefer_recent(current: Dict[str, object], incoming: Dict[str, object]) -> Dict[str, object]:
    current_date = current.get("start_date") or ""
    incoming_date = incoming.get("start_date") or ""
    if incoming_date and incoming_date > current_date:
        return dict(incoming)
    return current


def _fill_missing(target: Dict[str, object], source: Dict[str, object]) -> Dict[str, object]:
    for key, value in source.items():
        if key not in target or target[key] in (None, ""):
            target[key] = value
    return target
