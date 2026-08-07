#!/usr/bin/env python3
"""Fail-closed verifier for the Stage 1 tracked-change manuscript."""

import argparse
import copy
import csv
import datetime
import hashlib
import io
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
STAGE = REPO / "research" / "stage-1"
DEFAULT_SOURCE = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx"
DEFAULT_REVISED = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review_REVISED.docx"
EXPECTED_SOURCE_HASH = "8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CITATION = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
PLACEHOLDER = re.compile(r"\[(?:[^\]]*(?:to be verified|to be completed|placeholder|tbc|todo)[^\]]*)\]", re.I)


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def normalize(value):
    value = value.replace("β", "beta").replace("Β", "beta")
    value = unicodedata.normalize("NFKD", value)
    return "".join(character.lower() for character in value if character.isalnum())


def visible_text(element):
    values = []

    def visit(node, deleted=False):
        deleted = deleted or node.tag == W + "del"
        if node.tag == W + "t" and not deleted:
            values.append(node.text or "")
        for child in node:
            visit(child, deleted)

    visit(element)
    return "".join(values)


def rejected_text(element):
    values = []

    def visit(node, inserted=False):
        inserted = inserted or node.tag == W + "ins"
        if node.tag in {W + "t", W + "delText"} and not inserted:
            values.append(node.text or "")
        for child in node:
            visit(child, inserted)

    visit(element)
    return "".join(values)


def styled_spans(element, reject=False):
    """Return visible text spans with run properties for the accepted or rejected view."""
    spans = []

    def visit(node, inserted=False, deleted=False):
        inserted = inserted or node.tag == W + "ins"
        deleted = deleted or node.tag == W + "del"
        if node.tag == W + "r":
            include = (reject and not inserted) or (not reject and not deleted)
            if include:
                texts = []
                for child in node:
                    if child.tag == W + "t" and not deleted:
                        texts.append(child.text or "")
                    elif child.tag == W + "delText" and deleted and reject:
                        texts.append(child.text or "")
                text = "".join(texts)
                if text:
                    properties = node.find(W + "rPr")
                    style = ET.tostring(properties, encoding="utf-8") if properties is not None else b""
                    if spans and spans[-1][1] == style:
                        spans[-1] = (spans[-1][0] + text, style)
                    else:
                        spans.append((text, style))
            return
        for child in node:
            visit(child, inserted, deleted)

    visit(element)
    return spans


def direct_body_paragraphs(root):
    body = root.find(W + "body")
    if body is None:
        return []
    return [child for child in list(body) if child.tag == W + "p"]


def paragraph_properties(paragraph):
    properties = paragraph.find(W + "pPr")
    return ET.tostring(properties, encoding="utf-8") if properties is not None else b""


def setting_enabled(element):
    """Return False for explicit OOXML false values, not merely absent nodes."""
    if element is None:
        return False
    return (element.get(W + "val") or "true").lower() not in {"0", "false", "off", "no"}


def paragraph_mark_is_tracked(paragraph):
    properties = paragraph.find(W + "pPr")
    mark_properties = properties.find(W + "rPr") if properties is not None else None
    marker = mark_properties.find(W + "ins") if mark_properties is not None else None
    return marker is not None and all(marker.get(W + key) for key in ("id", "author", "date"))


def expand_citation(token):
    numbers = []
    for component in re.split(r"\s*,\s*", token[1:-1]):
        bounds = [int(value) for value in re.split(r"\s*-\s*", component)]
        if len(bounds) == 1:
            numbers.append(bounds[0])
        elif len(bounds) == 2 and bounds[0] <= bounds[1]:
            numbers.extend(range(bounds[0], bounds[1] + 1))
        else:
            raise ValueError(f"Malformed citation range {token}")
    return numbers


def remap_citations(text, citation_map):
    def replace(match):
        components = []
        for component in re.split(r"\s*,\s*", match.group(1)):
            bounds = re.split(r"\s*-\s*", component)
            mapped = [citation_map.get(str(int(bound))) for bound in bounds]
            if any(value is None or value == "" for value in mapped):
                raise ValueError(f"Missing citation map for {match.group(0)}")
            components.append("-".join(mapped))
        return "[" + ",".join(components) + "]"

    return CITATION.sub(replace, text)


