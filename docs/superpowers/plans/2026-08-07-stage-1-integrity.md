# Stage 1 Manuscript Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Produce an audit-ready revised DOCX that corrects C1, C2, C3, C7a, and C7b without modifying the original manuscript or losing its image, tables, styles, or relationships.

**Architecture:** Store the verified final references and prose replacements as reviewable text artifacts under `research/stage-1/`. A deterministic Python script will copy the original DOCX and patch `word/document.xml` with WordprocessingML tracked deletions and insertions. A separate verifier will inspect both DOCX packages, extract the accepted revision text, validate references against PubMed/DOI, and enforce preservation and writing constraints.

**Tech Stack:** Python 3 standard library, WordprocessingML, ZIP/OOXML, PubMed E-utilities, DOI resolution, unittest, git, GitHub CLI.

---

## File map

- Create `research/stage-1/README.md`: scope, correction summary, unresolved constraints, and verification commands.
- Create `research/stage-1/reference-audit.tsv`: final ordered reference list with DOI, PMID, PMCID, and verification basis.
- Create `research/stage-1/revisions.json`: final paragraph replacements, table-cell replacements, citation renumbering map, and added references.
- Create `research/stage-1/central-illustration-scale-decision.md`: binding C2 specification for Panel C before Stage 4 redesign.
- Create `research/stage-1/scripts/apply_stage1.py`: deterministic tracked-change DOCX transformer.
- Create `research/stage-1/scripts/verify_stage1.py`: package-preservation, tracked-change, citation, prose, and identifier verifier.
- Create `research/stage-1/scripts/test_stage1.py`: regression tests for source immutability, citation remapping, OOXML preservation, and verifier failure cases.
- Create `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx`: revised tracked-change manuscript.
- Do not modify `Manuskrip/COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx`.

### Task 1: Freeze source invariants and write failing tests

- [ ] Record the original SHA-256 `8a367b903a7ad9a6c751d5219e16afb5dbf46cbba3ed4d58c50143c2308880b1`, 11 source OOXML parts, five tables, one source image, and 126 body paragraphs in the verifier.
- [ ] Write tests requiring every source part to remain byte-identical except `word/document.xml`, `word/settings.xml`, and `word/_rels/document.xml.rels`; the revised package adds `image2.png` and one relationship for the tracked figure insertion.
- [ ] Write tests requiring at least one `w:del` and one `w:ins`, no mutation of the source hash, and a valid ZIP package.
- [ ] Run `uv run python3 -m unittest -v research/stage-1/scripts/test_stage1.py` and confirm failure because the transformer and revised DOCX do not exist.

### Task 2: Build the verified reference audit

- [ ] Convert the 36-reference audit into the final 44-reference citation order.
- [ ] Insert Au Yeung, Wielscher, and Zhu after Higbee for C3.
- [ ] Retain and complete Brassington [13], which supports the shared-mechanism paragraph.
- [ ] Replace Cureus [22] with Brekke, McAllister, and Høiseth.
- [ ] Replace the unverifiable ECG source [23] with the 2021 AHA/ACC Chest Pain Guideline.
- [ ] Replace Australian Resuscitation Council [34] with DETO2X-AMI, its COPD subgroup, and ESC ACS 2023.
- [ ] Replace the Andell thesis [35] with Andell et al. 2014.
- [ ] Verify every DOI-PMID pair against PubMed; obtain PMCID from PubMed where assigned; use the official DOI record for the ETHOS conference abstract.
- [ ] Write a regression test that rejects duplicate DOI/PMID, unresolved identifiers, citation-title mismatch, and missing source provenance.

### Task 3: Draft the integrity corrections as reviewable text

- [ ] Rewrite Introduction paragraphs 13 and 16 so references [1-3] support the burden statement and Yu's liability-scale OR is not compared with observational risk.
- [ ] Rewrite Section 5 paragraphs 35-37 to report Yu Table 2 correctly: BMI and smoking adjustments retain significance; IL-6, LDL cholesterol, and total cholesterol attenuate the estimate; Table 3 does not analyse CHD; FEV1 is not a CHD MVMR mediator.
- [ ] Triangulate Yu, Higbee, Au Yeung, Wielscher, and Zhu, including height sensitivity, genetic correlation without causation, null COPD-to-CAD beta, unstable reverse estimates, and instrument limitations.
- [ ] Rewrite the relevant Table 1 and Table 2 MR cells without cross-scale numerical comparisons or the claim that FEV1 equals obstruction.
- [ ] Rewrite paragraphs 52-54 using Brekke, McAllister, Hoiseth, the Fourth Universal Definition, and the AHA/ACC diagnostic guideline.
- [ ] Rewrite paragraph 70 to align COPD oxygen targets with DETO2X-AMI, its COPD subgroup, ESC 2023, and ACC/AHA 2025.
- [ ] Rewrite paragraph 72 to support undertreatment with Andell et al. 2014 and remove unsupported causal speculation.
- [ ] Apply British English, no em dash, no placeholders, and the repository stop-slop rules to every new sentence.

### Task 4: Encode deterministic tracked changes

- [ ] Implement paragraph replacement by retaining `w:pPr`, wrapping original runs in `w:del`, and placing accepted replacement text in `w:ins` with author `auctusstore-arch` and the fixed revision date.
- [ ] Implement citation-only renumbering for unchanged paragraphs and table cells so unaffected prose is not marked as rewritten.
- [ ] Implement full tracked replacement for changed table cells.
- [ ] Replace the 36 original reference paragraphs with 44 verified entries, tracking replacements and inserted entries.
- [ ] Add and explicitly enable `w:trackRevisions` in `word/settings.xml` while preserving all existing settings.
- [ ] Preserve the source raster as `image1.png`, add the revised raster as `image2.png`, track the old drawing as deleted and the new drawing as inserted, and write the revised DOCX atomically.

### Task 5: Make regression tests pass

- [ ] Run the transformer and generate the revised DOCX.
- [ ] Run `uv run python3 -m unittest -v research/stage-1/scripts/test_stage1.py`.
- [ ] Confirm the tests detect a deliberately corrupted source hash, removed image, missing tracked change, placeholder citation, and invalid citation mapping.
- [ ] Restore clean fixtures and rerun until all tests pass.

### Task 6: Run complete verification

- [ ] Run `uv run python3 research/stage-1/scripts/verify_stage1.py` with PubMed and DOI network checks.
- [ ] Extract accepted revision text and confirm zero placeholder markers and zero em dash characters in replaced or inserted text.
- [ ] Confirm 44 reference entries, ordered body citations, valid DOI-PMID-PMCID pairs, and no orphan references.
- [ ] Confirm five tables, the reviewed Stage 1 figure with a live drawing relationship, unchanged unrelated OOXML parts, and preserved paragraph styles.
- [ ] Compare the original SHA-256 before and after generation.
- [ ] Run `git diff --check` and inspect the complete diff.

### Task 7: Independent review and PR

- [ ] Request an adversarial scientific review of C1, C2, C3, and C7b against primary sources.
- [ ] Request an OOXML review focused on tracked changes and package preservation.
- [ ] Fix every Critical or Important finding and rerun all verification.
- [ ] Commit with author `auctusstore-arch <auctus.store@gmail.com>`.
- [ ] Push `revision/4-stage-1-integrity` and open a PR that closes Issue #4.
- [ ] Stop at the Stage 1 checkpoint; do not start Stage 2 before review and merge.
