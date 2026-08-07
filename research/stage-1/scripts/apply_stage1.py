#!/usr/bin/env python3
"""Create the Stage 1 revised manuscript with OOXML tracked changes."""

import copy
import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
STAGE = REPO / "research" / "stage-1"
SOURCE = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx"
OUTPUT = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review_REVISED.docx"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R = "{" + R_NS + "}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
XML = "{http://www.w3.org/XML/1998/namespace}"
CITATION = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")


class RevisionBuilder:
    def __init__(self, config):
        self.config = config
        self.revision_id = 1

    def attributes(self):
        value = str(self.revision_id)
        self.revision_id += 1
        return {
            W + "id": value,
            W + "author": self.config["revision_author"],
            W + "date": self.config["revision_date"],
        }

    @staticmethod
    def text(element):
        return "".join(node.text or "" for node in element.iter(W + "t"))

    @staticmethod
    def append_run(parent, text, deleted=False, run_properties=None):
        if not text:
            return
        run = ET.SubElement(parent, W + "r")
        if run_properties is not None:
            run.append(copy.deepcopy(run_properties))
        node = ET.SubElement(run, W + ("delText" if deleted else "t"))
        node.set(XML + "space", "preserve")
        node.text = text

    def append_deletion(self, parent, text, run_properties=None):
        deletion = ET.SubElement(parent, W + "del", self.attributes())
        self.append_run(deletion, text, deleted=True, run_properties=run_properties)

    def append_insertion(self, parent, text, run_properties=None):
        insertion = ET.SubElement(parent, W + "ins", self.attributes())
        self.append_run(insertion, text, run_properties=run_properties)

    @staticmethod
    def clear_content(paragraph):
        properties = paragraph.find(W + "pPr")
        saved = copy.deepcopy(properties) if properties is not None else None
        for child in list(paragraph):
            paragraph.remove(child)
        if saved is not None:
            paragraph.append(saved)

    @staticmethod
    def deleted_copy(run):
        copied = copy.deepcopy(run)
        for node in copied.iter(W + "t"):
            node.tag = W + "delText"
        return copied

    def replace_paragraph(self, paragraph, replacement):
        original_runs = [copy.deepcopy(run) for run in paragraph.findall(W + "r")]
        text_runs = [run for run in original_runs if self.text(run)]
        normal_properties = text_runs[0].find(W + "rPr") if text_runs else None
        second_properties = text_runs[1].find(W + "rPr") if len(text_runs) > 1 else normal_properties
        self.clear_content(paragraph)
        deletion = ET.SubElement(paragraph, W + "del", self.attributes())
        for run in original_runs:
            deletion.append(self.deleted_copy(run))
        insertion = ET.SubElement(paragraph, W + "ins", self.attributes())
        if replacement.startswith("Figure 1.") and len(text_runs) > 1:
            label = "Figure 1."
            self.append_run(insertion, label, run_properties=normal_properties)
            self.append_run(insertion, replacement[len(label):], run_properties=second_properties)
        else:
            self.append_run(insertion, replacement, run_properties=normal_properties)

    def remap_reference_number(self, value):
        mapped = self.config["citation_map"].get(str(int(value)))
        if mapped is None:
            raise RuntimeError(f"No citation mapping for reference {value}")
        if not mapped:
            raise RuntimeError(f"Removed reference {value} is still cited")
        return mapped

    def remap_citation(self, token):
        content = token[1:-1]
        parts = []
        for component in re.split(r"\s*,\s*", content):
            bounds = re.split(r"\s*-\s*", component)
            if len(bounds) == 1:
                parts.append(self.remap_reference_number(bounds[0]))
            elif len(bounds) == 2:
                parts.append(
                    self.remap_reference_number(bounds[0])
                    + "-"
                    + self.remap_reference_number(bounds[1])
                )
            else:
                raise RuntimeError(f"Unsupported citation token: {token}")
        return "[" + ",".join(parts) + "]"

    def remap_citations_in_paragraph(self, paragraph):
        for run in list(paragraph.findall(W + "r")):
            text_nodes = run.findall(W + "t")
            run_text = "".join(node.text or "" for node in text_nodes)
            matches = list(CITATION.finditer(run_text))
            changes = []
            for match in matches:
                old = match.group(0)
                new = self.remap_citation(old)
                if old != new:
                    changes.append((match.start(), match.end(), old, new))
            if not changes:
                continue
            non_text_children = [
                child for child in run if child.tag not in {W + "rPr", W + "t"}
            ]
            if len(text_nodes) != 1 or non_text_children:
                raise RuntimeError(
                    "Citation remapping encountered a complex or split run; "
                    "a run-aware fixture is required"
                )
            properties = run.find(W + "rPr")
            run_index = list(paragraph).index(run)
            cursor = 0
            replacement_nodes = []
            for start, end, old, new in changes:
                if run_text[cursor:start]:
                    holder = ET.Element("holder")
                    self.append_run(holder, run_text[cursor:start], run_properties=properties)
                    replacement_nodes.extend(list(holder))
                deletion = ET.Element(W + "del", self.attributes())
                self.append_run(deletion, old, deleted=True, run_properties=properties)
                replacement_nodes.append(deletion)
                insertion = ET.Element(W + "ins", self.attributes())
                self.append_run(insertion, new, run_properties=properties)
                replacement_nodes.append(insertion)
                cursor = end
            if run_text[cursor:]:
                holder = ET.Element("holder")
                self.append_run(holder, run_text[cursor:], run_properties=properties)
                replacement_nodes.extend(list(holder))
            paragraph.remove(run)
            for offset, node in enumerate(replacement_nodes):
                paragraph.insert(run_index + offset, node)

    def inserted_paragraph(self, template, text):
        paragraph = ET.Element(W + "p")
        properties = template.find(W + "pPr")
        if properties is not None:
            properties = copy.deepcopy(properties)
        else:
            properties = ET.Element(W + "pPr")
        mark_properties = properties.find(W + "rPr")
        if mark_properties is None:
            mark_properties = ET.SubElement(properties, W + "rPr")
        mark_properties.append(ET.Element(W + "ins", self.attributes()))
        paragraph.append(properties)
        template_runs = [run for run in template.findall(W + "r") if self.text(run)]
        run_properties = template_runs[0].find(W + "rPr") if template_runs else None
        self.append_insertion(paragraph, text, run_properties=run_properties)
        return paragraph


