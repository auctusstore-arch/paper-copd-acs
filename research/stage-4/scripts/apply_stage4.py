#!/usr/bin/env python3
"""Stage 4 OOXML transformer — presentation corrections (P1-P7)."""

import copy
import csv
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
STAGE = REPO / "research" / "stage-4"
STAGE1 = REPO / "research" / "stage-1"
STAGE2 = REPO / "research" / "stage-2"
STAGE3 = REPO / "research" / "stage-3"
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


def stage4_replacements():
    """Stage 4 paragraph replacements for em-dash removal, American→British, and rhetorical tic cleanup.

    These replace ORIGINAL paragraphs that were not touched by Stages 1-3.
    All citations use S1 numbers and will be remapped via citation_map.
    """
    return {
        # Para 7: Replace original keywords with British English version
        7: (
            "Keywords: chronic obstructive pulmonary disease; acute coronary syndrome; "
            "type 2 myocardial infarction; self-controlled case series; Mendelian randomisation; "
            "population attributable fraction; exacerbation; cardiovascular risk"
        ),
        # Para 6: Introduction — fix em-dash + "Randomized" → "Randomised"
        6: (
            "Cardiovascular disease is the leading cause of death in COPD, and the risk is not fully explained "
            "by smoking or shared exposures. Epidemiological studies report a 1.5- to 3-fold increased risk of "
            "cardiovascular events in COPD patients even after adjustment for traditional risk factors [1,2]. "
            "The excess reflects shared exposures, including smoking, ageing, adiposity, and inflammation, "
            "but COPD also contributes independently through systemic inflammation, hypoxaemia, and "
            "exacerbation-related physiological stress. Randomised trials have shown no cardiovascular benefit "
            "of inhaled corticosteroids or bronchodilators beyond their respiratory effects [5,6], while "
            "Mendelian randomisation studies yield effect estimates that are statistically significant but "
            "biologically modest [7]. We argue that the field has been asking the wrong question: not whether "
            "COPD causes cardiovascular disease, but how the two processes interact across timescales."
        ),
        # Para 15: fix em-dash
        15: (
            "The evidence base for this review is large but uneven. Observational cohorts dominate the "
            "chronic association literature, self-controlled case series dominate the trigger literature, "
            "and randomised trials address only a narrow strip of the question. The result is a body of "
            "evidence that is individually persuasive but collectively incomplete, wrong, or at least wrong "
            "about what it can tell us. We triangulate across designs rather than pooling within one."
        ),
        # Para 16: fix em-dashes (the OR 1.004 paragraph — already replaced by Stage 1, but check)
        # Para 18: fix em-dashes + "the point with clinical teeth" tic
        18: (
            "Our argument is that these findings do not conflict. They are measurements of two different "
            "processes that the field has insisted on treating as one. We propose the two-clock model: "
            "a slow clock that builds substrate over decades, driven largely by exposures shared with "
            "cardiovascular disease rather than by pulmonary inflammation; and a fast clock that converts "
            "an exacerbation into an acute event over days, through physiology rather than atherogenesis. "
            "The clocks differ in timescale, in mechanism, and in what modifies them. The clinical "
            "implication is that each clock responds to a different class of intervention: the slow clock "
            "to cardiovascular risk modification, the fast clock to exacerbation prevention."
        ),
        # Para 21: fix em-dashes + "Randomized" → "Randomised"
        21: (
            "Shared mediators do not establish a shared causal pathway. Interleukin-6 is elevated in COPD "
            "and in atherosclerosis; it is also elevated in rheumatoid arthritis, periodontitis, obesity "
            "and ageing. The relevant question is not whether the same molecules appear in both compartments "
            "but whether flux from one compartment to the other is a quantitatively important cause of "
            "events in the other. That question is answerable by triangulation across designs: "
            "randomised trials, genetic instruments, and self-controlled case series each test a different "
            "aspect of the hypothesis [10]."
        ),
        # Para 25: fix em-dashes
        25: (
            "In the coronary artery, an overlapping cast of cytokines, including interleukin-1\u03b2, "
            "interleukin-6, interferon-\u03b3, MMP-9, and nuclear factor \u03baB signalling, governs fibrous "
            "cap integrity, and the same molecules are released from inflamed airways during exacerbation. "
            "The spillover hypothesis holds that this molecular overlap is causal in both directions: "
            "pulmonary inflammation promotes atherogenesis, and acute exacerbation destabilises plaques."
        ),
        # Para 26: fix "answerable, and it has been answered" tic
        26: (
            "What is disputed, or ought to be, is the inference drawn from the coincidence. Shared mediators "
            "do not establish a shared causal pathway. Interleukin-6 is elevated in COPD and in atherosclerosis; "
            "it is also elevated in rheumatoid arthritis, periodontitis, obesity and ageing. The relevant "
            "question is not whether the same molecules appear in both compartments but whether flux from "
            "one compartment to the other is a quantitatively important cause of events in the other. "
            "Triangulation across designs can address this question [10]."
        ),
        # Para 35: fix em-dash
        35: (
            "Yu and colleagues reported a bidirectional genetic instrument for COPD and cardiovascular disease, "
            "with an odds ratio of 1.004 (95% confidence interval 1.002-1.006) for coronary heart disease "
            "per genetically predicted COPD liability [7]. The estimate is nominally significant but biologically "
            "modest, and it operates on a liability scale that is not directly comparable with observational "
            "effect estimates of 2- to 5-fold."
        ),
        # Para 36: fix em-dash + "Randomized" → "Randomised"
        36: (
            "Multivariable analyses sharpen the point. In a multivariable Mendelian randomisation analysis "
            "by Yu and colleagues, body mass index, smoking initiation, and smoking status did not attenuate "
            "the COPD to coronary heart disease association; interleukin-6, low-density lipoprotein, and "
            "total cholesterol did [7]. This pattern is consistent with mediation through inflammatory and "
            "lipid pathways rather than confounding by shared exposures. FEV1 was not included in the "
            "multivariable model; it is a mediator of COPD, not a confounder of the COPD to cardiovascular "
            "association. The same direction the randomised trials point: reducing pulmonary inflammation "
            "alone does not reduce cardiovascular events [5,6]."
        ),
        # Para 39: fix em-dashes
        39: (
            "The self-controlled case series compares the rate of cardiovascular events during a defined "
            "window after exacerbation to the rate during baseline time in the same individual. "
            "Time-invariant characteristics, including smoking history, genotype, sex, socioeconomic position, "
            "and baseline comorbidity, cannot confound the comparison, because each person serves as their "
            "own control. The design is well suited to detecting transient triggers."
        ),
        # Para 40: fix em-dash
        40: (
            "Rothnie and colleagues reported a 2.58-fold incidence rate ratio for myocardial infarction "
            "in the 91 days after severe exacerbation and 1.58 for moderate exacerbation, with the highest "
            "risk in the first three days (incidence rate ratio 8.00, 95% confidence interval 5.81-11.01) [12]. "
            "The signal rises within days and decays over weeks, a signature that a decades-long atherogenic "
            "process alone cannot produce."
        ),
        # Para 43: fix em-dashes
        43: (
            "The chronic association is confounded by shared exposures. Tobacco above all, with ageing, "
            "adiposity, and socioeconomic position, drives both COPD and cardiovascular disease. "
            "Conventional adjustment leaves residual confounding because these exposures are measured "
            "imperfectly and because COPD itself modifies cardiovascular risk through pathways that are "
            "not captured by adjustment variables."
        ),
        # Para 45: fix em-dash
        45: (
            "Post-exacerbation cardiovascular events are predominantly type 2 myocardial infarction and "
            "acute myocardial injury, with type 1 myocardial infarction, plaque rupture with atherothrombosis, "
            "accounting for a smaller proportion [12,29]. The NSTEMI to STEMI ratio in the Rothnie data "
            "(incidence rate ratio 1.80 versus 1.39) is consistent with a supply-demand mechanism rather "
            "than plaque rupture as the dominant acute pathway."
        ),
        # Para 46: fix em-dashes
        46: (
            "The two-clock model organises this evidence. One asymmetry, the chronic channel confounded by "
            "shared exposures while the acute channel is not, separates the two clocks. The slow clock is "
            "built by atherogenesis over decades and is difficult to isolate causally. The fast clock is "
            "triggered by exacerbation over days and is amenable to self-controlled designs."
        ),
        # Para 50: fix em-dashes
        50: (
            "The reflex that dominates cardiology practice, troponin rise plus dyspnoea equals acute coronary "
            "syndrome, is wrong more often than it is right in COPD. Troponin elevation during exacerbation "
            "is common, but the mechanism is frequently type 2 myocardial infarction or acute myocardial "
            "injury rather than plaque rupture [29,30,31]. Among patients with exacerbation and raised "
            "troponin who underwent angiography, 67% had significant coronary disease [33], but this does "
            "not establish that the exacerbation caused plaque rupture."
        ),
        # Para 52: fix "Honesty requires" tic + em-dash
        52: (
            "In acute exacerbation, troponin rises in a large proportion of patients, and the differential "
            "is wide: right ventricular strain from hyperinflation and hypoxic pulmonary vasoconstriction, "
            "tachycardia, pulmonary embolism, left ventricular dysfunction, and undiagnosed coronary disease "
            "all produce it [30,31,32]. The partition is not clean in either direction. Among 88 patients "
            "admitted with exacerbation and raised troponin who underwent angiography, 67% had significant "
            "coronary disease [33]. The DEMAND-MI study found that 68% of patients with adjudicated type 2 "
            "myocardial infarction had coronary artery disease, previously unrecognised in 60% [29]. "
            "This supports a low threshold for coronary assessment in COPD patients with troponin elevation, "
            "not reflexive attribution to supply-demand mismatch."
        ),
        # Para 54: fix em-dash
        54: (
            "The diagnostic corollary is that the default interpretation of troponin elevation in COPD, "
            "type 2 myocardial infarction from supply-demand mismatch, should trigger a search for coronary "
            "disease rather than a reflexive discharge label. The patient whose troponin is elevated by "
            "right ventricular strain, the one with regional wall-motion abnormality, not the one whose "
            "troponin is elevated by demand ischaemia alone, is the one who benefits from angiography [33]."
        ),
        # Para 61: fix em-dash
        61: (
            "ETHOS reported a post hoc signal for reduced cardiovascular events with triple therapy, "
            "but the magnitude is modest and the analysis is exploratory [35]. SUMMIT, the only trial "
            "powered for mortality, reported a cardiovascular composite hazard ratio of 0.93 "
            "(95% confidence interval 0.75-1.14) [5]. The lower confidence interval bound permits a "
            "25% relative benefit; the trial was underpowered for this endpoint. A bronchodilator "
            "effect on cardiovascular outcomes, independent of inhaled corticosteroid, remains possible "
            "and is given weight by the meta-analysis of Yang and colleagues [37]."
        ),
        # Para 71: fix em-dashes
        71: (
            "In the patient in whom both clocks are active, the common case, the discipline is to classify "
            "the mechanism: is the event atherothrombotic, triggered by substrate, or is it a supply-demand "
            "mismatch, triggered by exacerbation? The classification determines the intervention."
        ),
        # Para 77: fix em-dashes
        77: (
            "The model also generates predictions that are directly testable. A troponin-positive exacerbation "
            "should be investigated by angiography, intracoronary imaging, or functional testing, not "
            "discharged as supply-demand mismatch without further assessment [33]. The yield of such "
            "assessment is predicted to be high given that 68% of type 2 myocardial infarction patients "
            "have underlying coronary artery disease [29]."
        ),
        # Para 86: fix em-dashes + "randomized" → "randomised"
        86: (
            "The fast clock can be tested directly: a randomised trial of exacerbation prevention, "
            "powered for cardiovascular endpoints, would provide a causal estimate. The influenza "
            "vaccination trials approximate this design: IAMI reported a hazard ratio of 0.72 "
            "(95% confidence interval 0.52-0.99) for the cardiovascular composite after myocardial "
            "infarction [49], and a post-IVVE meta-analysis of six trials reported a pooled hazard "
            "ratio of 0.74 (0.63-0.88) [51]. These trials support vaccination on cardiovascular grounds "
            "but do not test a COPD-specific mechanism."
        ),
        # Para 87: fix em-dashes
        87: (
            "The slow clock remains in the shadow of shared causation: tobacco, ageing, adiposity, "
            "and socioeconomic position confound every observational estimate. The Mendelian randomisation "
            "instruments are statistically significant but biologically modest, and the liability-scale "
            "odds ratio is not comparable with observational effect estimates. The fast clock, by contrast, "
            "is amenable to self-controlled designs that remove time-invariant confounding, and the "
            "population attributable fraction of 15-25% quantifies its contribution."
        ),
        # Para 88: fix "central error" tic + em-dash
        88: (
            "Two clocks, running at different speeds, producing different events, answering to different "
            "treatments. The field has treated them as one, and the trial record shows the cost of that "
            "conflation. Separating them predicts the trial record, explains the beta-blocker reversal "
            "that no inflammatory account anticipates, and generates experiments that could show the "
            "model to be wrong, which is the only property that makes it worth proposing."
        ),
    }


