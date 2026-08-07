#!/usr/bin/env python3
"""Stage 2 acceptance tests written before the integrated transformer."""

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


class Stage2AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(REVISED) as archive:
            cls.document = ET.fromstring(archive.read("word/document.xml"))
        body = cls.document.find(W + "body")
        if body is None:
            raise AssertionError("word/document.xml has no w:body")
        cls.paragraphs = [child for child in body if child.tag == W + "p"]
        cls.text = "\n".join(accepted_text(paragraph) for paragraph in cls.paragraphs)

    def test_m2_influenza_trial_evidence(self):
        self.assertIn("IAMI", self.text)
        self.assertIn("IVVE", self.text)
        self.assertIn("hazard ratio of 0.72", self.text)

    def test_c4_beta_blocker_trial_update(self):
        self.assertIn("BICS", self.text)
        self.assertIn("PACE", self.text)
        self.assertIn("BETAMI-DANBLOCK", self.text)

    def test_m3_pathway_specific_anti_inflammatory_evidence(self):
        self.assertIn("CANTOS", self.text)
        self.assertIn("CIRT", self.text)
        self.assertIn("LoDoCo2", self.text)

    def test_m1_trigger_precedent_limits_novelty(self):
        self.assertIn("Muller", self.text)
        self.assertIn("Mittleman and Mostofsky", self.text)
        self.assertIn("organising synthesis", self.text)

    def test_m9_m10_keep_lung_traits_distinct(self):
        self.assertIn("forced vital capacity", self.text)
        self.assertIn("conditioning on height", self.text)

    def test_final_reference_count_is_62(self):
        references = [
            accepted_text(paragraph)
            for paragraph in self.paragraphs
            if re.match(r"^\d+\. ", accepted_text(paragraph))
        ]
        # Only count references that are in sequential order (skip deleted old refs)
        sequential = []
        expected = 1
        for ref in references:
            num = int(ref.split(".", 1)[0])
            if num == expected:
                sequential.append(ref)
                expected += 1
        self.assertEqual(62, len(sequential))
        self.assertEqual(list(range(1, 63)), [int(text.split(".", 1)[0]) for text in sequential])


if __name__ == "__main__":
    unittest.main()
