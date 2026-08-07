#!/usr/bin/env python3
"""Fail when Stage 0 evidence and its manifest are not audit-ready."""

import csv
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    "citation",
    "resolved_title",
    "doi",
    "pmid",
    "pmcid",
    "source_file",
    "verification_basis",
    "full_text_status",
    "verified_on",
]
GOLD_URL = "https://goldcopd.org/2025-gold-report/"
GOLD_TITLE = "2025 GOLD Report"


def normalize(value):
    value = value.replace("β", "beta").replace("Β", "beta")
    value = unicodedata.normalize("NFKD", value)
    return "".join(character.lower() for character in value if character.isalnum())


def load_manifest(root):
    manifest = root / "verification-manifest.tsv"
    with manifest.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return manifest, reader.fieldnames, rows


def evidence_index(root):
    files = sorted(root.glob("*.md"))
    texts = {path.name: path.read_text(encoding="utf-8") for path in files}
    doi_files = defaultdict(set)
    pmids = set()
    for filename, text in texts.items():
        for doi in re.findall(r"https://doi\.org/(\S+)", text):
            doi_files[doi.rstrip(".,;")].add(filename)
        pmids.update(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/", text))
    return texts, doi_files, pmids


def local_issues(root):
    root = Path(root)
    manifest, fieldnames, rows = load_manifest(root)
    texts, doi_files, document_pmids = evidence_index(root)
    text = "\n".join(texts.values())
    issues = []

    if fieldnames != FIELDS:
        issues.append({"manifest_schema": {"expected": FIELDS, "actual": fieldnames}})
        return issues

    manifest_dois = [row["doi"] for row in rows if row["doi"]]
    manifest_pmids = [row["pmid"] for row in rows if row["pmid"]]
    for label, values in (("duplicate_doi", manifest_dois), ("duplicate_pmid", manifest_pmids)):
        duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
        if duplicates:
            issues.append({label: duplicates})

    document_dois = set(doi_files)
    for label, document_values, manifest_values in (
        ("doi", document_dois, set(manifest_dois)),
        ("pmid", document_pmids, set(manifest_pmids)),
    ):
        if document_values - manifest_values:
            issues.append({f"{label}_missing_from_manifest": sorted(document_values - manifest_values)})
        if manifest_values - document_values:
            issues.append({f"{label}_missing_from_evidence": sorted(manifest_values - document_values)})

    gold_rows = [row for row in rows if row["resolved_title"] == GOLD_TITLE]
    if len(gold_rows) != 1:
        issues.append({"gold_row_count": len(gold_rows)})
    else:
        gold = gold_rows[0]
        if gold["source_file"] != "03-triggers-diagnostics-guidelines.md":
            issues.append({"gold_source_file": gold["source_file"]})
        if GOLD_URL not in gold["verification_basis"]:
            issues.append({"gold_official_url_missing": True})
        if GOLD_URL not in texts.get(gold["source_file"], ""):
            issues.append({"gold_evidence_link_missing": True})

    for row_number, row in enumerate(rows, 2):
        if not all(row[field] for field in ("citation", "resolved_title", "source_file", "verification_basis", "full_text_status", "verified_on")):
            issues.append({"incomplete_manifest_row": row_number})
        source_files = set(filter(None, row["source_file"].split(";")))
        missing_files = sorted(filename for filename in source_files if filename not in texts)
        if missing_files:
            issues.append({"nonexistent_source_file": {"row": row_number, "files": missing_files}})
        if row["doi"]:
            expected_files = doi_files.get(row["doi"], set())
            if source_files != expected_files:
                issues.append(
                    {
                        "source_provenance_mismatch": {
                            "row": row_number,
                            "expected": sorted(expected_files),
                            "actual": sorted(source_files),
                        }
                    }
                )
            if normalize(row["resolved_title"]) not in normalize(row["citation"]):
                issues.append({"citation_title_mismatch": row_number})
        elif row["resolved_title"] != GOLD_TITLE:
            issues.append({"unsupported_identifier_free_row": row_number})

    checks = {
        "em_dash": text.count("—"),
        "incomplete_markers": len(re.findall(r"\[(?:to be verified|to be completed)\]", text, re.I)),
        "placeholders": len(re.findall(r"\b(?:TBD|TODO|xxx)\b", text, re.I)),
    }
    issues.extend({label: count} for label, count in checks.items() if count)

    raw = manifest.read_bytes()
    if b"\r\n" in raw:
        issues.append({"manifest_crlf": True})
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if line != line.rstrip():
            issues.append({"trailing_whitespace_line": line_number})
    return issues


def pubmed_row_issues(row, item):
    issues = []
    article_ids = item.get("articleids", [])
    actual_dois = {
        article_id["value"].lower()
        for article_id in article_ids
        if article_id.get("idtype") == "doi"
    }
    actual_pmcids = {
        article_id["value"]
        for article_id in article_ids
        if article_id.get("idtype") == "pmc"
    }
    if row["doi"].lower() not in actual_dois:
        issues.append({"doi_pmid_mismatch": {"doi": row["doi"], "pmid": row["pmid"]}})
    expected_pmcid = next(iter(actual_pmcids), "")
    if row["pmcid"] != expected_pmcid:
        issues.append(
            {
                "pmcid_pmid_mismatch": {
                    "pmid": row["pmid"],
                    "expected": expected_pmcid,
                    "actual": row["pmcid"],
                }
            }
        )
    actual_title = item.get("title", "").rstrip(".")
    if row["resolved_title"] != actual_title:
        issues.append({"title_mismatch": {"pmid": row["pmid"], "actual": actual_title}})
    if normalize(actual_title) not in normalize(row["citation"]):
        issues.append({"citation_pubmed_title_mismatch": row["pmid"]})
    return issues


def check_doi(doi):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(
        "https://doi.org/" + doi,
        method="HEAD",
        headers={"User-Agent": "paper-copd-acs-verifier/1.0"},
    )
    try:
        with opener.open(request, timeout=30) as response:
            return doi, response.status
    except urllib.error.HTTPError as exc:
        return doi, exc.code
    except Exception as exc:
        return doi, str(exc)


def online_issues(rows):
    issues = []
    pmids = sorted({row["pmid"] for row in rows if row["pmid"]})
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=" + ",".join(pmids)
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        pubmed = json.load(response)["result"]
    for row in rows:
        if row["pmid"]:
            issues.extend(pubmed_row_issues(row, pubmed[row["pmid"]]))

    dois = sorted({row["doi"] for row in rows if row["doi"]})
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(check_doi, doi) for doi in dois]
        for future in as_completed(futures):
            doi, status = future.result()
            if not isinstance(status, int) or not 200 <= status < 400:
                issues.append({"doi_resolution_failure": {"doi": doi, "status": status}})
    return issues


def main():
    _, _, rows = load_manifest(ROOT)
    issues = local_issues(ROOT)
    if not issues:
        issues.extend(online_issues(rows))
    result = {
        "markdown_files": len(list(ROOT.glob("*.md"))),
        "manifest_records": len(rows),
        "unique_dois": len({row["doi"] for row in rows if row["doi"]}),
        "unique_pmids": len({row["pmid"] for row in rows if row["pmid"]}),
        "issues": issues,
    }
    print(json.dumps(result, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