def remap_styled_spans(spans, citation_map):
    remapped = []
    for text, style in spans:
        mapped_text = remap_citations(text, citation_map)
        if remapped and remapped[-1][1] == style:
            remapped[-1] = (remapped[-1][0] + mapped_text, style)
        else:
            remapped.append((mapped_text, style))
    return remapped


def replacement_styled_spans(text, source_spans, split_figure_label=False):
    if not text:
        return []
    first_style = source_spans[0][1] if source_spans else b""
    if split_figure_label and text.startswith("Figure 1.") and len(source_spans) > 1:
        label = "Figure 1."
        return [(label, first_style), (text[len(label):], source_spans[1][1])]
    return [(text, first_style)]


def manuscript_text_before_references(document, first_reference):
    body = document.find(W + "body")
    if body is None:
        return ""
    values = []
    for child in body:
        if child.tag == W + "p" and visible_text(child) == first_reference:
            break
        values.append(visible_text(child))
    return "\n".join(values)


def load_audit(issues):
    path = STAGE / "reference-audit.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 44:
        issues.append(f"Reference audit has {len(rows)} records instead of 44")
    if [row.get("order") for row in rows] != [str(number) for number in range(1, 45)]:
        issues.append("Reference audit order is not contiguous from 1 to 44")
    required_fields = (
        "citation", "resolved_title", "resolved_authors", "resolved_journal",
        "resolved_year", "resolved_publication_types", "doi", "doi_url",
        "publication_type", "study_design", "evidence_role", "source_quality",
        "title_source", "identifier_source", "official_record_url",
        "indexing_status", "verification_basis",
    )
    for field in required_fields:
        for row in rows:
            if not row.get(field):
                issues.append(f"Reference {row.get('order')} has empty {field}")
    dois = [row["doi"].lower() for row in rows if row.get("doi")]
    pmids = [row["pmid"] for row in rows if row.get("pmid")]
    if len(dois) != len(set(dois)):
        issues.append("Reference audit has duplicate DOI values")
    if len(pmids) != len(set(pmids)):
        issues.append("Reference audit has duplicate PMID values")
    for row in rows:
        if row.get("doi_url") != "https://doi.org/" + row.get("doi", ""):
            issues.append(f"Reference {row['order']} has invalid DOI URL")
        if row.get("pmid") and row.get("pubmed_url") != f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/":
            issues.append(f"Reference {row['order']} has invalid PubMed URL")
        if row.get("pmcid") and row.get("pmc_url") != f"https://pmc.ncbi.nlm.nih.gov/articles/{row['pmcid']}/":
            issues.append(f"Reference {row['order']} has invalid PMC URL")
    return rows


