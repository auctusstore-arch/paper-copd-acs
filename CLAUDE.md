# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Not a codebase. This is a manuscript revision workspace for one narrative review:

**"Beyond Inflammatory Spillover: A Two-Clock Model of Cardiovascular Risk in Chronic Obstructive Pulmonary Disease"** by Hendri Susilo (Universitas Airlangga, Dept. of Cardiology and Vascular Medicine). Single author, 13 sections, 36 references, ~6,900 words, one central illustration (4 panels) and 5 tables.

The user (dr. Muhammad Yusuf) was asked by his supervisor to fix this paper. A peer-review audit found it to be AI-generated draft quality with integrity-level defects. The work is: revise against the checklist, de-slop the prose, and expand the discussion with the supplied literature.

## Directory map

| Path | Contents |
|---|---|
| `Manuskrip/` | The original manuscript, `.docx`, single file. **Read-only.** Never edit, overwrite, or Save-As over this file. |
| `Checklist revisi/checklist_revisi_two_clock.html` | The peer-review report: 33 revision items in 5 stages. **Source of truth for what to fix.** Item data lives in the `STAGES` array inside the `<script>` at line 276, not in the visible HTML. |
| `Contoh review article/main.pdf` | Style exemplar: Heffernan & Rutherford, *CJC Open* 2025;7:493-507, "The Intersection of COPD and Cardiovascular Disease". Match this register, not the current manuscript's. |
| `Rangkuman consensus/` | Two AI-generated literature syntheses (COPD-MI correlation/causation; exacerbation-ACS). Use as leads to primary sources, never cite them. |
| `Jurnal bacaan/` | 11 primary-source PDFs for expanding the discussion (see below). |
| `stop-slop-main/` | Vendored copy of the stop-slop skill. `SKILL.md` plus `references/{phrases,structures,examples}.md`. |

### Jurnal bacaan inventory

- `01091-2024.pdf` Nordon et al., ERJ Open Res 2024. EXACOS-CV meta-analyses, sustained CV risk after exacerbation.
- `rccm.202307-1122OC.pdf` Graul et al., AJRCCM 2024;209:960-72. Temporal risk of nonfatal CV events post-exacerbation.
- `main.pdf` Wallström et al., Chest. Exacerbation history, MI **and pulmonary embolism** risk. Directly relevant to checklist item M11.
- `10.1177_17534666221113647.pdf` Müllerová & Marshall, Ther Adv Respir Dis 2022. SR/MA of exacerbations and acute CV events.
- `jcm-13-05173.pdf` Sá-Sousa et al., J Clin Med 2024. Systematic review, CV risk in COPD.
- `copd-20-2549.pdf` Ioannides, Whittaker, Quint. MACE and cause-specific mortality after COPD hospitalisation.
- `copd-20-1435.pdf` Meng et al. Obstructive airway disease and CVD risk independent of phenotype.
- `424_2024_Article_3013.pdf` Gillan et al., Pflügers Arch 2025. Immune mediators in heart-lung communication (mechanism/spillover side).
- `pone.0265682.pdf` Svendsen et al., PLOS ONE. Factors associated with CHD in COPD patients and controls.
- `fcvm-11-1362564.pdf` Front Cardiovasc Med 2024, inflammation as nexus between AMI and COPD.
- `jcm-13-07324.pdf` von Lewinski et al. Air pollution and MI, smoker's paradox.

Note: several papers the checklist demands (IAMI, BICS, PACE, Au Yeung 2022, Higbee 2021, CANTOS/CIRT/COLCOT, DETO2X-AMI, Smeeth 2004, Kwong 2018) are **not** in `Jurnal bacaan/`. Those need retrieval before the corresponding items can be closed.

## Manuscript structure

Sections are `Heading1`-styled paragraphs numbered 1-13. Subsections (9.1, 9.2) are plain paragraphs with manual numbering, not styled headings. Any new subsection (M6 asks for a new §7.1, C5 for a new sub-section in §6) must follow that convention.

1. Introduction  2. Scope/evidence appraisal  3. What the diseases share  4. Spillover tested both directions  5. Chronic association confounded  6. Exacerbation as trigger  7. The two-clock model  8. Diagnostic corollary  9. Testing against the trial record  10. Clinical implications  11. Predictions and refutation  12. Limitations  13. Conclusion

Tables: T1 two clocks anatomy · T2 evidence by design · T3 mechanisms of cardiac injury in AECOPD · T4 trials read as clock-matching · T5 falsifiable predictions.

## Revision workflow

The checklist is gated. Work the stages in order and do not reorder:

