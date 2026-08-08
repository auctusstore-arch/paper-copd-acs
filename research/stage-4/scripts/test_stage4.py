#!/usr/bin/env python3
"""Stage 4 acceptance tests."""

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


class Stage4AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(REVISED) as archive:
            cls.document = ET.fromstring(archive.read("word/document.xml"))
        body = cls.document.find(W + "body")
        if body is None:
            raise AssertionError("word/document.xml has no w:body")
        cls.paragraphs = [child for child in body if child.tag == W + "p"]
        cls.text = "\n".join(accepted_text(paragraph) for paragraph in cls.paragraphs)

    def test_no_em_dashes_in_full_text(self):
        count = self.text.count("\u2014")
        self.assertEqual(0, count, f"Found {count} em-dashes in accepted text")

    def test_no_american_spellings(self):
        # Check body text only, excluding reference list (paper titles may use American spelling)
        # References are paragraphs starting with "N. " pattern
        body_paragraphs = []
        in_refs = False
        for p in self.paragraphs:
            text = accepted_text(p)
            if text.strip() == "References":
                in_refs = True
            if not in_refs and not re.match(r"^\d+\. ", text):
                body_paragraphs.append(text)
        body_text = "\n".join(body_paragraphs)
        american = ["randomized", "hypoxemia", "dyslipidemia", "hemoglobin"]
        for word in american:
            self.assertNotIn(word, body_text.lower(), f"American spelling in body: {word}")

    def test_rhetorical_tics_removed(self):
        tics = [
            "honesty requires",
            "clinical teeth",
            "central error",
            "answerable, and it has been answered",
        ]
        for tic in tics:
            self.assertNotIn(tic.lower(), self.text.lower(), f"Rhetorical tic found: {tic}")

    def test_keywords_present(self):
        self.assertIn("Keywords:", self.text)
        self.assertIn("type 2 myocardial infarction", self.text.lower())
        self.assertIn("self-controlled case series", self.text.lower())

    def test_front_matter_present(self):
        self.assertIn("Author contributions:", self.text)
        self.assertIn("Funding:", self.text)
        self.assertIn("Conflicts of interest:", self.text)
        self.assertIn("Use of artificial intelligence:", self.text)

    def test_figure_brief_present(self):
        self.assertIn("conceptual schematic", self.text.lower())

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

    def test_citation_bounds(self):
        citations = re.findall(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", self.text)
        max_ref = 0
        for c in citations:
            parts = re.split(r"\s*[-,]\s*", c)
            for p in parts:
                if p.strip().isdigit():
                    max_ref = max(max_ref, int(p.strip()))
        self.assertLessEqual(max_ref, 69)

    def test_british_english_present(self):
        self.assertIn("randomised", self.text.lower())
        self.assertIn("hypoxaemia", self.text.lower())


if __name__ == "__main__":
    unittest.main()