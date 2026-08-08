# Stage 2 Missing-Evidence Implementation Plan

> **For Hermes:** Follow this plan task by task. Keep the original DOCX immutable, prove each failure mode with a regression test, and open a separate PR for Issue #6.

**Goal:** Add the missing trial, trigger, and Mendelian-randomisation evidence for M2, C4, M3, M1, M9, and M10 while preserving an auditable Tracked Changes manuscript.

**Architecture:** Generate the Stage 2 DOCX from the immutable original rather than nesting new revisions inside the Stage 1 package. Reapply the approved Stage 1 corrections, overlay Stage 2 paragraph insertions and replacements, compile a final 62-reference Vancouver sequence, then emit native `w:ins` and `w:del` revisions. Verify both views: Reject All restores the original text and drawing, while Accept All yields the final Stage 2 manuscript.

**Tooling:** Python standard library (`zipfile`, `xml.etree.ElementTree`, `csv`, `json`, `hashlib`, `urllib`), Pillow 10.2.0 for the unchanged Stage 1 figure asset, `uv`, `unittest`, PubMed E-utilities, Crossref, Europe PMC, GitHub CLI.

**Issue:** #6

---

## Task 1: Freeze requirements and evidence

**Files:**
- Create: `research/stage-2/README.md`
- Create: `research/stage-2/evidence-record.md`
- Create: `research/stage-2/reference-seed.tsv`
- Create: `research/stage-2/scripts/generate_reference_audit.py`
- Generate: `research/stage-2/reference-audit.tsv`

1. Record the Stage 1 merge as the approved baseline and the immutable original SHA-256 as the Reject All baseline.
2. Record the exact scope and exclusions for M2, C4, M3, M1, M9, and M10.
3. Add primary-source records for the influenza-vaccination, beta-blocker, anti-inflammatory, trigger, and lung-function MR evidence.
4. Build a final 62-record seed in first-citation order, preserving all approved Stage 1 references.
5. Generate PubMed, Crossref, and Europe PMC metadata with provenance and source-quality classification.
6. Verify online metadata and official URLs fail closed.

## Task 2: Specify accepted manuscript text and final citation numbering

**Files:**
- Create: `research/stage-2/revisions.json`

1. Import the approved Stage 1 paragraph and table replacements as the base transformation.
2. Map original citations directly to the final Stage 2 numbering.
3. Replace the novelty paragraph so it cites the pre-existing substrate-trigger and respiratory-infection trigger literature.
4. Replace the beta-blocker subsection with evidence from BLOCK-COPD, BICS, PACE, ABYSS, REBOOT, BETAMI-DANBLOCK, and the existing COPD post-MI observational studies.
5. Replace the clinical-implications vaccination paragraph with IAMI, IVVE, Modin 2023, and the current mixed-design synthesis, preserving COPD-specific limitations.
6. Add a pathway-specific anti-inflammatory trial paragraph and limit COPD effect modification to a falsifiable hypothesis.
7. Expand the lung-function MR discussion while keeping FEV1, FVC, and FEV1/FVC distinct and documenting the unavailable exact Higbee FEV1/FVC coefficient.
8. Avoid em dashes, placeholders, unqualified causality, and prohibited stop-slop phrasing.

## Task 3: Write regression tests first

**Files:**
- Create: `research/stage-2/scripts/test_stage2.py`

1. Assert the intended 62-reference sequence and first-appearance numbering.
2. Assert exact trial estimates and required limitations for M2, C4, M3, M1, M9, and M10.
3. Assert rejected text restores every original body and table paragraph.
4. Assert tracked settings, revision metadata, run formatting, paragraph marks, image deletion/insertion, relationship integrity, and deterministic ZIP output.
5. Assert verifier failure after corruption of metadata, body text, table text, run formatting, relationships, and drawings.
6. Run tests before implementation and record the expected RED result because Stage 2 artifacts do not yet exist.

## Task 4: Implement integrated OOXML transformation

**Files:**
- Create: `research/stage-2/scripts/apply_stage2.py`
- Generate: `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx`

1. Start from `COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx` on every run.
2. Reapply Stage 1 paragraph, table, reference, and figure corrections.
3. Apply Stage 2 replacements and insertions using `w:ins` and `w:del` with valid author, ID, and date metadata.
4. Preserve original paragraph and run properties, bookmarks, drawings, relationship attributes, and every untouched package part.
5. Preserve `word/media/image1.png` for Reject All and insert deterministic `image2.png` for the Stage 1 Panel C correction.
6. Add 62 reference paragraphs with tracked paragraph marks.
7. Enable `w:trackRevisions` and write the ZIP deterministically.

## Task 5: Build a fail-closed verifier

**Files:**
- Create: `research/stage-2/scripts/verify_stage2.py`

1. Verify source hash, package integrity, allowed changed parts, source-image preservation, and deterministic replacement-image bytes.
2. Verify active `trackRevisions`, unique numeric revision IDs, ISO dates, and required authors.
3. Verify Reject All reconstructs the immutable original body, tables, reference list, formatting spans, and original drawing.
4. Verify Accept All contains the exact Stage 2 text and 62 sequential references.
5. Verify Vancouver first-appearance order and citation bounds.
6. Verify every audit row has complete metadata/provenance fields and valid DOI, PMID, PMCID status, and URLs.
7. Reject placeholders, em dashes, prohibited slop phrases, uncalibrated COPD-specific claims, detached drawings, and unexpected relationship/package changes.

## Task 6: Verify and review

1. Regenerate the reference audit online.
2. Regenerate the figure with `uv run --with Pillow==10.2.0` and prove byte identity.
3. Generate the revised DOCX twice across different timestamps and prove byte identity.
4. Run syntax checks, all Stage 2 regression tests, offline verification, and online verification.
5. Confirm the original SHA-256 remains `8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1`.
6. Inspect the final figure visually.
7. Request independent scientific, OOXML, and reproducibility review; fix all Critical and Important findings.

## Task 7: Commit and open PR

1. Confirm branch `revision/6-stage-2-evidence` and clean diff checks.
2. Commit as `auctusstore-arch <auctus.store@gmail.com>`.
3. Push the feature branch.
4. Update Issue #6 with implementation and verification evidence.
5. Open a PR referencing `Closes #6`; do not merge without explicit user direction.