def verify_packages(source, revised, rows, issues):
    if not source.exists():
        issues.append(f"Missing source DOCX: {source}")
        return None
    if not revised.exists():
        issues.append(f"Missing revised DOCX: {revised}")
        return None
    source_hash = sha256_bytes(source.read_bytes())
    if source_hash != EXPECTED_SOURCE_HASH:
        issues.append(f"Original manuscript SHA-256 changed: {source_hash}")
        return None
    try:
        source_zip = zipfile.ZipFile(source)
        revised_zip = zipfile.ZipFile(revised)
    except zipfile.BadZipFile as error:
        issues.append(f"Invalid DOCX ZIP package: {error}")
        return None
    with source_zip, revised_zip:
        if source_zip.testzip() is not None or revised_zip.testzip() is not None:
            issues.append("A DOCX package failed CRC verification")
        expected_parts = set(source_zip.namelist()) | {"word/media/image2.png"}
        if set(revised_zip.namelist()) != expected_parts:
            issues.append("Revised DOCX package does not contain exactly the source parts plus image2.png")
        excluded = {"word/document.xml", "word/settings.xml", "word/_rels/document.xml.rels"}
        for name in source_zip.namelist():
            if name not in excluded and name in revised_zip.namelist():
                if source_zip.read(name) != revised_zip.read(name):
                    issues.append(f"Unexpected changed OOXML part: {name}")
        if "word/media/image1.png" not in revised_zip.namelist():
            issues.append("Original image1.png is missing from the revised package")
        elif revised_zip.read("word/media/image1.png") != source_zip.read("word/media/image1.png"):
            issues.append("Original image1.png was modified instead of preserved for Reject All")
        expected_figure = (STAGE / "assets" / "central-illustration-stage1.png").read_bytes()
        if "word/media/image2.png" not in revised_zip.namelist():
            issues.append("Tracked replacement image2.png is missing")
        elif revised_zip.read("word/media/image2.png") != expected_figure:
            issues.append("Embedded image2.png does not match the reviewed Stage 1 figure")
        source_relationships = ET.fromstring(source_zip.read("word/_rels/document.xml.rels"))
        relationships = ET.fromstring(revised_zip.read("word/_rels/document.xml.rels"))
        source_document = ET.fromstring(source_zip.read("word/document.xml"))
        revised_document = ET.fromstring(revised_zip.read("word/document.xml"))
        source_settings = ET.fromstring(source_zip.read("word/settings.xml"))
        settings = ET.fromstring(revised_zip.read("word/settings.xml"))

    settings_without_tracking = copy.deepcopy(settings)
    tracking_node = settings_without_tracking.find(W + "trackRevisions")
    if tracking_node is not None:
        settings_without_tracking.remove(tracking_node)
    if ET.tostring(source_settings) != ET.tostring(settings_without_tracking):
        issues.append("Word settings changed beyond enabling trackRevisions")

    source_relationship_map = {node.get("Id"): dict(node.attrib) for node in source_relationships}
    revised_relationship_map = {node.get("Id"): dict(node.attrib) for node in relationships}
    for relationship_id, attributes in source_relationship_map.items():
        if revised_relationship_map.get(relationship_id) != attributes:
            issues.append(f"Source relationship {relationship_id} was modified")
    added_relationships = set(revised_relationship_map) - set(source_relationship_map)
    if len(added_relationships) != 1:
        issues.append("Revised package must add exactly one image relationship")

    relationship_targets = {
        relationship.get("Id"): relationship.get("Target", "").lstrip("/")
        for relationship in relationships
    }
    deleted_embeds = {
        blip.get(R + "embed")
        for deletion in revised_document.findall(".//" + W + "del")
        for blip in deletion.findall(".//" + A + "blip")
    }
    inserted_embeds = {
        blip.get(R + "embed")
        for insertion in revised_document.findall(".//" + W + "ins")
        for blip in insertion.findall(".//" + A + "blip")
    }
    if not any(relationship_targets.get(value) == "media/image1.png" for value in deleted_embeds):
        issues.append("Original image drawing is not inside a tracked deletion")
    if not any(relationship_targets.get(value) == "media/image2.png" for value in inserted_embeds):
        issues.append("Revised image drawing is not inside a tracked insertion")

    source_image_relationship = next(
        (node for node in source_relationships if node.get("Target") == "media/image1.png"), None
    )
    revised_image_relationship = next(
        (node for node in relationships if node.get("Target") == "media/image2.png"), None
    )
    if source_image_relationship is None or revised_image_relationship is None:
        issues.append("Source or replacement image relationship is missing")
    else:
        replacement_id = revised_image_relationship.get("Id")
        if replacement_id is None:
            issues.append("Replacement image relationship has no Id")
        else:
            expected_attributes = dict(source_image_relationship.attrib)
            expected_attributes["Id"] = replacement_id
            expected_attributes["Target"] = "media/image2.png"
            if dict(revised_image_relationship.attrib) != expected_attributes:
                issues.append("Replacement image relationship has invalid attributes")

    source_drawing_runs = [
        run for run in source_document.findall(".//" + W + "r")
        if run.find(".//" + A + "blip") is not None
    ]
    deleted_drawing_runs = [
        run
        for deletion in revised_document.findall(".//" + W + "del")
        for run in deletion.findall(W + "r")
        if any(
            relationship_targets.get(blip.get(R + "embed")) == "media/image1.png"
            for blip in run.findall(".//" + A + "blip")
        )
    ]
    if len(source_drawing_runs) != 1 or len(deleted_drawing_runs) != 1:
        issues.append("Expected exactly one source drawing and one tracked source drawing")
    elif ET.tostring(source_drawing_runs[0]) != ET.tostring(deleted_drawing_runs[0]):
        issues.append("Tracked source drawing differs structurally from the original drawing")

    original_paragraphs = direct_body_paragraphs(source_document)
    revised_paragraphs = direct_body_paragraphs(revised_document)
    config = json.loads((STAGE / "revisions.json").read_text(encoding="utf-8"))
    if len(original_paragraphs) != 126:
        issues.append(f"Original has {len(original_paragraphs)} direct paragraphs instead of 126")
    expected_revised_paragraphs = 90 + len(rows)
    if len(revised_paragraphs) != expected_revised_paragraphs:
        issues.append(
            f"Revised has {len(revised_paragraphs)} direct paragraphs instead of "
            f"{expected_revised_paragraphs}"
        )
    for index in range(min(126, len(original_paragraphs), len(revised_paragraphs))):
        if paragraph_properties(original_paragraphs[index]) != paragraph_properties(revised_paragraphs[index]):
            issues.append(f"Paragraph style/properties changed at direct paragraph {index}")
    replacements = {int(key): value for key, value in config["paragraph_replacements"].items()}
    for index in range(min(90, len(original_paragraphs), len(revised_paragraphs))):
        source_text = visible_text(original_paragraphs[index])
        expected_text = replacements.get(index)
        if expected_text is None:
            try:
                expected_text = remap_citations(source_text, config["citation_map"])
            except ValueError as error:
                issues.append(str(error))
                expected_text = source_text
        if visible_text(revised_paragraphs[index]) != expected_text:
            issues.append(f"Accepted direct paragraph {index} differs from its configured transformation")
        if rejected_text(revised_paragraphs[index]) != source_text:
            issues.append(f"Rejected direct paragraph {index} does not restore the source text")
        source_styles = styled_spans(original_paragraphs[index])
        if styled_spans(revised_paragraphs[index], reject=True) != source_styles:
            issues.append(f"Rejected direct paragraph {index} does not restore source run formatting")
        if index in replacements:
            expected_styles = replacement_styled_spans(
                replacements[index], source_styles, split_figure_label=index == 10
            )
        else:
            try:
                expected_styles = remap_styled_spans(source_styles, config["citation_map"])
            except ValueError as error:
                issues.append(str(error))
                expected_styles = source_styles
        if styled_spans(revised_paragraphs[index]) != expected_styles:
            issues.append(f"Accepted direct paragraph {index} has unexpected run formatting")

    source_tables = source_document.findall(".//" + W + "tbl")
    revised_tables = revised_document.findall(".//" + W + "tbl")
    if len(source_tables) != len(revised_tables):
        issues.append("Table count differs between source and revised manuscripts")
    for table_number, (source_table, revised_table) in enumerate(zip(source_tables, revised_tables), 1):
        source_rows = source_table.findall(W + "tr")
        revised_rows = revised_table.findall(W + "tr")
        if len(source_rows) != len(revised_rows):
            issues.append(f"Row count changed in table {table_number}")
            continue
        for row_number, (source_row, revised_row) in enumerate(zip(source_rows, revised_rows)):
            source_cells = source_row.findall(W + "tc")
            revised_cells = revised_row.findall(W + "tc")
            if len(source_cells) != len(revised_cells):
                issues.append(f"Cell count changed in table {table_number}, row {row_number}")
                continue
            for column_number, (source_cell, revised_cell) in enumerate(zip(source_cells, revised_cells)):
                source_cell_paragraphs = source_cell.findall(W + "p")
                revised_cell_paragraphs = revised_cell.findall(W + "p")
                if len(source_cell_paragraphs) != len(revised_cell_paragraphs):
                    issues.append(f"Paragraph count changed in table cell {table_number}:{row_number}:{column_number}")
                    continue
                key = f"{table_number}:{row_number}:{column_number}"
                for paragraph_number, (source_paragraph, revised_paragraph) in enumerate(
                    zip(source_cell_paragraphs, revised_cell_paragraphs)
                ):
                    source_text = visible_text(source_paragraph)
                    expected_text = config["table_replacements"].get(key) if paragraph_number == 0 else None
                    if expected_text is None:
                        try:
                            expected_text = remap_citations(source_text, config["citation_map"])
                        except ValueError as error:
                            issues.append(str(error))
                            expected_text = source_text
                    if visible_text(revised_paragraph) != expected_text:
                        issues.append(f"Accepted table paragraph differs at {key}:{paragraph_number}")
                    if rejected_text(revised_paragraph) != source_text:
                        issues.append(f"Rejected table paragraph does not restore source at {key}:{paragraph_number}")
                    source_styles = styled_spans(source_paragraph)
                    if styled_spans(revised_paragraph, reject=True) != source_styles:
                        issues.append(f"Rejected table run formatting differs at {key}:{paragraph_number}")
                    if paragraph_number == 0 and key in config["table_replacements"]:
                        expected_styles = replacement_styled_spans(expected_text, source_styles)
                    else:
                        try:
                            expected_styles = remap_styled_spans(source_styles, config["citation_map"])
                        except ValueError as error:
                            issues.append(str(error))
                            expected_styles = source_styles
                    if styled_spans(revised_paragraph) != expected_styles:
                        issues.append(f"Accepted table run formatting differs at {key}:{paragraph_number}")
                    if paragraph_properties(source_paragraph) != paragraph_properties(revised_paragraph):
                        issues.append(f"Table paragraph style/properties changed at {key}:{paragraph_number}")
    if len(revised_tables) != 5:
        issues.append("Revised manuscript does not contain exactly five tables")
    insertions = revised_document.findall(".//" + W + "ins")
    deletions = revised_document.findall(".//" + W + "del")
    if not insertions or not deletions:
        issues.append("Tracked insertions or deletions are missing")
    revision_ids = []
    for node in insertions + deletions:
        if node.get(W + "author") != "auctusstore-arch":
            issues.append("Tracked revision has an unexpected author")
        date_value = node.get(W + "date")
        try:
            datetime.datetime.fromisoformat((date_value or "").replace("Z", "+00:00"))
        except ValueError:
            issues.append("Tracked revision has an invalid date")
        revision_id = node.get(W + "id")
        if revision_id is None or not revision_id.isdecimal():
            issues.append("Tracked revision ID is not a decimal number")
        revision_ids.append(revision_id)
    if None in revision_ids or len(revision_ids) != len(set(revision_ids)):
        issues.append("Tracked revision IDs are missing or duplicated")
    elif all(value is not None and value.isdecimal() for value in revision_ids):
        if sorted(int(value) for value in revision_ids) != list(range(1, len(revision_ids) + 1)):
            issues.append("Tracked revision IDs are not contiguous from 1")
    if not setting_enabled(settings.find(W + "trackRevisions")):
        issues.append("w:trackRevisions is absent or explicitly disabled in settings.xml")

    reference_paragraphs = revised_paragraphs[90:90 + len(rows)]
    actual_references = [visible_text(paragraph) for paragraph in reference_paragraphs]
    expected_references = [row["citation"] for row in rows]
    if actual_references != expected_references:
        issues.append("DOCX reference list does not exactly match reference-audit.tsv")
    inserted_reference_paragraphs = reference_paragraphs[36:]
    if any(not paragraph_mark_is_tracked(paragraph) for paragraph in inserted_reference_paragraphs):
        issues.append("An inserted reference paragraph has an untracked paragraph mark")
    if not rows:
        return revised_document
    body_text = manuscript_text_before_references(revised_document, rows[0]["citation"])
    if PLACEHOLDER.search(body_text) or PLACEHOLDER.search("\n".join(actual_references)):
        issues.append("Accepted manuscript text contains a placeholder marker")
    citation_numbers = []
    try:
        for match in CITATION.finditer(body_text):
            citation_numbers.extend(expand_citation(match.group(0)))
    except ValueError as error:
        issues.append(str(error))
    if any(number < 1 or number > len(rows) for number in citation_numbers):
        issues.append(f"Body contains a citation outside references 1-{len(rows)}")
    first_seen = []
    for number in citation_numbers:
        if number not in first_seen:
            first_seen.append(number)
    if first_seen != list(range(1, len(rows) + 1)):
        missing = sorted(set(range(1, len(rows) + 1)) - set(first_seen))
        issues.append(f"Reference first-citation order is invalid; missing/orphan={missing}; order={first_seen}")

    for raw_index, replacement in config["paragraph_replacements"].items():
        index = int(raw_index)
        if visible_text(revised_paragraphs[index]) != replacement:
            issues.append(f"Accepted paragraph {index} does not match revisions.json")
        if rejected_text(revised_paragraphs[index]) != visible_text(original_paragraphs[index]):
            issues.append(f"Rejected paragraph {index} does not restore the source text")
    for offset, paragraph in enumerate(reference_paragraphs[:36]):
        source_paragraph = original_paragraphs[90 + offset]
        if rejected_text(paragraph) != visible_text(source_paragraph):
            issues.append(f"Rejected reference {offset + 1} does not restore the source text")
        source_styles = styled_spans(source_paragraph)
        if styled_spans(paragraph, reject=True) != source_styles:
            issues.append(f"Rejected reference {offset + 1} does not restore source run formatting")
        expected_styles = replacement_styled_spans(expected_references[offset], source_styles)
        if styled_spans(paragraph) != expected_styles:
            issues.append(f"Accepted reference {offset + 1} has unexpected run formatting")
    inserted_text = "\n".join(config["paragraph_replacements"].values())
    inserted_text += "\n" + "\n".join(config["table_replacements"].values())
    inserted_text += "\n" + "\n".join(expected_references)
    if "—" in inserted_text:
        issues.append("Stage 1 inserted text contains an em dash")
    if PLACEHOLDER.search(inserted_text):
        issues.append("Stage 1 inserted text contains a placeholder")
    return revised_document


