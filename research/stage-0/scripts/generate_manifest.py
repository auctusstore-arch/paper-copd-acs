#!/usr/bin/env python3
"""Generate the Stage 0 publication manifest from the evidence Markdown files."""

import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIED_ON = "2026-08-07"
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


def extract_records():
    records = []
    for path in sorted(ROOT.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = re.search(r"https://doi\.org/(\S+)", line)
            if not match:
                continue
            doi = match.group(1).rstrip(".,;")
            citation = ""
            for previous in range(index - 1, max(-1, index - 8), -1):
                candidate = lines[previous].strip()
                if candidate and not candidate.startswith(("#", "-")):
                    citation = candidate.replace("*", "").replace("`", "")
                    break
            block = "\n".join(lines[index : index + 6])
            pmid_match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/", block)
            pmcid_match = re.search(r"pmc\.ncbi\.nlm\.nih\.gov/articles/(PMC\d+)/", block)
            records.append(
                {
                    "citation": citation,
                    "doi": doi,
                    "pmid": pmid_match.group(1) if pmid_match else "",
                    "pmcid": pmcid_match.group(1) if pmcid_match else "",
                    "source_file": path.name,
                }
            )
    return records


def deduplicate(records):
    """Keep one manifest record per publication and preserve every source file."""
    unique = {}
    for record in records:
        key = record["doi"].lower()
        if key not in unique:
            record["source_file"] = {record["source_file"]}
            unique[key] = record
            continue
        existing = unique[key]
        for identifier in ("pmid", "pmcid"):
            values = {value for value in (existing[identifier], record[identifier]) if value}
            if len(values) > 1:
                raise RuntimeError(f"Conflicting {identifier.upper()} for DOI {record['doi']}: {values}")
            existing[identifier] = next(iter(values), "")
        existing["source_file"].add(record["source_file"])
    for record in unique.values():
        record["source_file"] = ";".join(sorted(record["source_file"]))
    return list(unique.values())


def enrich_from_pubmed(records):
    pmids = sorted({record["pmid"] for record in records if record["pmid"]})
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=" + ",".join(pmids)
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        pubmed = json.load(response)["result"]

    for record in records:
        if record["pmid"]:
            item = pubmed[record["pmid"]]
            record["resolved_title"] = item.get("title", "").rstrip(".")
            article_ids = item.get("articleids", [])
            actual_dois = {
                item_id["value"].lower()
                for item_id in article_ids
                if item_id.get("idtype") == "doi"
            }
            if record["doi"].lower() not in actual_dois:
                raise RuntimeError(f"DOI-PMID mismatch: {record}")
            pubmed_pmcids = {
                item_id["value"]
                for item_id in article_ids
                if item_id.get("idtype") == "pmc"
            }
            if record["pmcid"] and pubmed_pmcids and record["pmcid"] not in pubmed_pmcids:
                raise RuntimeError(f"PMCID-PMID mismatch: {record}")
            record["pmcid"] = next(iter(pubmed_pmcids), record["pmcid"])
            record["verification_basis"] = (
                "PubMed metadata; abstract findings manually reviewed in evidence record"
            )
            record["full_text_status"] = (
                "Available via PMC"
                if record["pmcid"]
                else "Not retrieved in Stage 0; abstract and DOI metadata used"
            )
        else:
            url = "https://api.crossref.org/works/" + urllib.parse.quote(record["doi"], safe="")
            with urllib.request.urlopen(url, timeout=60) as response:
                message = json.load(response)["message"]
            record["resolved_title"] = (message.get("title") or [""])[0]
            record["verification_basis"] = "Crossref and DOI metadata only"
            record["full_text_status"] = "Not retrieved in Stage 0; no PubMed record paired"
        record["verified_on"] = VERIFIED_ON
    return records


def main():
    records = enrich_from_pubmed(deduplicate(extract_records()))
    gold_url = "https://goldcopd.org/2025-gold-report/"
    gold_source = ROOT / "03-triggers-diagnostics-guidelines.md"
    if gold_url not in gold_source.read_text(encoding="utf-8"):
        raise RuntimeError("The GOLD report must be linked from its evidence record")
    records.append(
        {
            "citation": "Global Initiative for Chronic Obstructive Lung Disease. Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease: 2025 Report. GOLD; 2025.",
            "resolved_title": "2025 GOLD Report",
            "doi": "",
            "pmid": "",
            "pmcid": "",
            "source_file": "03-triggers-diagnostics-guidelines.md",
            "verification_basis": "Official GOLD report page: https://goldcopd.org/2025-gold-report/",
            "full_text_status": "Official report page identified; report chapters cited in source record",
            "verified_on": VERIFIED_ON,
        }
    )
    records.sort(key=lambda record: (record["source_file"], record["resolved_title"].lower()))
    output = ROOT / "verification-manifest.tsv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps({"records": len(records), "output": str(output)}))


if __name__ == "__main__":
    main()
