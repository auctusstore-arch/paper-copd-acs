# Stage 1: Manuscript integrity

Issue: #4
Checklist items: C1, C2, C3, C7a, C7b

## Deliverable

`Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx` is generated from the original manuscript with WordprocessingML tracked changes. The original DOCX remains byte-identical.

## Corrections

1. **C1, Yu et al.** The manuscript now reports that separate adjustment for BMI, smoking initiation and smoking status retained the COPD-liability to CHD association, whereas small-instrument conditional models including IL-6, LDL cholesterol or total cholesterol lost nominal significance despite little change in the point estimate. The revised text does not describe FEV1 as a CHD mediator because the paper's mediation table does not analyse CHD.
2. **C2, cross-scale comparison.** Yu's source-reported exponentiated estimate is not interpreted as a patient-level odds ratio or compared numerically with observational relative risks or post-exacerbation incidence rate ratios. The binding scale decision is in `central-illustration-scale-decision.md`.
3. **C3, MR triangulation.** Yu, Higbee, Au Yeung, Wielscher and Zhu are presented together. The synthesis distinguishes COPD liability, FEV1, FVC and airflow obstruction; it also records sensitivity to height adjustment, shared genetic architecture without demonstrated causation, the null Zhu estimate, Yu's permissive instrument threshold, its implausibly large reverse estimate, and the failed forward replication after pleiotropy correction.
4. **C7a, reference audit.** The 36 supplied entries were checked against PubMed, PMC, DOI and official metadata. Bibliographic defects were corrected, three MR studies and primary diagnostic/oxygen sources were added, and the retained Brassington review was completed because it is cited in the body.
5. **C7b, source replacement.** The Cureus troponin review was replaced with Brekke, McAllister and Høiseth primary studies. The unverifiable ECG paper was replaced with the 2021 AHA/ACC chest-pain guideline. The 2011 Australian oxygen source was replaced with DETO2X-AMI, its COPD subgroup and ESC 2023. The thesis was replaced with Andell et al. 2014.
6. **Citation sequence.** The revised manuscript has 44 references, no orphan references, and first citations appear in Vancouver order from 1 through 44.
7. **Central illustration.** Panel C was replaced with three nonquantitative evidence lanes. The source drawing and raster are preserved inside a tracked deletion; the reviewed replacement drawing and raster are inside a tracked insertion. Reject All therefore restores the original figure.

## Audit artefacts

- `reference-seed.tsv`: human-reviewed citation seed and correction disposition.
- `reference-audit.tsv`: generated audit with resolved title, DOI, PMID, PMCID and official DOI/PubMed/PMC URLs where available.
- `revisions.json`: reviewable source of all substantive paragraph/table replacements and the old-to-new citation map.
- `scripts/generate_reference_audit.py`: regenerates the online metadata audit.
- `scripts/apply_stage1.py`: deterministically produces the revised DOCX.
- `scripts/verify_stage1.py`: fail-closed package, citation, reference and online metadata verifier.
- `scripts/test_stage1.py`: seventeen regression tests, including negative tests for a removed image, a detached image relationship, and absent or explicitly disabled tracked changes.

## Reproduction

```bash
uv run python3 research/stage-1/scripts/generate_reference_audit.py
uv run --with Pillow==10.2.0 python3 research/stage-1/scripts/generate_stage1_figure.py
uv run python3 research/stage-1/scripts/apply_stage1.py
uv run python3 -m unittest -v research/stage-1/scripts/test_stage1.py
uv run python3 research/stage-1/scripts/verify_stage1.py
```

The figure generator also requires the system fonts `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` and `DejaVuSans-Bold.ttf`; it fails if they are unavailable.

For a deterministic verification run without network metadata refresh:

```bash
uv run python3 research/stage-1/scripts/verify_stage1.py --offline
```

## Quality gates

The verifier enforces:

- original SHA-256 `8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1`;
- 134 direct revised paragraphs, including 44 reference entries;
- five tables, with the source image preserved as `image1.png` and the reviewed replacement as `image2.png`;
- tracked deletion of the source drawing and tracked insertion of the replacement drawing, so Reject All restores the source figure;
- byte-identical preservation of every source OOXML part except `word/document.xml`, `word/settings.xml`, and `word/_rels/document.xml.rels`;
- preserved paragraph styles/properties for all original direct body paragraphs;
- tracked insertions and deletions with contiguous decimal IDs, valid dates and expected author metadata;
- an enabled `w:trackRevisions` setting, with explicit false values rejected;
- tracked paragraph marks for all inserted reference paragraphs;
- accepted-view correspondence and rejected-view restoration for all direct body paragraphs and table paragraphs, including run formatting;
- structural identity of the tracked source drawing and complete validation of the replacement image relationship;
- exact correspondence between the DOCX bibliography and `reference-audit.tsv`;
- first-citation order 1-44, no orphan references and no out-of-range citation;
- no placeholder markers or em dashes in inserted Stage 1 text;
- unique DOI and PMID identifiers;
- online DOI-PMID-PMCID-title agreement against PubMed, with Crossref verification for records without PMID.

## Scope boundary

Stage 1 changes only Panel C of the supplied raster central illustration. It removes the invalid shared quantitative scale and separates observational, genetic and acute-trigger evidence into nonquantitative lanes. Panels A, B and D remain visually unchanged. A broader presentation redesign remains in the Stage 4 scope.
