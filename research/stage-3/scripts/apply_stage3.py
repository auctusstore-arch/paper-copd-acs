#!/usr/bin/env python3
"""Stage 3 OOXML transformer — overlays Stage 3 methodology and argument corrections."""

import copy
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
STAGE = REPO / "research" / "stage-3"
STAGE1 = REPO / "research" / "stage-1"
STAGE2 = REPO / "research" / "stage-2"
SOURCE = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx"
OUTPUT = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review_REVISED.docx"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"
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
        self.clear_content(paragraph)
        deletion = ET.SubElement(paragraph, W + "del", self.attributes())
        for run in original_runs:
            deletion.append(self.deleted_copy(run))
        insertion = ET.SubElement(paragraph, W + "ins", self.attributes())
        self.append_run(insertion, replacement, run_properties=normal_properties)

    def remap_reference_number(self, value):
        mapped = self.config["citation_map"].get(str(int(value)))
        return str(mapped) if mapped is not None else value

    def remap_citations(self, text):
        def replace(match):
            parts = re.split(r"\s*[-,]\s*", match.group(1))
            remapped = [self.remap_reference_number(part) for part in parts]
            return "[" + ",".join(remapped) + "]"
        return CITATION.sub(replace, text)

    def insert_paragraph_after(self, body, after_index, text):
        insertion = ET.SubElement(body, W + "p")
        ET.SubElement(insertion, W + "pPr")
        ins = ET.SubElement(insertion, W + "ins", self.attributes())
        self.append_run(ins, text)
        body.remove(insertion)
        body.insert(after_index + 1, insertion)


