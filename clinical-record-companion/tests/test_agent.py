import os
import sys
import unittest


# Ensure package is importable when running from repo root
PKG_ROOT = os.path.join(os.getcwd(), "clinical-record-companion")
if PKG_ROOT not in sys.path:
    sys.path.insert(0, PKG_ROOT)

from clinical_record_companion.ccda_parser import parse_many
from clinical_record_companion.insights import (
    unify_records,
    med_discrepancies,
    find_interactions,
    allergy_conflicts,
    summarize,
    handoff_summary,
)
from clinical_record_companion.knowledge_base import (
    load_interactions,
    load_allergy_crosswalk,
)


DATA_DIR = os.path.join("clinical-record-companion", "data")
REC_A = os.path.join(DATA_DIR, "synthetic", "record_a.xml")
REC_B = os.path.join(DATA_DIR, "synthetic", "record_b.xml")
KB = os.path.join(DATA_DIR, "reference", "MedicationKnowledgeBase.csv")
CW = os.path.join(DATA_DIR, "reference", "AllergyCrosswalk.csv")


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.records = parse_many([REC_A, REC_B])
        self.unified = unify_records(self.records)

    def test_summarize_mentions_penicillin(self):
        s = summarize(self.unified)
        self.assertIn("Penicillin", s)

    def test_discrepancies_added_removed(self):
        d = med_discrepancies(self.records[0].medications, self.records[1].medications)
        added_names = {name for name, _ in d["added"]}
        removed_names = {name for name, _ in d["removed"]}
        self.assertIn("Amoxicillin", added_names)
        self.assertIn("Warfarin", removed_names)

    def test_ddi_warfarin_amoxicillin(self):
        inter = load_interactions(KB)
        out = find_interactions(self.unified.medications, inter)
        pairs = {tuple(item["pair"]) for item in out}
        self.assertIn(("warfarin", "amoxicillin"), pairs)

    def test_allergy_conflict(self):
        cw = load_allergy_crosswalk(CW)
        out = allergy_conflicts(self.unified.allergies, self.unified.medications, cw)
        pairs = {(o["drug"], o["substance"]) for o in out}
        self.assertIn(("amoxicillin", "penicillin"), pairs)

    def test_handoff_plain_x_symbol(self):
        inter = load_interactions(KB)
        out = find_interactions(self.unified.medications, inter)
        note = handoff_summary(self.unified, out, [])
        self.assertIn(" x ", note)
        self.assertNotIn("×", note)


if __name__ == "__main__":
    unittest.main()