def verify_online(rows, issues):
    pmids = [row["pmid"] for row in rows if row.get("pmid")]
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=" + ",".join(pmids)
    )
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            result = json.load(response)["result"]
    except Exception as error:
        issues.append(f"PubMed verification request failed: {error}")
        return
    for row in rows:
        if row.get("pmid"):
            item = result.get(row["pmid"])
            if not item:
                issues.append(f"PubMed did not return PMID {row['pmid']}")
                continue
            article_ids = item.get("articleids", [])
            dois = {
                article_id["value"].lower()
                for article_id in article_ids
                if article_id.get("idtype") == "doi"
            }
            pmcids = {
                article_id["value"]
                for article_id in article_ids
                if article_id.get("idtype") == "pmc"
            }
            if row["doi"].lower() not in dois:
                issues.append(f"Reference {row['order']} DOI-PMID pair failed PubMed")
            audit_pmcid = row.get("pmcid") or ""
            if pmcids and audit_pmcid not in pmcids:
                issues.append(f"Reference {row['order']} is missing the PMCID returned by PubMed")
            elif audit_pmcid and audit_pmcid not in pmcids:
                issues.append(f"Reference {row['order']} PMCID does not match PubMed")
            title = item.get("title", "").rstrip(".")
            if normalize(title) != normalize(row["resolved_title"]):
                issues.append(f"Reference {row['order']} title drifted from PubMed")
        else:
            crossref_url = "https://api.crossref.org/works/" + urllib.parse.quote(row["doi"], safe="")
            try:
                request = urllib.request.Request(crossref_url, headers={"User-Agent": "paper-copd-acs-audit/1.0"})
                with urllib.request.urlopen(request, timeout=60) as response:
                    message = json.load(response)["message"]
                title = (message.get("title") or [""])[0]
                if normalize(title) != normalize(row["resolved_title"]):
                    issues.append(f"Reference {row['order']} title drifted from Crossref")
            except Exception as error:
                issues.append(f"Reference {row['order']} Crossref verification failed: {error}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--revised", type=Path, default=DEFAULT_REVISED)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    issues = []
    rows = load_audit(issues)
    verify_packages(args.source, args.revised, rows, issues)
    if not args.offline:
        verify_online(rows, issues)
    if issues:
        print(f"Stage 1 verification FAILED with {len(issues)} issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        raise SystemExit(1)
    print(
        json.dumps(
            {
                "status": "PASS",
                "references": len(rows),
                "source_sha256": EXPECTED_SOURCE_HASH,
                "network_checks": not args.offline,
                "revised": str(args.revised),
            }
        )
    )


if __name__ == "__main__":
    main()