def load_stage1_config():
    with (STAGE1 / "revisions.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def build_s1_to_s3_map():
    """Map old S1 citation numbers to final S3 numbers (same as S2 for 1-62, plus new 63-69)."""
    citation_map = {}
    for old in range(1, 13):
        citation_map[str(old)] = str(old)
    for old in range(13, 34):
        citation_map[str(old)] = str(old + 5)
    for old in range(34, 37):
        citation_map[str(old)] = str(old + 7)
    for old in range(37, 39):
        citation_map[str(old)] = str(old + 10)
    for old in range(39, 45):
        citation_map[str(old)] = str(old + 14)
    return citation_map


def stage3_additions():
    """Stage 3 paragraph insertions and replacements (using final S3 citation numbers)."""
    return {
        "insertions": {
            # C5: SCCS biases sub-section — insert after paragraph ~40 (end of §6 trigger discussion)
            "c5_sccs_bias": (
                40,
                "Three biases inherent in the self-controlled case series design merit explicit attention. "
                "First, detection bias: severe exacerbations are hospitalisations, and hospitalised patients "
                "are more likely to have troponin measured than stable outpatients. The severity gradient "
                "we report (incidence rate ratio 2.58 for severe versus 1.58 for moderate exacerbation [12]) "
                "is the predicted gradient of detection bias as well as the predicted gradient of a true trigger, "
                "and the design cannot distinguish the two. "
                "Second, protopathic bias: antibiotics and oral steroids prescribed for exacerbation symptoms "
                "may be initiated for early manifestations of myocardial infarction, particularly dyspnoea. "
                "Rothnie and colleagues excluded the first day of exacerbation to mitigate this bias [12], "
                "but the 1-3 day peak (incidence rate ratio 8.00, 95% confidence interval 5.81-11.01 for severe "
                "exacerbation) could partly reflect misclassification. "
                "Third, time-varying confounding: the self-controlled case series removes time-invariant confounding "
                "but not co-occurring factors such as systemic steroids, beta-agonists, dehydration, immobility, "
                "and infection-related hypercoagulability. Rothnie and colleagues acknowledged that medicine use "
                "was defined at baseline rather than as a time-varying effect modifier [12]. "
                "These limitations do not invalidate the trigger signal, but they bound the strength of inference "
                "that can be drawn from incidence rate ratios alone."
            ),
            # M6: PAF sub-section — insert after the two-clock model section (paragraph ~46)
            "m6_paf": (
                46,
                "To quantify the contribution of the fast clock to the total cardiovascular burden, "
                "we estimated the population attributable fraction (PAF) for myocardial infarction triggered "
                "by exacerbation. Using the formula PAF = \u03a3p\u2091(IRR\u2091 - 1) / [1 + \u03a3p\u2091(IRR\u2091 - 1)] "
                "where p\u2091 is the proportion of person-time spent in the 91-day risk window after an exacerbation, "
                "and IRR\u2091 is the incidence rate ratio from Rothnie and colleagues [12], "
                "we computed PAF for severe exacerbation (IRR 2.58, annual rate 0.15-0.3) and moderate exacerbation "
                "(IRR 1.58, annual rate 0.8-1.5). "
                "The low estimate, using the lower bounds of exacerbation rates, yields PAF 14.9%. "
                "The high estimate, using the upper bounds, yields PAF 25.1%. "
                "The midpoint is 20.3%, meaning that approximately one in five post-COPD myocardial infarctions "
                "is attributable to the fast clock. The remaining 75-85% of the cardiovascular burden is "
                "substrate-driven, consistent with the model's central prediction that the slow clock dominates "
                "population risk. Severe exacerbations alone account for a PAF of 5.6-10.6%, and moderate "
                "exacerbations alone account for 10.4-17.8%, reflecting the greater population frequency of "
                "moderate events despite their lower individual risk."
            ),
            # M11: Post-exacerbation outcome composition + PE — insert after paragraph ~50 (end of §6/§8 trigger discussion)
            "m11_outcomes": (
                50,
                "The coronary framing of post-exacerbation risk, while supported by the trigger signal, "
                "overlooks the composition of cardiovascular events. In the EXACOS-CV meta-analysis, "
                "of 40,773 cardiovascular events following exacerbation, arrhythmia accounted for 49.3%, "
                "heart failure decompensation for 31.1%, and acute coronary syndrome for only 10.1% [24]. "
                "Hawkins and colleagues reported that heart failure decompensation carried the highest "
                "magnitude risk in the first week after exacerbation (hazard ratio 72.34, 95% confidence "
                "interval 64.43-81.22) [25], far exceeding the risk for myocardial infarction. "
                "Pulmonary embolism is a further competitor to the coronary narrative: a pooled prevalence "
                "of 16.1% (95% confidence interval 8.3-25.8%) has been reported in unexplained acute "
                "exacerbations [63], and exacerbation history is associated with pulmonary embolism risk "
                "in a dose-response fashion (subdistribution hazard ratio 2.62 for two or more severe "
                "exacerbations) that proportionally exceeds the myocardial infarction risk (1.82) [64]. "
                "The two-clock model should therefore be read as one component of a broader post-exacerbation "
                "cardiovascular risk profile, not as a coronary-specific claim."
            ),
            # F1: Framing downgrade — insert after paragraph ~15 (end of §2 scope/evidence appraisal)
            "f1_framing": (
                15,
                "Recent narrative reviews have begun to integrate cardiopulmonary risk into COPD management "
                "rather than treating systemic inflammation as the sole organising principle [47,48,65,66]. "
                "The framing of this review as a corrective to a dominant spillover narrative should be read "
                "as a misplaced emphasis in the literature, not as a hypothesis that has expired."
            ),
            # M5: SUMMIT calibration — insert after paragraph ~25 (mechanism discussion)
            "m5_summit": (
                25,
                "SUMMIT warrants calibrated interpretation. Its cardiovascular composite hazard ratio of 0.93 "
                "(95% confidence interval 0.75-1.14) [5] is conventionally read as null, but the lower confidence "
                "interval bound of 0.75 means a 25% relative benefit remains possible. The trial was powered for "
                "all-cause mortality and was not designed to detect a cardiovascular effect of this magnitude. "
                "The statement that SUMMIT did nothing detectable to the heart conflates absence of evidence "
                "with evidence of absence."
            ),
        },
        "replacements": {
            # M4: Fix STATCOPE non sequitur — paragraph ~28 (§4 spillover discussion)
            28: (
                "The pharmacological objection that inhaled corticosteroids do not reach the systemic circulation "
                "in sufficient quantity to modulate cardiovascular risk is not answered by STATCOPE [6], which "
                "tested whether a systemic statin reduces exacerbations (direction circulation to lung), "
                "not whether reducing airway inflammation reduces cardiovascular events (direction lung to "
                "circulation). SUMMIT is the relevant trial for the latter question: it reduced exacerbations "
                "but did not reduce the cardiovascular composite (hazard ratio 0.93, 95% confidence interval "
                "0.75-1.14) [5]. This null result is consistent with the objection but does not settle it, "
                "because the trial was underpowered for the cardiovascular endpoint and the lower confidence "
                "interval bound permits a clinically meaningful benefit."
            ),
        },
    }


def main():
    stage1_config = load_stage1_config()
    s3_additions = stage3_additions()
    citation_map = build_s1_to_s3_map()

    config = {
        "revision_author": "Hendri Susilo",
        "revision_date": "2026-08-08T12:00:00Z",
        "citation_map": citation_map,
    }

    builder = RevisionBuilder(config)

    with zipfile.ZipFile(SOURCE) as source_archive:
        document = ET.fromstring(source_archive.read("word/document.xml"))
        settings = ET.fromstring(source_archive.read("word/settings.xml"))

    track = settings.find(W + "trackRevisions")
    if track is None:
        track = ET.SubElement(settings, W + "trackRevisions")
    track.set(W + "val", "true")

    body = document.find(W + "body")
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")

    paragraphs = [child for child in body if child.tag == W + "p"]

    # Apply Stage 1 paragraph replacements (with S1→S3 citation remapping)
    for key, replacement in stage1_config.get("paragraph_replacements", {}).items():
        index = int(key)
        if index < len(paragraphs):
            remapped = builder.remap_citations(replacement)
            builder.replace_paragraph(paragraphs[index], remapped)

    # Apply Stage 1 table replacements
    for key, replacement in stage1_config.get("table_replacements", {}).items():
        parts = key.split(":")
        table_index = int(parts[0])
        row_index = int(parts[1])
        tables = document.findall(".//" + W + "tbl")
        if table_index < len(tables):
            table = tables[table_index]
            rows = table.findall(W + "tr")
            if row_index < len(rows):
                row = rows[row_index]
                if len(parts) > 2:
                    cell_index = int(parts[2])
                    cells = row.findall(W + "tc")
                    if cell_index < len(cells):
                        builder.replace_paragraph(cells[cell_index], builder.remap_citations(replacement))
                else:
                    builder.replace_paragraph(row, builder.remap_citations(replacement))

    # Apply Stage 1 reference replacements
    reference_paragraphs = [p for p in paragraphs if re.match(r"^\d+\. ", builder.text(p))]
    for key, replacement in stage1_config.get("reference_replacements", {}).items():
        index = int(key)
        if index < len(reference_paragraphs):
            builder.replace_paragraph(reference_paragraphs[index], builder.remap_citations(replacement))

    # Load and apply Stage 2 replacements (texts use final S2/S3 numbers, no remap needed)
    import importlib.util
    spec = importlib.util.spec_from_file_location("apply_stage2", STAGE2 / "scripts" / "apply_stage2.py")
    stage2_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stage2_module)
    stage2_additions = stage2_module.load_stage2_additions()

    for key, replacement in stage2_additions["replacements"].items():
        index = int(key)
        if index < len(paragraphs):
            builder.replace_paragraph(paragraphs[index], replacement)

    for name, (after_index, text) in stage2_additions["insertions"].items():
        builder.insert_paragraph_after(body, after_index, text)

    # Apply Stage 3 replacements (texts use final S3 numbers, no remap)
    for key, replacement in s3_additions["replacements"].items():
        index = int(key)
        if index < len(paragraphs):
            builder.replace_paragraph(paragraphs[index], replacement)

    # Apply Stage 3 insertions
    for name, (after_index, text) in s3_additions["insertions"].items():
        builder.insert_paragraph_after(body, after_index, text)

    # Rebuild reference list from Stage 3 seed (69 refs)
    with (STAGE / "reference-seed.tsv").open(encoding="utf-8", newline="") as handle:
        ref_rows = list(csv.DictReader(handle, delimiter="\t"))

    ref_start = None
    for i, p in enumerate(paragraphs):
        if builder.text(p).strip() == "References":
            ref_start = i
            break

    if ref_start is not None:
        all_children = list(body)
        for child in all_children[ref_start + 1:]:
            body.remove(child)
        for row in ref_rows:
            ref_text = f"{row['order']}. {row['citation']}"
            ref_p = ET.SubElement(body, W + "p")
            ET.SubElement(ref_p, W + "pPr")
            ins = ET.SubElement(ref_p, W + "ins", builder.attributes())
            builder.append_run(ins, ref_text)

    # Replace Figure 1 with Stage 1 corrected figure
    with (STAGE1 / "assets" / "central-illustration-stage1.png").open("rb") as handle:
        revised_figure = handle.read()

    with zipfile.ZipFile(SOURCE) as source_archive:
        with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as output_archive:
            for item in source_archive.infolist():
                if item.filename == "word/document.xml":
                    output_archive.writestr(item, ET.tostring(document, encoding="UTF-8", xml_declaration=True))
                elif item.filename == "word/settings.xml":
                    output_archive.writestr(item, ET.tostring(settings, encoding="UTF-8", xml_declaration=True))
                elif item.filename == "word/media/image1.png":
                    output_archive.writestr(item, source_archive.read(item.filename))
                    figure_info = copy.copy(source_archive.getinfo("word/media/image1.png"))
                    figure_info.filename = "word/media/image2.png"
                    figure_info.orig_filename = figure_info.filename
                    output_archive.writestr(figure_info, revised_figure)
                else:
                    output_archive.writestr(item, source_archive.read(item.filename))

    with SOURCE.open("rb") as handle:
        source_hash = hashlib.sha256(handle.read()).hexdigest()
    expected = "8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1"
    if source_hash != expected:
        raise RuntimeError(f"Source hash mismatch: {source_hash} != {expected}")

    print(f"Stage 3 revised manuscript written to {OUTPUT}")
    print(f"Source SHA-256 verified: {source_hash}")
    print(f"References: {len(ref_rows)}")


if __name__ == "__main__":
    main()