def stage4_insertions():
    """Stage 4 insertions: front/back matter, abstract calibration, keywords."""
    return {
        # P6: Abstract calibration — insert at the very beginning (before paragraph 0)
        # Actually, we'll insert after paragraph 0 (title) as a new abstract paragraph
        # P7: Keywords — insert after abstract
        "keywords": (
            1,
            "Keywords: chronic obstructive pulmonary disease; acute coronary syndrome; "
            "type 2 myocardial infarction; self-controlled case series; Mendelian randomisation; "
            "population attributable fraction; exacerbation; cardiovascular risk"
        ),
        # P4: Front matter — insert after keywords
        "front_matter": (
            2,
            "Author contributions: H.S. conceived the review, conducted the literature search, "
            "synthesised the evidence, and wrote the manuscript. "
            "Funding: This review received no external funding. "
            "Conflicts of interest: The author declares no conflicts of interest. "
            "Data availability: All data are available from the cited published sources. "
            "The population attributable fraction calculation script is available from the "
            "corresponding author on reasonable request. "
            "Use of artificial intelligence: AI-assisted tools were used for literature retrieval "
            "and manuscript drafting. All content was reviewed, verified, and edited by the author, "
            "who takes full responsibility for the integrity of the work."
        ),
        # P1: Central illustration brief — insert after §7 two-clock model section
        "figure_brief": (
            47,
            "Figure 1 note: This is a conceptual schematic, not a quantitative plot. "
            "Panel A shows the slow clock as atherogenesis over decades. "
            "Panel B shows the fast clock as exacerbation-triggered events over days. "
            "Panel C separates observational, genetic, and acute-trigger evidence into non-quantitative "
            "lanes to avoid comparing unlike estimands on a common numerical scale. "
            "Panel D shows the interaction of both clocks in the individual patient."
        ),
    }


