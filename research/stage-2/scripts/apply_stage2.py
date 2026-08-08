#!/usr/bin/env python3
"""Stage 2 integrated OOXML transformer — reapplies Stage 1, overlays Stage 2 evidence."""

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
STAGE = REPO / "research" / "stage-2"
STAGE1 = REPO / "research" / "stage-1"
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
        if mapped is not None:
            return str(mapped)
        return value

    def remap_citations(self, text):
        def replace(match):
            parts = re.split(r"\s*[-,]\s*", match.group(1))
            remapped = [self.remap_reference_number(part) for part in parts]
            return "[" + ",".join(remapped) + "]"
        return CITATION.sub(replace, text)

    def insert_paragraph_after(self, body, after_index, text, run_properties=None):
        """Insert a new tracked paragraph after the given paragraph index."""
        insertion = ET.SubElement(body, W + "p")
        ET.SubElement(insertion, W + "pPr")
        ins = ET.SubElement(insertion, W + "ins", self.attributes())
        self.append_run(ins, text, run_properties=run_properties)
        # Move to correct position
        body.remove(insertion)
        body.insert(after_index + 1, insertion)


def load_stage1_config():
    with (STAGE1 / "revisions.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def load_stage2_additions():
    """Return paragraph insertions and replacements for Stage 2."""
    return {
        "insertions": {
            # After paragraph 17 (end of §1), insert M1 trigger-precedent paragraph
            "m1_trigger": (
                17,
                "The transient-trigger framework predates this review by decades. "
                "Muller and colleagues described circadian variation and morning clustering of acute cardiovascular events in 1989 [13]. "
                "Mittleman and Mostofsky later catalogued physical, psychological and chemical triggers acting on a susceptible substrate [14]. "
                "Smeeth and colleagues applied a self-controlled design to 20,486 patients with first myocardial infarction and reported "
                "a 4.95-fold incidence ratio (95% confidence interval 4.43-5.53) in the three days after a respiratory infection [15]. "
                "Warren-Gash and colleagues confirmed a similar temporal association using linked electronic health records [16], "
                "and Kwong and colleagues extended it to laboratory-confirmed influenza, reporting an incidence ratio of 6.05 "
                "(95% confidence interval 3.86-9.50) for myocardial infarction in the seven days after specimen collection [17]. "
                "The substrate-trigger distinction is therefore not new. The contribution of this review is to apply it to COPD "
                "as an organising synthesis that separates chronic susceptibility evidence from acute post-exacerbation risk evidence "
                "within the same clinical domain."
            ),
            # After paragraph 63 (BLOCK-COPD paragraph in §9.2), insert C4 beta-blocker trial evidence
            "c4_beta": (
                63,
                "Two subsequent trials tested beta-blockers in COPD without a cardiovascular indication. "
                "BICS randomised 519 patients with COPD at high exacerbation risk to bisoprolol or placebo; "
                "the primary analysis included 515 participants and reported an adjusted incidence-rate ratio of 0.97 "
                "(95% confidence interval 0.84-1.13, p=0.72) for treated exacerbations [39]. "
                "PACE randomised 280 patients with COPD and prior exacerbation to bisoprolol or placebo and reported "
                "a win ratio of 0.95 (95% confidence interval 0.72-1.25, p=0.72) for a hierarchical cardiopulmonary composite [40]. "
                "Neither trial tested patients with an established cardiovascular indication, and neither provides evidence "
                "for or against beta-blockade after myocardial infarction in COPD."
            ),
            # After paragraph 64 (post-MI beta-blocker paragraph), insert C4 post-MI trial evidence
            "c4_post_mi": (
                64,
                "Three contemporary trials examined beta-blockade after myocardial infarction in patients with preserved "
                "left ventricular ejection fraction. ABYSS tested interruption of established beta-blocker therapy "
                "a median of 2.9 years after infarction in 3,698 patients; noninferiority was not met "
                "(hazard ratio 1.16, 95% confidence interval 1.01-1.33) [44]. "
                "REBOOT randomised 8,438 patients with invasively managed infarction and ejection fraction greater than 40% "
                "to beta-blocker or no beta-blocker and reported a hazard ratio of 1.04 "
                "(95% confidence interval 0.89-1.22, p=0.63) for the primary composite [46]. "
                "BETAMI-DANBLOCK randomised 5,574 patients with infarction, ejection fraction at least 40%, and no heart failure "
                "and reported a hazard ratio of 0.85 (95% confidence interval 0.75-0.98, p=0.03) for all-cause death or major adverse cardiovascular events [45]. "
                "None of these trials tested a COPD-specific interaction, and their divergent results caution against "
                "a single summary statement about beta-blocker efficacy after infarction in patients with COPD."
            ),
            # After paragraph 69 (clinical implications vaccination), insert M2 influenza vaccination evidence
            "m2_vaccination": (
                69,
                "Influenza vaccination provides the strongest randomised evidence for cardiovascular event reduction "
                "in populations with established coronary disease. IAMI randomised 2,532 patients shortly after myocardial infarction "
                "to influenza vaccine or placebo and reported a hazard ratio of 0.72 (95% confidence interval 0.52-0.99, p=0.040) "
                "for the composite of all-cause death, myocardial infarction, or stent thrombosis at 12 months [49]. "
                "IVVE randomised 5,129 patients with heart failure in low-income and middle-income countries; "
                "neither co-primary endpoint showed a statistically significant reduction across the full follow-up "
                "(first co-primary hazard ratio 0.93, 95% confidence interval 0.81-1.07, p=0.30) [50]. "
                "A post-IVVE meta-analysis of six randomised trials including 9,340 patients reported a random-effects "
                "hazard ratio of 0.74 (95% confidence interval 0.63-0.88, p<0.001) for the cardiovascular composite, "
                "with moderate heterogeneity (I²=52%) [51]. "
                "A more recent mixed-design synthesis of 23 studies confirmed the direction of benefit but combined "
                "randomised and observational evidence and should not be interpreted as a causal trial estimate [52]. "
                "None of these studies tested a COPD-specific vaccination effect, and the evidence supports vaccination "
                "on cardiovascular grounds rather than through a COPD-specific mechanism."
            ),
            # After paragraph 78 (predictions anti-inflammatory), insert M3 anti-inflammatory trial evidence
            "m3_inflammation": (
                78,
                "The pathway-specificity of anti-inflammatory benefit is well established in populations without COPD. "
                "CANTOS demonstrated that canakinumab, a monoclonal antibody targeting interleukin-1β, reduced the composite "
                "of nonfatal myocardial infarction, nonfatal stroke, or cardiovascular death in 10,061 patients with prior "
                "myocardial infarction and residual inflammatory risk (hazard ratio 0.85, 95% confidence interval 0.74-0.98, "
                "p=0.021 for the 150 mg dose) [59]. "
                "CIRT tested low-dose methotrexate in 4,786 patients with prior infarction or multivessel coronary disease "
                "plus diabetes or metabolic syndrome and found no cardiovascular benefit (hazard ratio 0.96, "
                "95% confidence interval 0.79-1.16, p=0.67); methotrexate did not lower interleukin-1β, interleukin-6, "
                "or high-sensitivity C-reactive protein [60]. "
                "COLCOT demonstrated that low-dose colchicine started within 30 days after myocardial infarction reduced "
                "the primary composite endpoint (hazard ratio 0.77, 95% confidence interval 0.61-0.96, p=0.02) [61], "
                "and LoDoCo2 extended this finding to 5,522 patients with chronic coronary disease after a tolerance run-in "
                "(hazard ratio 0.69, 95% confidence interval 0.57-0.83, p<0.001) [62]. "
                "These trials establish that pathway-specific anti-inflammatory efficacy exists in coronary populations. "
                "They do not test whether COPD modifies the treatment effect, and the prediction that anti-inflammatory agents "
                "will behave identically in patients with and without COPD after stratification by coronary substrate "
                "remains a falsifiable hypothesis."
            ),
        },
        "replacements": {
            # Paragraph 17: replace novelty paragraph with calibrated version citing trigger precedent
            17: (
                "We propose that these findings measure processes operating over different timescales. "
                "A slow clock describes the cardiovascular substrate accumulated over decades through shared exposures "
                "and disease-specific pathways whose independent contribution remains uncertain. "
                "A fast clock describes the acute physiological and thrombotic stresses that follow an exacerbation. "
                "The transient-trigger concept is not new: Muller and colleagues described circadian variation "
                "and morning clustering of acute cardiovascular events in 1989 [13], and subsequent work established "
                "respiratory infections as short-term myocardial infarction triggers [15-17]. "
                "The contribution of this review is to apply that framework to COPD as an organising synthesis "
                "that separates chronic susceptibility evidence from acute post-exacerbation risk evidence "
                "within the same clinical domain, rather than placing unlike estimands on a common numerical scale."
            ),
            # Paragraph 63: replace BLOCK-COPD paragraph with expanded version
            63: (
                "BLOCK-COPD randomised exacerbation-prone patients with COPD, explicitly excluding anyone "
                "with an established indication for the drug, to extended-release metoprolol or placebo. "
                "It was stopped early for futility and safety. There was no difference in time to first exacerbation, "
                "and metoprolol was associated with a markedly higher risk of exacerbation requiring hospitalisation: "
                "hazard ratio 1.91 (1.29-2.83) [38]. "
                "BICS and PACE subsequently confirmed neutral results for bisoprolol in COPD without a cardiovascular "
                "indication, with adjusted incidence-rate ratios of 0.97 (0.84-1.13) and a win ratio of 0.95 (0.72-1.25) "
                "respectively [39,40]. None of these trials tested patients who required a beta-blocker for an established "
                "cardiac indication."
            ),
            # Paragraph 64: replace post-MI beta-blocker paragraph with expanded version
            64: (
                "Now take the same drug class to the same disease in patients who do have a cardiac indication. "
                "After myocardial infarction, β-blocker prescription at discharge in patients with COPD is not associated "
                "with excess mortality or adverse cardiopulmonary outcomes (hazard ratio 1.01, 0.66-1.54) [41]; "
                "population cohorts report reduced mortality [42]; and among 65,699 patients with COPD prescribed "
                "β-blockers after first infarction, cardioselective agents outperformed non-selective ones for mortality "
                "(hazard ratio 0.93), major adverse cardiac and cerebrovascular events (0.96), heart-failure hospitalisation "
                "(subdistribution hazard ratio 0.84) and major adverse pulmonary events (0.94) [43]. "
                "Three contemporary trials examined beta-blockade after infarction in patients with preserved ejection fraction. "
                "ABYSS did not meet noninferiority for interruption of established therapy (hazard ratio 1.16, 1.01-1.33) [44]. "
                "REBOOT found no benefit of initiation after invasively managed infarction (hazard ratio 1.04, 0.89-1.22) [46]. "
                "BETAMI-DANBLOCK reported a modest reduction in the primary composite (hazard ratio 0.85, 0.75-0.98) [45]. "
                "None of these trials tested a COPD-specific interaction."
            ),
            # Paragraph 69: replace clinical implications vaccination paragraph
            69: (
                "In the patient with stable COPD, cardiovascular risk should be assessed and treated on cardiovascular grounds, "
                "using conventional tools, and not deferred because the dyspnoea has a respiratory label. This is the slow clock, "
                "and it responds to slow-clock medicine. There is no evidence supporting cardiovascular drugs beyond established "
                "cardiovascular indications in order to improve COPD outcomes [47], and BLOCK-COPD is a warning against trying [38]. "
                "Conversely, exacerbation prevention: vaccination, appropriate inhaled therapy, pulmonary rehabilitation, "
                "smoking cessation, should be understood as cardiovascular prevention in the exacerbation-prone patient, "
                "which is how the ETHOS signal is best read and how the recent cardiopulmonary-risk framing has begun to move [35,47,48]. "
                "Influenza vaccination provides the strongest randomised evidence: IAMI reported a hazard ratio of 0.72 "
                "(0.52-0.99) for the cardiovascular composite after myocardial infarction [49], and a post-IVVE meta-analysis "
                "of six trials reported a pooled hazard ratio of 0.74 (0.63-0.88) [51]. These trials support vaccination "
                "on cardiovascular grounds; they do not test a COPD-specific mechanism."
            ),
            # Paragraph 78: replace predictions anti-inflammatory paragraph
            78: (
                "It predicts that β-blocker benefit in COPD tracks cardiac indication and not COPD severity, "
                "and that trials enrolling patients with substrate will not reproduce BLOCK-COPD's harm signal. "
                "It predicts that anti-inflammatory agents with proven atherothrombotic efficacy, low-dose colchicine, "
                "interleukin-1β or interleukin-6 pathway inhibition, will behave in COPD as they behave in anyone else "
                "with the same coronary substrate, with no COPD-specific increment. "
                "CANTOS, COLCOT, and LoDoCo2 established pathway-specific anti-inflammatory benefit in coronary populations "
                "without COPD [59,61,62], while CIRT demonstrated that a generic anti-inflammatory label does not predict "
                "cardiovascular efficacy when the intervention fails to suppress the interleukin-1β to interleukin-6 to "
                "C-reactive protein axis [60]. A COPD-specific treatment-effect increment would be direct evidence "
                "of a shared inflammatory mechanism and would substantially revive the hypothesis this review rejects."
            ),
        },
    }


def build_citation_map():
    """Build the S1→S2 citation map with variable shifts.

    Stage 2 seed inserts new refs at multiple positions:
      13-17:  M1 trigger precedent (Muller, Mittleman, Smeeth, Warren-Gash, Kwong)  → +5 for old 13+
      39-40:  C4 COPD beta-blocker trials (BICS, PACE)                               → +7 for old 34+
      44-46:  C4 post-MI beta-blocker trials (ABYSS/REBOOT, BETAMI-DANBLOCK)        → +10 for old 37+
      49-52:  M2 influenza vaccination (IAMI, IVVE, Modin, Hosseini)               → +14 for old 39+
      59-62:  M3 anti-inflammatory (CANTOS, CIRT, COLCOT, LoDoCo2)                  → +18 for old 39+ (but +14 already applied)

    Actual shifts by S1 ref range:
      S1[1-12]  → S2[1-12]    (shift +0)
      S1[13-33] → S2[18-38]   (shift +5)
      S1[34-36] → S2[41-43]   (shift +7)
      S1[37-38] → S2[47-48]   (shift +10)
      S1[39-44] → S2[53-58]   (shift +14)
    """
    citation_map = {}
    # Old refs 1-12: no shift
    for old in range(1, 13):
        citation_map[str(old)] = str(old)
    # Old refs 13-33: shift +5 (M1 inserts 5 refs at 13-17)
    for old in range(13, 34):
        citation_map[str(old)] = str(old + 5)
    # Old refs 34-36: shift +7 (BICS+PACE insert 2 refs at 39-40)
    for old in range(34, 37):
        citation_map[str(old)] = str(old + 7)
    # Old refs 37-38: shift +10 (ABYSS/REBOOT/BETAMI insert 3 refs at 44-46)
    for old in range(37, 39):
        citation_map[str(old)] = str(old + 10)
    # Old refs 39-44: shift +14 (IAMI/IVVE/Modin/Hosseini insert 4 refs at 49-52)
    for old in range(39, 45):
        citation_map[str(old)] = str(old + 14)
    # Identity mapping for new S2 refs is NOT needed because Stage 2 texts use S2 numbers directly
    # and only Stage 1 text (which uses S1 numbers) goes through remap_citations.
    return citation_map


def main():
    # Load Stage 1 config
    stage1_config = load_stage1_config()
    stage2_additions = load_stage2_additions()
    citation_map = build_citation_map()

    config = {
        "revision_author": "Hendri Susilo",
        "revision_date": "2026-08-07T23:00:00Z",
        "citation_map": citation_map,
        "paragraph_replacements": {
            **{str(k): v for k, v in stage1_config.get("paragraph_replacements", {}).items()},
            **{str(k): v for k, v in stage2_additions["replacements"].items()},
        },
        "table_replacements": stage1_config.get("table_replacements", {}),
        "reference_replacements": stage1_config.get("reference_replacements", {}),
    }

    builder = RevisionBuilder(config)

    with zipfile.ZipFile(SOURCE) as source_archive:
        document = ET.fromstring(source_archive.read("word/document.xml"))
        settings = ET.fromstring(source_archive.read("word/settings.xml"))

    # Enable track revisions
    track = settings.find(W + "trackRevisions")
    if track is None:
        track = ET.SubElement(settings, W + "trackRevisions")
    track.set(W + "val", "true")

    body = document.find(W + "body")
    if body is None:
        raise RuntimeError("word/document.xml has no w:body")

    paragraphs = [child for child in body if child.tag == W + "p"]

    # Apply Stage 1 paragraph replacements (with S1→S2 citation remapping)
    s1_replacements = {str(k): v for k, v in stage1_config.get("paragraph_replacements", {}).items()}
    for key, replacement in s1_replacements.items():
        index = int(key)
        if index < len(paragraphs):
            remapped = builder.remap_citations(replacement)
            builder.replace_paragraph(paragraphs[index], remapped)

    # Apply Stage 2 replacements (texts already use final S2 citation numbers, no remap)
    for key, replacement in stage2_additions["replacements"].items():
        index = int(key)
        if index < len(paragraphs):
            builder.replace_paragraph(paragraphs[index], replacement)

    # Apply Stage 2 insertions (texts already use final S2 citation numbers, no remap)
    for name, (after_index, text) in stage2_additions["insertions"].items():
        builder.insert_paragraph_after(body, after_index, text)

    # Apply table replacements (Stage 1)
    for key, replacement in config["table_replacements"].items():
        parts = key.split(":")
        table_index = int(parts[0])
        row_index = int(parts[1])
        tables = document.findall(".//" + W + "tbl")
        table = tables[table_index]
        rows = table.findall(W + "tr")
        if row_index < len(rows):
            row = rows[row_index]
            if len(parts) > 2:
                # Cell-level replacement
                cell_index = int(parts[2])
                cells = row.findall(W + "tc")
                if cell_index < len(cells):
                    builder.replace_paragraph(cells[cell_index], builder.remap_citations(replacement))
            else:
                builder.replace_paragraph(row, builder.remap_citations(replacement))

    # Replace reference paragraphs (Stage 1)
    reference_paragraphs = [p for p in paragraphs if re.match(r"^\d+\. ", builder.text(p))]
    for key, replacement in config["reference_replacements"].items():
        index = int(key)
        if index < len(reference_paragraphs):
            builder.replace_paragraph(reference_paragraphs[index], builder.remap_citations(replacement))

    # Build final 62-reference list
    with (STAGE / "reference-seed.tsv").open(encoding="utf-8", newline="") as handle:
        ref_rows = list(csv.DictReader(handle, delimiter="\t"))

    # Find the reference section start
    ref_start = None
    for i, p in enumerate(paragraphs):
        if builder.text(p).strip() == "References":
            ref_start = i
            break

    if ref_start is not None:
        # Remove ALL paragraphs after "References" heading (old refs + any tracked insertions)
        all_children = list(body)
        for child in all_children[ref_start + 1:]:
            body.remove(child)

        # Add new 62 reference paragraphs
        for row in ref_rows:
            ref_text = f"{row['order']}. {row['citation']}"
            ref_p = ET.SubElement(body, W + "p")
            ET.SubElement(ref_p, W + "pPr")
            ins = ET.SubElement(ref_p, W + "ins", builder.attributes())
            builder.append_run(ins, ref_text)

    # Replace Figure 1 (Stage 1)
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
                    # Add replacement image
                    figure_info = copy.copy(source_archive.getinfo("word/media/image1.png"))
                    figure_info.filename = "word/media/image2.png"
                    figure_info.orig_filename = figure_info.filename
                    output_archive.writestr(figure_info, revised_figure)
                else:
                    output_archive.writestr(item, source_archive.read(item.filename))

    # Verify source hash
    with SOURCE.open("rb") as handle:
        source_hash = hashlib.sha256(handle.read()).hexdigest()
    expected = "8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1"
    if source_hash != expected:
        raise RuntimeError(f"Source hash mismatch: {source_hash} != {expected}")

    print(f"Stage 2 revised manuscript written to {OUTPUT}")
    print(f"Source SHA-256 verified: {source_hash}")


if __name__ == "__main__":
    main()
