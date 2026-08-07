#!/usr/bin/env python3
"""Regression tests for the Stage 1 tracked-change DOCX."""

import hashlib
import json
import subprocess
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
STAGE = REPO / "research" / "stage-1"
SOURCE = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx"
REVISED = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review_REVISED.docx"
EXPECTED_SOURCE_HASH = "8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_text(root):
    values = []
    for node in root.iter():
        if node.tag == W + "del":
            continue
        if node.tag == W + "t":
            values.append(node.text or "")
    return "".join(values)


class Stage1DocxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            ["uv", "run", "python3", str(STAGE / "scripts" / "apply_stage1.py")],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_source_is_byte_identical(self):
        self.assertEqual(EXPECTED_SOURCE_HASH, sha256(SOURCE))

    def test_package_preserves_original_parts_and_image(self):
        with zipfile.ZipFile(SOURCE) as original, zipfile.ZipFile(REVISED) as revised:
            self.assertEqual(set(original.namelist()) | {"word/media/image2.png"}, set(revised.namelist()))
            excluded = {"word/document.xml", "word/settings.xml", "word/_rels/document.xml.rels"}
            for name in original.namelist():
                if name not in excluded:
                    self.assertEqual(original.read(name), revised.read(name), name)
            expected_figure = (STAGE / "assets" / "central-illustration-stage1.png").read_bytes()
            self.assertEqual(original.read("word/media/image1.png"), revised.read("word/media/image1.png"))
            self.assertEqual(expected_figure, revised.read("word/media/image2.png"))

    def test_tracked_changes_and_track_revisions_setting_exist(self):
        with zipfile.ZipFile(REVISED) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            settings = ET.fromstring(archive.read("word/settings.xml"))
        self.assertGreater(len(document.findall(".//" + W + "ins")), 0)
        self.assertGreater(len(document.findall(".//" + W + "del")), 0)
        track_revisions = settings.find(W + "trackRevisions")
        self.assertIsNotNone(track_revisions)
        self.assertNotIn((track_revisions.get(W + "val") or "true").lower(), {"0", "false", "off", "no"})

    def test_accepted_text_contains_integrity_corrections(self):
        with zipfile.ZipFile(REVISED) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
        text = accepted_text(document)
        self.assertIn("retained nominal significance in separate models including body mass index", text)
        self.assertIn("cannot be interpreted as a patient-level odds ratio", text)
        self.assertIn("Wielscher et al.", text)
        self.assertIn("Zhu et al.", text)
        self.assertIn("p<5×10⁻⁶", text)
        self.assertIn("10.227 (95% confidence interval 1.889-55.363)", text)
        self.assertIn("odds ratio 0.72 (0.63-0.82)", text)
        self.assertIn("FEV1 estimate was 0.95 (0.75-1.19)", text)
        self.assertIn("DETO2X-AMI subgroup", text)
        self.assertNotIn("[to be verified]", text)
        self.assertNotIn("[to be completed]", text)

    def test_reference_count_and_inserted_prose_constraints(self):
        with zipfile.ZipFile(REVISED) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
        body = document.find(W + "body")
        if body is None:
            self.fail("word/document.xml has no w:body")
        paragraphs = [child for child in list(body) if child.tag == W + "p"]
        reference_texts = [accepted_text(paragraph) for paragraph in paragraphs[90:134]]
        self.assertEqual(44, len(reference_texts))
        self.assertTrue(reference_texts[0].startswith("Agustí A"))
        self.assertTrue(reference_texts[-1].startswith("Leong P"))
        for paragraph in paragraphs[126:134]:
            marker = paragraph.find(W + "pPr/" + W + "rPr/" + W + "ins")
            self.assertIsNotNone(marker)
            self.assertEqual("auctusstore-arch", marker.get(W + "author"))
        revisions = json.loads((STAGE / "revisions.json").read_text(encoding="utf-8"))
        inserted = "\n".join(revisions["paragraph_replacements"].values())
        inserted += "\n" + "\n".join(revisions["table_replacements"].values())
        self.assertNotIn("—", inserted)
        self.assertNotRegex(inserted, r"\[(?:to be verified|to be completed)\]")

    def test_verifier_rejects_removed_image(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "missing-image.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    if info.filename != "word/media/image1.png":
                        output.writestr(info, source.read(info.filename))
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)],
                cwd=REPO,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("image1.png", result.stderr)

    def test_verifier_rejects_disabled_track_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "no-track-setting.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/settings.xml":
                        settings = ET.fromstring(data)
                        track = settings.find(W + "trackRevisions")
                        if track is not None:
                            settings.remove(track)
                        data = ET.tostring(settings, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)],
                cwd=REPO,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("trackRevisions", result.stderr)

    def test_figure_drawing_relationship_is_live(self):
        with zipfile.ZipFile(REVISED) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        targets = {relationship.get("Id"): relationship.get("Target") for relationship in relationships}
        deleted_ids = {
            blip.get(R + "embed")
            for deletion in document.findall(".//" + W + "del")
            for blip in deletion.findall(".//" + A + "blip")
        }
        inserted_ids = {
            blip.get(R + "embed")
            for insertion in document.findall(".//" + W + "ins")
            for blip in insertion.findall(".//" + A + "blip")
        }
        self.assertIn("media/image1.png", {targets.get(value) for value in deleted_ids})
        self.assertIn("media/image2.png", {targets.get(value) for value in inserted_ids})

    def test_verifier_rejects_explicitly_false_track_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "track-false.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/settings.xml":
                        settings = ET.fromstring(data)
                        track = settings.find(W + "trackRevisions")
                        if track is None:
                            self.fail("Generated manuscript has no trackRevisions setting")
                        track.set(W + "val", "false")
                        data = ET.tostring(settings, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)],
                cwd=REPO,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("explicitly disabled", result.stderr)

    def test_verifier_rejects_corrupted_unchanged_paragraph(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "corrupt-paragraph.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/document.xml":
                        document = ET.fromstring(data)
                        body = document.find(W + "body")
                        if body is None:
                            self.fail("word/document.xml has no body")
                        paragraphs = [child for child in body if child.tag == W + "p"]
                        text_node = paragraphs[14].find(".//" + W + "t")
                        if text_node is None:
                            self.fail("Fixture paragraph has no text")
                        text_node.text = "CORRUPTED " + (text_node.text or "")
                        data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Accepted direct paragraph 14", result.stderr)

    def test_verifier_rejects_corrupted_table_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "corrupt-table.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/document.xml":
                        document = ET.fromstring(data)
                        table = document.findall(".//" + W + "tbl")[0]
                        paragraph = table.findall(W + "tr")[4].findall(W + "tc")[1].find(W + "p")
                        if paragraph is None:
                            self.fail("Fixture table paragraph is missing")
                        text_node = paragraph.find(".//" + W + "ins/" + W + "r/" + W + "t")
                        if text_node is None:
                            self.fail("Fixture table insertion is missing")
                        text_node.text = "CORRUPTED " + (text_node.text or "")
                        data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Accepted table paragraph differs", result.stderr)

    def test_verifier_rejects_invalid_revision_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "bad-revision-metadata.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/document.xml":
                        document = ET.fromstring(data)
                        revision = document.find(".//" + W + "ins")
                        if revision is None:
                            self.fail("Fixture has no tracked insertion")
                        revision.set(W + "id", "not-a-number")
                        revision.set(W + "date", "not-a-date")
                        data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("invalid date", result.stderr)
            self.assertIn("not a decimal", result.stderr)

    def test_verifier_rejects_corrupted_run_formatting(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "corrupt-formatting.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/document.xml":
                        document = ET.fromstring(data)
                        body = document.find(W + "body")
                        if body is None:
                            self.fail("word/document.xml has no body")
                        paragraph = [child for child in body if child.tag == W + "p"][14]
                        run = paragraph.find(W + "r")
                        if run is None:
                            self.fail("Fixture paragraph has no run")
                        properties = run.find(W + "rPr")
                        if properties is None:
                            properties = ET.Element(W + "rPr")
                            run.insert(0, properties)
                        properties.append(ET.Element(W + "b"))
                        data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("run formatting", result.stderr)

    def test_verifier_rejects_corrupted_deleted_drawing(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "corrupt-drawing.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/document.xml":
                        document = ET.fromstring(data)
                        extent = None
                        for deletion in document.findall(".//" + W + "del"):
                            candidate = deletion.find(".//" + WP + "extent")
                            if candidate is not None:
                                extent = candidate
                                break
                        if extent is None:
                            self.fail("Tracked source drawing extent is missing")
                        extent.set("cx", "1")
                        data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("differs structurally", result.stderr)

    def test_verifier_rejects_invalid_replacement_relationship_type(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "bad-image-relationship.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/_rels/document.xml.rels":
                        relationships = ET.fromstring(data)
                        replacement = next(
                            (node for node in relationships if node.get("Target") == "media/image2.png"), None
                        )
                        if replacement is None:
                            self.fail("Replacement image relationship is missing")
                        replacement.set("Type", "urn:not-an-image")
                        data = ET.tostring(relationships, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)], cwd=REPO,
                capture_output=True, text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("invalid attributes", result.stderr)

    def test_generator_is_byte_deterministic(self):
        first = REVISED.read_bytes()
        time.sleep(2.1)
        subprocess.run(
            ["uv", "run", "python3", str(STAGE / "scripts" / "apply_stage1.py")],
            cwd=REPO, check=True, capture_output=True, text=True,
        )
        self.assertEqual(first, REVISED.read_bytes())

    def test_verifier_rejects_detached_figure_relationship(self):
        with tempfile.TemporaryDirectory() as directory:
            corrupted = Path(directory) / "detached-figure.docx"
            with zipfile.ZipFile(REVISED) as source, zipfile.ZipFile(corrupted, "w") as output:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "word/_rels/document.xml.rels":
                        relationships = ET.fromstring(data)
                        for relationship in relationships:
                            if relationship.get("Target", "").lstrip("/") == "media/image1.png":
                                relationship.set("Target", "media/detached.png")
                        data = ET.tostring(relationships, encoding="utf-8", xml_declaration=True)
                    output.writestr(info, data)
            result = subprocess.run(
                ["uv", "run", "python3", str(STAGE / "scripts" / "verify_stage1.py"),
                 "--offline", "--revised", str(corrupted)],
                cwd=REPO,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("tracked deletion", result.stderr)


if __name__ == "__main__":
    unittest.main()
