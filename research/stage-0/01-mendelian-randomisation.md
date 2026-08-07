# Mendelian Randomisation Evidence

Items: C1, C2, C3, M9, M10

Source-location convention: numeric results come from the cited source's Results section or results table. The record names the table when the full text exposes one. The verification manifest identifies records reviewed through PMC full text and records limited to PubMed abstracts or DOI metadata.

## 1. Yu et al. 2024

**Citation:** Yu G, Liu L, Ma Q, Han F, He H. Bidirectional Causal Association Between Chronic Obstructive Pulmonary Disease and Cardiovascular Diseases: A Mendelian Randomization Study. *Int J Chron Obstruct Pulmon Dis.* 2024;19:2109-2122.

- DOI: https://doi.org/10.2147/COPD.S475481
- PMID: https://pubmed.ncbi.nlm.nih.gov/39351082/
- PMCID: https://pmc.ncbi.nlm.nih.gov/articles/PMC11439898/
- Design: bidirectional two-sample MR, with univariable MR, factor-specific multivariable MR, mediation analyses, and sensitivity analyses.
- Main estimator: inverse-variance weighted. Sensitivity methods include weighted median, MR-Egger, MR-PRESSO, Cochran Q, and leave-one-out analysis.

### Reported findings

The univariable result for genetically predicted COPD and CHD was OR 1.004, 95% CI 1.002-1.006, p<0.001. The reverse CHD to COPD estimate was OR 10.227, 95% CI 1.889-55.363, p=0.007. These estimates use genetic-liability scales and do not represent a clinical comparison between people with and without COPD.

Table 2 reports separate multivariable models. The COPD to CHD estimate remained statistically significant after adjustment for:

- BMI: OR 1.004, 95% CI 1.002-1.006, p=6.78x10^-5.
- Smoking initiation: OR 1.003, 95% CI 1.001-1.005, p=0.0006.
- Smoking status: OR 1.005, 95% CI 1.002-1.007, p=3.49x10^-5.

The estimate crossed or approached the null after separate adjustment for:

- IL-6: OR 1.003, 95% CI 1.000-1.006, p=0.052.
- LDL cholesterol: OR 1.003, 95% CI 0.999-1.006, p=0.141.
- Total cholesterol: OR 1.002, 95% CI 0.998-1.006, p=0.314.

Table 3 reports mediation analyses for heart failure, stroke, and essential hypertension. It does not report CHD. FEV1, BMI, smoking initiation, smoking status, and obesity therefore cannot be described as measured mediators of COPD to CHD from Table 3.

### Interpretation for the manuscript

The current manuscript reverses the Table 2 result. BMI and smoking did not remove the association. Lipid and inflammatory adjustment weakened it. This pattern does not establish mediation, because the conditional instrument set is small and Table 2 lacks the full diagnostics needed to exclude weak-instrument bias. The paper cannot support the claim that smoking and BMI explain the COPD to CHD association.

The OR of 1.004 cannot be plotted or compared on the same numerical axis as an observational HR or IRR. The reverse estimate has a wide confidence interval and should be presented as unstable rather than as a tenfold clinical effect.

## 2. Higbee et al. 2021

**Citation:** Higbee DH, Granell R, Sanderson E, Davey Smith G, Dodd JW. Lung function and cardiovascular disease: a two-sample Mendelian randomisation study. *Eur Respir J.* 2021;58(3):2003196.

- DOI: https://doi.org/10.1183/13993003.03196-2020
- PMID: https://pubmed.ncbi.nlm.nih.gov/33574079/
- Design: two-sample MR with multivariable conditioning for height, BMI, and smoking.
- Scale: OR per 1 SD decrease in lung-function measure.

### Reported findings

Lower FVC was associated with CAD: OR 1.32 per 1 SD decrease, 95% CI 1.19-1.46. The corresponding FEV1 estimate after conditioning for height was OR 1.08, 95% CI 0.89-1.30. Airflow obstruction did not show a clear causal effect on cardiovascular events.

### Interpretation for the manuscript

The supported signal concerns FVC, not COPD obstruction. M10 should replace `FEV1 equals obstruction` with explicit distinction among FEV1, FVC, and FEV1/FVC. The result cannot be used to claim that COPD itself causes CAD.

