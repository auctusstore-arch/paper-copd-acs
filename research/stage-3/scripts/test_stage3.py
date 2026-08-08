#!/usr/bin/env python3
"""Stage 3 acceptance tests."""

import re
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
REVISED = ROOT / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review_REVISED.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def accepted_text(element):
    output = []
    def visit(node, deleted=False):
        deleted = deleted or node.tag == W + "del"
        if node.tag == W + "t" and not deleted:
            output.append(node.text or "")
        for child in node:
            visit(child, deleted)
    visit(element)
    return "".join(output)


class Stage3AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(REVISED) as archive:
            cls.document = ET.fromstring(archive.read("word/document.xml"))
        body = cls.document.find(W + "body")
        if body is None:
            raise AssertionError("word/document.xml has no w:body")
        cls.paragraphs = [child for child in body if child.tag == W + "p"]
        cls.text = "\n".join(accepted_text(paragraph) for paragraph in cls.paragraphs)

    def test_c5_sccs_bias_section(self):
        self.assertIn("detection bias", self.text.lower())
        self.assertIn("protopathic bias", self.text.lower())
        self.assertIn("time-varying confounding", self.text.lower())

    def test_m6_paf_section(self):
        self.assertIn("population attributable fraction", self.text.lower())
        self.assertIn("14.9", self.text)
        self.assertIn("25.1", self.text)

    def test_m4_statcope_non_sequitur_fixed(self):
        self.assertIn("circulation to lung", self.text.lower())

    def test_m5_summit_calibrated(self):
        self.assertIn("absence of evidence", self.text.lower())
        self.assertIn("0.75", self.text)

    def test_f1_framing_downgraded(self):
        self.assertIn("misplaced emphasis", self.text.lower())

    def test_m11_outcome_composition(self):
        self.assertIn("arrhythmia", self.text.lower())
        self.assertIn("pulmonary embolism", self.text)
        self.assertIn("16.1", self.text)

    def test_no_em_dashes_in_insertions(self):
        new_texts = []
        for p in self.paragraphs:
            for ins in p.findall(W + "ins"):
                text = accepted_text(ins)
                if text and len(text) > 50:
                    new_texts.append(text)
        for t in new_texts:
            self.assertNotIn("\u2014", t, f"Em-dash found in insertion: {t[:60]}...")

    def test_reference_count_is_69(self):
        refs = [
            accepted_text(paragraph)
            for paragraph in self.paragraphs
            if re.match(r"^\d+\. ", accepted_text(paragraph))
        ]
        sequential = []
        expected = 1
        for ref in refs:
            num = int(ref.split(".", 1)[0])
            if num == expected:
                sequential.append(num)
                expected += 1
        self.assertEqual(69, len(sequential))

    def test_new_refs_present(self):
        refs = [accepted_text(p) for p in self.paragraphs if re.match(r"^\d+\. ", accepted_text(p))]
        ref_text = " ".join(refs)
        self.assertIn("Aleva", ref_text)
        self.assertIn("Wallstr", ref_text)
        self.assertIn("Baethge", ref_text)
        self.assertIn("Heffernan", ref_text)

    def test_citation_bounds(self):
        citations = re.findall(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", self.text)
        max_ref = 0
        for c in citations:
            parts = re.split(r"\s*[-,]\s*", c)
            for p in parts:
                if p.strip().isdigit():
                    max_ref = max(max_ref, int(p.strip()))
        self.assertLessEqual(max_ref, 69)


if __name__ == "__main__":
    unittest.main()