def main():
    stage1_config = load_stage1_config()
    s4_replacements = stage4_replacements()
    s4_insertions = stage4_insertions()
    citation_map = build_s1_to_s3_map()

    config = {
        "revision_author": "Hendri Susilo",
        "revision_date": "2026-08-08T18:00:00Z",
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

    # 1. Apply Stage 1 paragraph replacements (with S1→S3 citation remapping)
    for key, replacement in stage1_config.get("paragraph_replacements", {}).items():
        index = int(key)
        if index < len(paragraphs):
            remapped = builder.remap_citations(replacement)
            builder.replace_paragraph(paragraphs[index], remapped)

    # 2. Apply Stage 1 table replacements
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

    # 3. Apply Stage 1 reference replacements
    reference_paragraphs = [p for p in paragraphs if re.match(r"^\d+\. ", builder.text(p))]
    for key, replacement in stage1_config.get("reference_replacements", {}).items():
        index = int(key)
        if index < len(reference_paragraphs):
            builder.replace_paragraph(reference_paragraphs[index], builder.remap_citations(replacement))

    # 4. Load and apply Stage 2 (no remap, texts use final S2/S3 numbers)
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

    # 5. Load and apply Stage 3 (no remap)
    spec3 = importlib.util.spec_from_file_location("apply_stage3", STAGE3 / "scripts" / "apply_stage3.py")
    stage3_module = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(stage3_module)
    stage3_additions = stage3_module.stage3_additions()

    for key, replacement in stage3_additions["replacements"].items():
        index = int(key)
        if index < len(paragraphs):
            builder.replace_paragraph(paragraphs[index], replacement)

    for name, (after_index, text) in stage3_additions["insertions"].items():
        builder.insert_paragraph_after(body, after_index, text)

    # 6. Apply Stage 4 replacements (em-dash cleanup, tics, British English)
    # These replace ORIGINAL paragraphs with S1 citation numbers, so remap
    for key, replacement in s4_replacements.items():
        index = int(key)
        if index < len(paragraphs):
            remapped = builder.remap_citations(replacement)
            builder.replace_paragraph(paragraphs[index], remapped)

    # 6b. Fix remaining American spellings in unreplaced body paragraphs
    # Only fix in body text, NOT in reference list (paper titles may use American spelling)
    ref_start_idx = None
    for i, p in enumerate(paragraphs):
        if builder.text(p).strip() == "References":
            ref_start_idx = i
            break
    if ref_start_idx is None:
        ref_start_idx = len(paragraphs)
    for p in paragraphs[:ref_start_idx]:
        for t_node in p.iter(W + "t"):
            if t_node.text and "randomization" in t_node.text:
                t_node.text = t_node.text.replace("randomization", "randomisation")
            if t_node.text and "randomized" in t_node.text:
                t_node.text = t_node.text.replace("randomized", "randomised")

    # 7. Apply Stage 4 insertions (keywords, front matter, figure brief)
    for name, (after_index, text) in s4_insertions.items():
        builder.insert_paragraph_after(body, after_index, text)

    # 8. Rebuild reference list from Stage 3 seed (69 refs)
    with (STAGE3 / "reference-seed.tsv").open(encoding="utf-8", newline="") as handle:
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

    # 9. Replace Figure 1 with Stage 1 corrected figure
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

    print(f"Stage 4 revised manuscript written to {OUTPUT}")
    print(f"Source SHA-256 verified: {source_hash}")
    print(f"References: {len(ref_rows)}")


if __name__ == "__main__":
    main()