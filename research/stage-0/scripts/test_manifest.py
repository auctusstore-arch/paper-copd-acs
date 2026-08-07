#!/usr/bin/env python3
"""Regression tests for Stage 0 manifest audit failures."""

import csv
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE_ROOT = SCRIPT_DIR.parent
SPEC = importlib.util.spec_from_file_location("verify_manifest", SCRIPT_DIR / "verify_manifest.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load verify_manifest.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class ManifestAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "stage-0"
        shutil.copytree(STAGE_ROOT, self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def rewrite_rows(self, mutate):
        manifest = self.root / "verification-manifest.tsv"
        with manifest.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            rows = list(reader)
            fields = list(reader.fieldnames or [])
        rows = mutate(rows)
        with manifest.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def issue_names(self):
        return {next(iter(issue)) for issue in VERIFY.local_issues(self.root)}

    def test_current_artifacts_pass_local_audit(self):
        self.assertEqual([], VERIFY.local_issues(self.root))

    def test_rejects_garbage_citation(self):
        def mutate(rows):
            next(row for row in rows if row["doi"])["citation"] = "garbage"
            return rows

        self.rewrite_rows(mutate)
        self.assertIn("citation_title_mismatch", self.issue_names())

    def test_rejects_nonexistent_source_file(self):
        def mutate(rows):
            next(row for row in rows if row["doi"])["source_file"] = "nonexistent.md"
            return rows

        self.rewrite_rows(mutate)
        names = self.issue_names()
        self.assertIn("nonexistent_source_file", names)
        self.assertIn("source_provenance_mismatch", names)

    def test_rejects_missing_gold_record(self):
        self.rewrite_rows(lambda rows: [row for row in rows if row["resolved_title"] != VERIFY.GOLD_TITLE])
        self.assertIn("gold_row_count", self.issue_names())

    def test_rejects_wrong_pmcid_from_pubmed(self):
        row = {
            "citation": "Example title.",
            "resolved_title": "Example title",
            "doi": "10.1/example",
            "pmid": "1",
            "pmcid": "PMC999",
        }
        item = {
            "title": "Example title.",
            "articleids": [
                {"idtype": "doi", "value": "10.1/example"},
                {"idtype": "pmc", "value": "PMC123"},
            ],
        }
        names = {next(iter(issue)) for issue in VERIFY.pubmed_row_issues(row, item)}
        self.assertIn("pmcid_pmid_mismatch", names)


if __name__ == "__main__":
    unittest.main()