- **Tahap 1 (Integritas)** C1, C2, C3, C7a, C7b. Factual misrepresentation and reference integrity. **C1 and C2 are hard gates**: the review verdict stays at Major Revision on the edge of reject until both are corrected, regardless of what else is done.
- **Tahap 2 (Bukti yang hilang)** M2, C4, M3, M1, M9, M10. Missing trials and MR studies.
- **Tahap 3 (Metodologi)** C5, C6, M6, M7, M8, M4, M5, F1, M11, M12, M13, M14. M6 (population attributable fraction for the fast clock) is the single highest-value addition.
- **Tahap 4 (Presentasi)** P1-P7. Do not start until substance is settled; these polish text that Tahap 1-3 will rewrite.
- **Tahap 5 (Struktural)** S1 co-author, S2 target journal, S3 response letter.

Counts: 8 kritis, 16 mayor, 9 minor.

Two defects recur and must never be reintroduced:
- **Do not fabricate or leave placeholder citations.** 17 lines in the current reference list carry `[to be verified]` / `[to be completed]` markers. Every reference must be checked against PubMed/DOI before it stays. This is item C7a and it is what will trigger a research-integrity review rather than a revision request.
- **Do not restate a source's findings from memory.** C1 exists because the manuscript claims ref [7] (Yu 2024) found something it did not. When touching any claim tied to a specific paper, read the paper.

## Writing standards

Three constraints stack, in this order of precedence:

1. **User global rule: no em dashes anywhere.** The current manuscript is full of them. Replace with a comma, semicolon, colon, or a sentence break.
2. **stop-slop** (`stop-slop-main/SKILL.md`, read `references/phrases.md` and `references/structures.md` before editing prose). Cut filler, kill adverbs, active voice, no "not X but Y" contrasts, no rule of three, no punchy one-line paragraph endings, vary sentence length.
3. **Academic register from the exemplar.** The current draft's rhetorical tics are named in checklist item P3: "Honesty requires acknowledging", "the point with clinical teeth", "The field's central error", "answerable, and it has been answered". P3 also asks for a ~20% prose cut and consolidation of §4-§6, which repeat the same material three times.

Where stop-slop and journal convention conflict, journal convention wins. Reviews use "we", hedge causal claims deliberately, and cite rather than assert. Stop-slop's "put the reader in the room / use you" rule does not apply to a Q1 manuscript.

Manuscript body text is British English (`randomised`, `hypoxaemia`, `dyslipidaemia`). Keep it consistent.

## Working with the files

`python3` is blocked by a hook in this environment. Use `uv run python3` for every Python invocation, and `uv run --with <pkg> python3` when a package is needed.

Extract the manuscript to plain text (styles preserved as `[Heading1]` prefixes):

```bash
uv run python3 -c "
import zipfile
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
z=zipfile.ZipFile('Manuskrip/COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx')
root=ET.fromstring(z.read('word/document.xml'))
for p in root.iter(W+'p'):
    t=''.join(x.text or '' for x in p.iter(W+'t'))
    pPr=p.find(W+'pPr'); s=''
    if pPr is not None:
        ps=pPr.find(W+'pStyle')
        if ps is not None: s=ps.get(W+'val')
    if t.strip(): print(f'[{s}] {t}' if s else t)
"
```

PDFs: `pdftotext` is installed and works on all files here. `pypdf` returns empty text on these PDFs, so prefer `pdftotext`.

```bash
pdftotext "Jurnal bacaan/rccm.202307-1122OC.pdf" -
```

Reading the checklist items: dump the `STAGES` array rather than the rendered page.

```bash
sed -n '277,435p' "Checklist revisi/checklist_revisi_two_clock.html"
```

Editing: `Manuskrip/COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx` is **read-only** — the source paper as handed off by the supervisor. Never write to it. All revision work happens in a **new, separate `.docx`** (e.g. `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx` or similarly named). Create that new file by copying the original first, then edit the copy. Use the `docx` skill (`Skill` tool, `anthropic-skills:docx`) for the edit itself; it handles tracked changes and comments, which the supervisor will expect on a revision. The file contains one image (`word/media/image1.png`, the central illustration) that must survive any round-trip. Never rebuild the document from extracted text without preserving styles, the figure, and the table structures.

## Deliverables

Beyond the revised manuscript, the checklist implies two more artifacts:

- A **response letter** answering the eight reviewer questions (item S3). C1 and C2 must be conceded explicitly in it, not buried.
- **Supplementary methods** (item M14): full search strings, dates, databases, and a SANRA compliance statement. PRISMA does not apply to a narrative review.
