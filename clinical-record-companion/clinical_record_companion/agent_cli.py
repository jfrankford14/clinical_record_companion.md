from __future__ import annotations

import argparse
import sys
from typing import List

from .ccda_parser import parse_many, dumps_pretty
from .knowledge_base import load_interactions, load_allergy_crosswalk
from .insights import unify_records, med_discrepancies, find_interactions, allergy_conflicts, summarize, handoff_summary
import json, os


def _load_records(paths: List[str]):
    if not paths:
        print("No record paths provided", file=sys.stderr)
        sys.exit(2)
    return parse_many(paths)


def cmd_summarize(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    unified = unify_records(records)
    print(summarize(unified))


def cmd_discrepancies(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    if len(records) < 2:
        print("Provide at least two records to compare", file=sys.stderr)
        sys.exit(2)
    d = med_discrepancies(records[0].medications, records[1].medications)
    print(dumps_pretty(d))


def cmd_interactions(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    kb = load_interactions(args.kb)
    unified = unify_records(records)
    out = find_interactions(unified.medications, kb)
    print(dumps_pretty(out))


def cmd_conflicts(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    cross = load_allergy_crosswalk(args.crosswalk)
    unified = unify_records(records)
    out = allergy_conflicts(unified.allergies, unified.medications, cross)
    print(dumps_pretty(out))


def cmd_handoff(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    unified = unify_records(records)
    interactions = []
    conflicts = []
    if args.kb:
        interactions = find_interactions(unified.medications, load_interactions(args.kb))
    if args.crosswalk:
        conflicts = allergy_conflicts(unified.allergies, unified.medications, load_allergy_crosswalk(args.crosswalk))
    print(handoff_summary(unified, interactions, conflicts))


def cmd_export(args: argparse.Namespace) -> None:
    records = _load_records(args.records)
    unified = unify_records(records)

    kb = load_interactions(args.kb) if args.kb else []
    cross = load_allergy_crosswalk(args.crosswalk) if args.crosswalk else []

    interactions = find_interactions(unified.medications, kb) if kb else []
    conflicts = allergy_conflicts(unified.allergies, unified.medications, cross) if cross else []

    discrepancies = {}
    if len(records) >= 2:
        discrepancies = med_discrepancies(records[0].medications, records[1].medications)

    outdir = args.out or "exports"
    os.makedirs(outdir, exist_ok=True)

    payloads = {
        "records_parsed.json": [r.to_json() for r in records],
        "unified.json": {
            "patient": unified.patient,
            "facilities": unified.facilities,
            "medications": [m.__dict__ for m in unified.medications],
            "allergies": [a.__dict__ for a in unified.allergies],
        },
        "discrepancies.json": discrepancies,
        "interactions.json": interactions,
        "conflicts.json": conflicts,
        "handoff.md": handoff_summary(unified, interactions, conflicts),
    }

    for name, obj in payloads.items():
        path = os.path.join(outdir, name)
        if name.endswith(".md"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(obj))
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2, ensure_ascii=False)

    # Create NDJSON for Vertex AI Search style ingestion
    ndjson_path = os.path.join(outdir, "search_docs.ndjson")
    with open(ndjson_path, "w", encoding="utf-8") as f:
        # One document per section for simple grounding
        doc_id_prefix = "mary-thompson-demo"
        # Meds
        meds_text = ", ".join(sorted({f"{m.name} {m.dose or ''}".strip() for m in unified.medications}))
        f.write(json.dumps({
            "id": f"{doc_id_prefix}-meds",
            "section": "medications",
            "text": f"Current medications: {meds_text}",
            "source": "synthetic-ccda",
        }, ensure_ascii=False) + "\n")
        # Allergies
        algs_text = ", ".join(sorted({a.substance for a in unified.allergies})) or "None"
        f.write(json.dumps({
            "id": f"{doc_id_prefix}-allergies",
            "section": "allergies",
            "text": f"Known allergies: {algs_text}",
            "source": "synthetic-ccda",
        }, ensure_ascii=False) + "\n")
        # Discrepancies
        if discrepancies:
            f.write(json.dumps({
                "id": f"{doc_id_prefix}-discrepancies",
                "section": "discrepancies",
                "text": json.dumps(discrepancies, ensure_ascii=False),
                "source": "synthetic-ccda",
            }, ensure_ascii=False) + "\n")
        # Interactions
        if interactions:
            f.write(json.dumps({
                "id": f"{doc_id_prefix}-interactions",
                "section": "interactions",
                "text": json.dumps(interactions, ensure_ascii=False),
                "source": "local-kb",
            }, ensure_ascii=False) + "\n")
        # Conflicts
        if conflicts:
            f.write(json.dumps({
                "id": f"{doc_id_prefix}-conflicts",
                "section": "allergy_conflicts",
                "text": json.dumps(conflicts, ensure_ascii=False),
                "source": "local-crosswalk",
            }, ensure_ascii=False) + "\n")

    print(f"Wrote extracts to: {os.path.abspath(outdir)}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="clinical-record-companion")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("summarize", help="Summarize unified meds/allergies")
    s.add_argument("--records", nargs="+", required=True)
    s.set_defaults(func=cmd_summarize)

    s = sub.add_parser("discrepancies", help="Compare med lists (A vs B)")
    s.add_argument("--records", nargs="+", required=True)
    s.set_defaults(func=cmd_discrepancies)

    s = sub.add_parser("interactions", help="List potential DDIs from local KB")
    s.add_argument("--records", nargs="+", required=True)
    s.add_argument("--kb", required=True)
    s.set_defaults(func=cmd_interactions)

    s = sub.add_parser("conflicts", help="Find allergy–drug conflicts")
    s.add_argument("--records", nargs="+", required=True)
    s.add_argument("--crosswalk", required=True)
    s.set_defaults(func=cmd_conflicts)

    s = sub.add_parser("handoff", help="Generate one-paragraph handoff summary")
    s.add_argument("--records", nargs="+", required=True)
    s.add_argument("--kb")
    s.add_argument("--crosswalk")
    s.set_defaults(func=cmd_handoff)

    s = sub.add_parser("export", help="Write JSON/NDJSON extracts for Vertex AI grounding")
    s.add_argument("--records", nargs="+", required=True)
    s.add_argument("--kb")
    s.add_argument("--crosswalk")
    s.add_argument("--out")
    s.set_defaults(func=cmd_export)

    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
