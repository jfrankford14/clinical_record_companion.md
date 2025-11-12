from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class Interaction:
    a: str
    b: str
    severity: str
    note: str


def load_interactions(path: str) -> List[Interaction]:
    out: List[Interaction] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            a = (row.get("DrugName") or "").strip()
            b = (row.get("InteractionPair") or "").strip()
            if not a or not b:
                continue
            sev = (row.get("Severity") or "").strip() or "Unknown"
            note = (row.get("Note") or "").strip()
            out.append(Interaction(a=a.lower(), b=b.lower(), severity=sev, note=note))
    return out


@dataclass(frozen=True)
class AllergyLink:
    substance: str
    drug: str
    severity: str


def load_allergy_crosswalk(path: str) -> List[AllergyLink]:
    out: List[AllergyLink] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sub = (row.get("Substance") or "").strip()
            drug = (row.get("AssociatedDrug") or "").strip()
            if not sub or not drug:
                continue
            sev = (row.get("Severity") or "").strip() or "Unknown"
            out.append(AllergyLink(substance=sub.lower(), drug=drug.lower(), severity=sev))
    return out

