#!/usr/bin/env python3
"""Generate the Stage 2 final reference audit from verified primary metadata."""

import csv
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "reference-seed.tsv"
OUTPUT = ROOT / "reference-audit.tsv"
FIELDS = [
    "order",
    "citation",
    "resolved_title",
    "resolved_authors",
    "resolved_journal",
    "resolved_year",
    "resolved_volume",
    "resolved_issue",
    "resolved_pages",
    "resolved_publication_types",
    "doi",
    "doi_url",
    "pmid",
    "pubmed_url",
    "pmcid",
    "pmc_url",
    "publication_type",
    "study_design",
    "design_detail",
    "evidence_role",
    "source_quality",
    "disposition",
    "title_source",
    "identifier_source",
    "official_record_url",
    "indexing_status",
    "verification_basis",
    "verified_on",
]


def normalize(value):
    value = value.replace("β", "beta").replace("Β", "beta")
    value = unicodedata.normalize("NFKD", value)
    return "".join(character.lower() for character in value if character.isalnum())


def main():
    with SEED.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    expected_orders = [str(number) for number in range(1, len(rows) + 1)]
    if [row["order"] for row in rows] != expected_orders:
        raise RuntimeError("Reference seed order must be contiguous and start at 1")

    pmids = [row["pmid"] for row in rows if row["pmid"]]
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=" + ",".join(pmids)
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        pubmed = json.load(response)["result"]

    for row in rows:
        if row["pmid"]:
            item = pubmed[row["pmid"]]
            title = item.get("title", "").rstrip(".")
            author_names = [
                author["name"]
                for author in item.get("authors", [])
                if author.get("authtype") == "Author"
            ]
            row["resolved_authors"] = "; ".join(author_names)
            row["resolved_journal"] = item.get("source", "")
            row["resolved_year"] = item.get("pubdate", "")[:4]
            row["resolved_volume"] = item.get("volume", "")
            row["resolved_issue"] = item.get("issue", "")
            row["resolved_pages"] = item.get("pages", "")
            row["resolved_publication_types"] = "; ".join(item.get("pubtype", []))
            citation_normalized = normalize(row["citation"])
            # For "et al" citations, only verify the first author matches
            if "etal" in citation_normalized:
                if normalize(author_names[0]) not in citation_normalized:
                    raise RuntimeError(
                        f"Citation-first-author mismatch at reference {row['order']}: {author_names[0]}"
                    )
            else:
                for author in author_names[:6]:
                    if normalize(author) not in citation_normalized:
                        raise RuntimeError(
                            f"Citation-author mismatch at reference {row['order']}: {author}"
                        )
            for label, value in (
                ("journal", row["resolved_journal"]),
                ("year", row["resolved_year"]),
                ("volume", row["resolved_volume"]),
                ("issue", row["resolved_issue"]),
            ):
                if value and normalize(value) not in citation_normalized:
                    raise RuntimeError(
                        f"Citation-{label} mismatch at reference {row['order']}: {value}"
                    )
            pages = row["resolved_pages"]
            page_parts = re.split(r"[-–]", pages) if pages else []
            if pages and not all(normalize(part) in citation_normalized for part in page_parts):
                raise RuntimeError(
                    f"Citation-pages mismatch at reference {row['order']}: {pages}"
                )
            article_ids = item.get("articleids", [])
            dois = {
                article_id["value"].lower()
                for article_id in article_ids
                if article_id.get("idtype") == "doi"
            }
            if row["doi"].lower() not in dois:
                raise RuntimeError(f"DOI-PMID mismatch at reference {row['order']}: {row['doi']}")
            pmcids = [
                article_id["value"]
                for article_id in article_ids
                if article_id.get("idtype") == "pmc"
            ]
            row["pmcid"] = pmcids[0] if pmcids else ""
            row["verification_basis"] = "PubMed ESummary DOI-PMID-title pairing"
        else:
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                "?db=pubmed&retmode=json&term="
                + urllib.parse.quote(row["doi"] + "[doi]")
            )
            with urllib.request.urlopen(search_url, timeout=60) as response:
                found_pmids = json.load(response)["esearchresult"]["idlist"]
            if found_pmids:
                raise RuntimeError(
                    f"Reference {row['order']} omits available PMID {found_pmids[0]}"
                )
            crossref_url = "https://api.crossref.org/works/" + urllib.parse.quote(row["doi"], safe="")
            with urllib.request.urlopen(crossref_url, timeout=60) as response:
                message = json.load(response)["message"]
            title = (message.get("title") or [""])[0]
            row["resolved_authors"] = "; ".join(
                " ".join(
                    value
                    for value in (author.get("family", ""), author.get("given", ""))
                    if value
                )
                for author in message.get("author", [])
            )
            row["resolved_journal"] = "; ".join(message.get("container-title", []))
            date_parts = message.get("published", {}).get("date-parts", [[]])
            row["resolved_year"] = str(date_parts[0][0]) if date_parts and date_parts[0] else ""
            row["resolved_volume"] = message.get("volume", "")
            row["resolved_issue"] = message.get("issue", "")
            row["resolved_pages"] = message.get("page", "") or message.get("article-number", "")
            row["resolved_publication_types"] = message.get("type", "")
            europe_url = (
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&query="
                + urllib.parse.quote('DOI:"' + row["doi"] + '"')
            )
            with urllib.request.urlopen(europe_url, timeout=60) as response:
                europe_results = json.load(response).get("resultList", {}).get("result", [])
            pmcids = [item.get("pmcid", "") for item in europe_results if item.get("pmcid")]
            row["pmcid"] = pmcids[0] if pmcids else ""
            row["verification_basis"] = "Crossref DOI metadata and Europe PMC identifier lookup"
        if normalize(title) not in normalize(row["citation"]):
            raise RuntimeError(
                f"Citation-title mismatch at reference {row['order']}: expected {title!r}"
            )
        row["resolved_title"] = title
        row["doi_url"] = "https://doi.org/" + row["doi"]
        row["pubmed_url"] = (
            "https://pubmed.ncbi.nlm.nih.gov/" + row["pmid"] + "/"
            if row["pmid"]
            else ""
        )
        row["pmc_url"] = (
            "https://pmc.ncbi.nlm.nih.gov/articles/" + row["pmcid"] + "/"
            if row["pmcid"]
            else ""
        )
        row["title_source"] = "PubMed ESummary" if row["pmid"] else "Crossref"
        row["identifier_source"] = (
            "PubMed articleids" if row["pmid"] else "PubMed ESearch and Europe PMC"
        )
        row["official_record_url"] = row["doi_url"]
        row["indexing_status"] = (
            "PubMed indexed; PMCID present"
            if row["pmid"] and row["pmcid"]
            else "PubMed indexed; no PMCID assigned"
            if row["pmid"]
            else "Not indexed in PubMed; PMCID present in Europe PMC"
            if row["pmcid"]
            else "Not indexed in PubMed or PMC"
        )
        row["verified_on"] = "2026-08-07"

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"records": len(rows), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()
