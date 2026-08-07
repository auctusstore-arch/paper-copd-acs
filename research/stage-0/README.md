# Tahap 0: Verified Literature Retrieval

Issue: #2

## Purpose

This directory records the source-level evidence needed for Stages 1 to 3 of the manuscript revision. The original manuscript remains read-only. Each record separates reported findings from manuscript interpretation.

## Files

- `01-mendelian-randomisation.md`: C1, C2, C3, M9, and M10.
- `02-intervention-trials.md`: M2, C4, M3, and M13.
- `03-triggers-diagnostics-guidelines.md`: M1, M11, M12, M13, C7b, and F1.
- `verification-manifest.tsv`: one row per publication with DOI, PMID, and PMCID where assigned; resolved title; all evidence files that use it; verification basis; full-text status; and verification date.
- `scripts/generate_manifest.py`: regenerates and deduplicates the manifest from the evidence records.
- `scripts/verify_manifest.py`: checks identifier coverage, uniqueness, DOI-PMID-PMCID pairing, citation titles, evidence-file provenance, the official GOLD record, DOI resolution, placeholders, and file formatting.
- `scripts/test_manifest.py`: regression tests for malformed citations, missing GOLD, invalid provenance, and incorrect PMCID data.

## Reproducible verification

Run both commands from the repository root:

```bash
python3 research/stage-0/scripts/generate_manifest.py
python3 -m unittest -v research/stage-0/scripts/test_manifest.py
python3 research/stage-0/scripts/verify_manifest.py
```

The verifier exits non-zero if an audit condition fails. Network access to PubMed and doi.org is required.

## Material corrections to the existing roadmap

1. Yu et al. Table 2 does not show that BMI, smoking initiation, or smoking status remove the COPD to CHD association. The estimate becomes non-significant after separate adjustment for IL-6, LDL cholesterol, or total cholesterol. Table 3 does not analyse CHD.
2. The reported OR of 1.004 in Yu et al. uses a genetic-liability scale. It cannot be compared numerically with observational relative risks of 2 to 5.
3. PACE was published online in January 2026 and in print in March 2026. The DOI contains 2025, but the article is not a 2025 Lancet Respiratory Medicine publication.
4. Aleva et al. estimated a 16.1% pulmonary embolism prevalence in unexplained AECOPD, not in all exacerbations.
5. The roadmap phrase `High-STEACS Chapman JAMA 2017 type 2 MI/CAD` combines two sources. The JAMA 2017 study concerns high-sensitivity troponin and prognosis. Systematic coronary imaging in type 2 MI comes from DEMAND-MI, published in Circulation in 2022.
6. Muller 1989 is a historical review of circadian variation and triggers, not the primary onset study.
7. Leong and Bardin 2021 is a commentary. GOLD 2025 is a strategy report. Neither should be labelled a narrative review.
8. Reference [35], Andell's Lund thesis, appears in the reference list but has no body citation in the extracted manuscript. Stage 1 should remove it unless a specific claim requires one of Andell's peer-reviewed papers.

## Evidence status

- MR bundle: verified against PubMed, PMC, DOI records, and source tables where open full text was available.
- Trial bundle: verified against PubMed and journal records. Primary endpoint values are recorded below.
- Trigger and diagnostic bundle: verified against PubMed, PMC, DOI records, and society guideline pages.
- Full reference-list audit: remains a Stage 1 task because the manuscript contains 36 references and 17 incomplete markers.

## Rules for downstream drafting

- Do not cite the files in `Rangkuman consensus/`.
- Do not infer a result that the source did not report.
- Preserve each exposure scale and direction.
- Treat non-significance as uncertainty, not proof of no effect.
- Use British English in manuscript prose.
- Do not introduce em dashes.