def register_namespaces(xml_bytes):
    for _, namespace in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
        prefix, uri = namespace
        if prefix != "xml":
            ET.register_namespace(prefix or "", uri)


def serialise(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def add_track_revisions(settings_bytes):
    register_namespaces(settings_bytes)
    settings = ET.fromstring(settings_bytes)
    track_revisions = settings.find(W + "trackRevisions")
    if track_revisions is None:
        track_revisions = ET.Element(W + "trackRevisions")
        settings.insert(0, track_revisions)
    else:
        track_revisions.attrib.pop(W + "val", None)
    return serialise(settings)


def add_figure_relationship(relationships_bytes, relationship_id):
    register_namespaces(relationships_bytes)
    relationships = ET.fromstring(relationships_bytes)
    if any(node.get("Id") == relationship_id for node in relationships):
        raise RuntimeError(f"Relationship {relationship_id} already exists")
    image_relationship = next(
        (node for node in relationships if node.get("Target") == "media/image1.png"),
        None,
    )
    if image_relationship is None:
        raise RuntimeError("Source image relationship is missing")
    inserted = copy.deepcopy(image_relationship)
    inserted.set("Id", relationship_id)
    inserted.set("Target", "media/image2.png")
    relationships.append(inserted)
    return serialise(relationships)


def load_references():
    with (STAGE / "reference-audit.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [int(row["order"]) for row in rows] != list(range(1, 45)):
        raise RuntimeError("The final reference audit must contain ordered references 1-44")
    return [row["citation"] for row in rows]


def transform_document(document_bytes, config, references):
    register_namespaces(document_bytes)
    document = ET.fromstring(document_bytes)
    body = document.find(W + "body")
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")
    builder = RevisionBuilder(config)
    figure_relationship_id = "rId9"
    figure_run = None
    figure_paragraph = None
    for paragraph in document.findall(".//" + W + "p"):
        for run in paragraph.findall(W + "r"):
            if run.find(".//" + A + "blip") is not None:
                if figure_run is not None:
                    raise RuntimeError("Expected exactly one source drawing run")
                figure_run = run
                figure_paragraph = paragraph
    if figure_run is None or figure_paragraph is None:
        raise RuntimeError("Source drawing run is missing")
    run_index = list(figure_paragraph).index(figure_run)
    deletion = ET.Element(W + "del", builder.attributes())
    deletion.append(copy.deepcopy(figure_run))
    insertion = ET.Element(W + "ins", builder.attributes())
    revised_run = copy.deepcopy(figure_run)
    revised_blip = revised_run.find(".//" + A + "blip")
    if revised_blip is None:
        raise RuntimeError("Source drawing has no embedded image")
    revised_blip.set(R + "embed", figure_relationship_id)
    insertion.append(revised_run)
    figure_paragraph.remove(figure_run)
    figure_paragraph.insert(run_index, deletion)
    figure_paragraph.insert(run_index + 1, insertion)

    body_paragraphs = [child for child in list(body) if child.tag == W + "p"]
    if len(body_paragraphs) != 126:
        raise RuntimeError(f"Expected 126 body paragraphs, found {len(body_paragraphs)}")

    replacements = {int(key): value for key, value in config["paragraph_replacements"].items()}
    reference_start = config["reference_start_paragraph"]
    for index, paragraph in enumerate(body_paragraphs[:reference_start]):
        if index in replacements:
            builder.replace_paragraph(paragraph, replacements[index])
        else:
            builder.remap_citations_in_paragraph(paragraph)

    tables = [child for child in list(body) if child.tag == W + "tbl"]
    table_replacements = config["table_replacements"]
    for table_number, table in enumerate(tables, 1):
        for row_number, row in enumerate(table.findall(W + "tr")):
            for column_number, cell in enumerate(row.findall(W + "tc")):
                paragraphs = cell.findall(W + "p")
                key = f"{table_number}:{row_number}:{column_number}"
                if key in table_replacements:
                    if not paragraphs:
                        raise RuntimeError(f"Table cell {key} has no paragraph")
                    builder.replace_paragraph(paragraphs[0], table_replacements[key])
                    for extra in paragraphs[1:]:
                        builder.remap_citations_in_paragraph(extra)
                else:
                    for paragraph in paragraphs:
                        builder.remap_citations_in_paragraph(paragraph)

    original_reference_paragraphs = body_paragraphs[reference_start:126]
    for paragraph, citation in zip(original_reference_paragraphs, references[:36]):
        builder.replace_paragraph(paragraph, citation)

    insertion_point = list(body).index(original_reference_paragraphs[-1]) + 1
    template = original_reference_paragraphs[-1]
    for citation in references[36:]:
        body.insert(insertion_point, builder.inserted_paragraph(template, citation))
        insertion_point += 1

    return serialise(document)


def main():
    config = json.loads((STAGE / "revisions.json").read_text(encoding="utf-8"))
    actual_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if actual_hash != config["source_sha256"]:
        raise RuntimeError(f"Original manuscript hash changed: {actual_hash}")
    references = load_references()

    with zipfile.ZipFile(SOURCE) as source_archive:
        document_bytes = source_archive.read("word/document.xml")
        settings_bytes = source_archive.read("word/settings.xml")
        relationships_bytes = source_archive.read("word/_rels/document.xml.rels")
        revised_figure = (STAGE / "assets" / "central-illustration-stage1.png").read_bytes()
        transformed_document = transform_document(document_bytes, config, references)
        transformed_settings = add_track_revisions(settings_bytes)
        transformed_relationships = add_figure_relationship(relationships_bytes, "rId9")
        with tempfile.NamedTemporaryFile(
            prefix="stage1-", suffix=".docx", dir=OUTPUT.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            with zipfile.ZipFile(temporary_path, "w") as output_archive:
                for info in source_archive.infolist():
                    if info.filename == "word/document.xml":
                        data = transformed_document
                    elif info.filename == "word/settings.xml":
                        data = transformed_settings
                    elif info.filename == "word/_rels/document.xml.rels":
                        data = transformed_relationships
                    else:
                        data = source_archive.read(info.filename)
                    output_archive.writestr(info, data)
                figure_info = copy.copy(source_archive.getinfo("word/media/image1.png"))
                figure_info.filename = "word/media/image2.png"
                figure_info.orig_filename = figure_info.filename
                output_archive.writestr(figure_info, revised_figure)
            with zipfile.ZipFile(temporary_path) as check_archive:
                if check_archive.testzip() is not None:
                    raise RuntimeError("Generated DOCX failed ZIP integrity check")
            temporary_path.replace(OUTPUT)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
    print(
        json.dumps(
            {
                "source": str(SOURCE),
                "output": str(OUTPUT),
                "references": len(references),
                "source_sha256": actual_hash,
            }
        )
    )


if __name__ == "__main__":
    main()