The PubMed abstract states that airflow obstruction did not appear to increase cardiovascular events, but it does not report the exact FEV1/FVC coefficient. The publisher blocked full-text retrieval during Stage 0. Record the qualitative result now and retrieve the supplementary table before inserting an exact FEV1/FVC estimate in Stage 2.

## 3. Au Yeung et al. 2022

**Citation:** Au Yeung SL, Borges MC, Lawlor DA, Schooling CM. Impact of lung function on cardiovascular diseases and cardiovascular risk factors: a two sample bidirectional Mendelian randomisation study. *Thorax.* 2022;77(2):164-171.

- DOI: https://doi.org/10.1136/thoraxjnl-2020-215600
- PMID: https://pubmed.ncbi.nlm.nih.gov/34155093/
- Design: bidirectional two-sample MR using UK Biobank lung-function instruments.
- Scale: OR per 1 SD increase in FEV1 or FVC.

### Reported findings

The main estimates suggested lower CAD risk with higher FEV1, OR 0.72, 95% CI 0.63-0.82, and higher FVC, OR 0.70, 95% CI 0.62-0.78. Adjustment for height materially weakened the CAD result. One reported adjusted FEV1 estimate was OR 0.95, 95% CI 0.75-1.19. The study did not find strong evidence that cardiovascular disease caused lower lung function.

### Interpretation for the manuscript

The result is sensitive to the treatment of height. M9 should present this trade-off beside Higbee rather than selecting one result. Conditioning on height may reduce confounding by body size but can also alter instrument structure and introduce collider concerns.

## 4. Wielscher et al. 2021

**Citation:** Wielscher M, Amaral AFS, van der Plaat D, et al. Genetic correlation and causal relationships between cardio-metabolic traits and lung function impairment. *Genome Med.* 2021;13(1):104.

- DOI: https://doi.org/10.1186/s13073-021-00914-x
- PMID: https://pubmed.ncbi.nlm.nih.gov/34154662/
- PMCID: https://pmc.ncbi.nlm.nih.gov/articles/PMC8215837/
- Design: observational analysis, LD-score regression, bidirectional MR, multivariable MR, and multiple pleiotropy-robust sensitivity methods.

### Reported findings

CAD showed genetic correlation with FEV1, FVC, and FEV1/FVC. The MR analyses did not support a causal relationship between CAD and impaired lung function. Detailed pairwise MR coefficients are in the supplementary material rather than the main text.

### Interpretation for the manuscript

Shared genetic architecture is not evidence of causation. This study should provide the null or discordant part of the C3 triangulation.

## 5. Zhu et al. 2019

**Citation:** Zhu Z, Wang X, Li X, et al.; International COPD Genetics Consortium. Genetic overlap of chronic obstructive pulmonary disease and cardiovascular disease-related traits: a large-scale genome-wide cross-trait analysis. *Respir Res.* 2019;20(1):64.

- DOI: https://doi.org/10.1186/s12931-019-1036-8
- PMID: https://pubmed.ncbi.nlm.nih.gov/30940143/
- PMCID: https://pmc.ncbi.nlm.nih.gov/articles/PMC6444755/
- Design: cross-trait GWAS and MR.

### Reported findings

The COPD to CAD causal estimate was beta 0.004, p=0.40, as reported in the causal-inference results and supplementary Table S23. The main text does not report a CAD OR and confidence interval. Shared loci were identified, but the MR result for CAD was null.

### Interpretation for the manuscript

Do not exponentiate the coefficient without confirming the model and exposure scale in the supplement. Use the study as evidence that genetic overlap can coexist with a null causal estimate.

## Triangulated conclusion

The defensible synthesis is narrower than the original manuscript. Genetic relationships exist between COPD, lung-function traits, and CAD. The evidence for an independent causal effect depends on respiratory phenotype, exposure scale, height adjustment, smoking, inflammatory markers, lipids, and instrument strength. FVC has the most consistent signal. FEV1, airflow obstruction, and COPD liability do not show a robust and uniform CAD effect across studies. None of these studies estimates the short-term risk of ACS after an exacerbation.
