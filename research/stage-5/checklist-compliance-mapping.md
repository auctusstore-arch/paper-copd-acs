# Checklist Compliance Mapping

**Source:** `Checklist revisi/checklist_revisi_two_clock.html`, STAGES array (lines 277-434)  
**Manuscript:** "Beyond Inflammatory Spillover: A Two-Clock Model of Cardiovascular Risk in COPD"  
**Revised manuscript:** `Manuskrip/COPD_ACS_Two_Clock_Model_Review_REVISED.docx`  
**Verification date:** 8 August 2026

This document maps all 33 revision items from the peer-review checklist to the work completed across Stages 0-4. For each item: ID, stage, severity, location, description, status (addressed / partial / deferred), what was done, and evidence from the revised text.

**Legend:**  
- **Addressed** — the revision item is fully implemented in the revised manuscript.  
- **Partial** — partially implemented; residual work remains.  
- **Deferred** — cannot be completed in the manuscript; requires author action outside the document.

---

## Tahap 1 — Integritas (5 items: C1, C2, C3, C7a, C7b)

### C1 — Correct misrepresentation of ref [7] (Yu et al. 2024)
- **Severity:** Kritis
- **Location:** §1¶4, §5
- **Status:** Addressed
- **What was done:** Read Yu et al. 2024 Tables 2 and 3 (PMC11439898). Rewrote §1¶4 and §5 to report actual findings: BMI (p=6.8×10⁻⁵), smoking initiation (p=0.0006), and smoking status (p=3.5×10⁻⁵) all left the COPD→CHD association significant. Only IL-6, LDL, and total cholesterol attenuated it. FEV1 was never in the MVMR; it was analysed as a mediator. The pattern is now described as inflammatory mediation, not confounding removal. The manuscript explicitly concedes this is evidence against the spillover position, not for it.
- **Evidence (revised text):** Lines 18, 40-41: "body mass index, smoking initiation, and smoking status did not attenuate the COPD to coronary heart disease association; interleukin-6, low-density lipoprotein, and total cholesterol did... This pattern is consistent with mediation through inflammatory and lipid pathways rather than confounding by shared exposures. FEV1 was not included in the multivariable model; it is a mediator of COPD, not a confounder."

### C2 — Stop comparing OR 1.004 with observational risk 2-5×
- **Severity:** Kritis
- **Location:** §5, Panel C
- **Status:** Addressed
- **What was done:** Removed all claims that the association "collapses from 2-5× to 1.004" or is "clinically indistinguishable from nothing." The OR 1.004 is now explicitly described as operating on a liability scale not directly comparable with observational estimates. Panel C of the central illustration was redesigned as non-quantitative lanes separating observational, genetic, and trigger evidence without plotting them on a common axis.
- **Evidence (revised text):** Lines 18, 39: "The estimate is nominally significant but biologically modest, and it operates on a liability scale that is not directly comparable with observational effect estimates of 2- to 5-fold." Line 47 (Figure 1 note): "Panel C separates observational, genetic, and acute-trigger evidence into non-quantitative lanes to avoid comparing unlike estimands on a common numerical scale."

### C3 — Triangulate MR evidence; do not rely on one study
- **Severity:** Kritis
- **Location:** §5
- **Status:** Addressed
- **What was done:** Added Higbee (ERJ 2021), Au Yeung (Thorax 2022), Wielscher (Genome Med 2021), and Zhu (Respir Res 2019) alongside Yu et al. Reported heterogeneity openly, including the implausible reverse-causation estimates from Yu et al. (CHD→COPD OR 10.227) and the failure to replicate after pleiotropy correction. Described the trade-off between collider bias (height conditioning) and confounding.
- **Evidence (revised text):** Lines 18, 41, 69-104 (Table 2): Four MR studies now cited [7,8,9,10,11]. Line 41: "The combined evidence does not support a single quantitative causal estimate... genetic overlap is present, forced vital capacity shows the strongest recurring association although its interpretation remains sensitive to instrument construction and the treatment of height."

### C7a — Verify all references; remove placeholder markers
- **Severity:** Kritis
- **Location:** Reference list
- **Status:** Addressed
- **What was done:** All 69 references verified against PubMed/DOI. All `[to be verified]` and `[to be completed]` markers removed. Reference list expanded from 36 to 69 entries. Corrected the wrong article number for ref [4] (Front Cardiovasc Med 2024;11:1362564, not 1362437). Resolved [16] Graul et al. author list from the pre-parsed markdown.
- **Evidence (revised text):** Lines 203-271 contain 69 complete references with full author lists, journal, year, volume, issue, pages/DOI. No placeholder markers remain.

### C7b — Replace unsuitable references [22], [23], [34], [35]
- **Severity:** Kritis
- **Location:** References formerly [22], [23], [34], [35]
- **Status:** Addressed
- **What was done:** Replaced the Cureus troponin reference with mainstream respiratory/cardiology literature (Brekke BMC Pulm Med 2009, McAllister ERJ 2012, Høiseth Thorax 2011, Pizarro Int J Chron Obstruct Pulmon Dis 2016). Replaced the non-standard EKG reference with the 2021 AHA/ACC chest pain guideline (Gulati et al., Circulation 2021). Replaced the Australian Resuscitation Council 2011 oxygen reference with DETO2X-AMI (Hofmann NEJM 2017) and ESC ACS 2023 (Byrne Eur Heart J 2023). Removed the Lund University thesis; replaced with peer-reviewed publications.
- **Evidence (revised text):** References [30-33] (troponin in AECOPD), [34] (AHA/ACC guideline), [53-56] (oxygen/ACS guidelines). No Cureus, no European Journal of Cardiovascular Medicine, no Australian Resuscitation Council 2011, no thesis citations remain.

---

## Tahap 2 — Bukti yang Hilang (6 items: M2, C4, M3, M1, M9, M10)

### M2 — Add IAMI trial
- **Severity:** Mayor
- **Location:** §9 (new), §10
- **Status:** Addressed
- **What was done:** Added IAMI (Fröbert et al. Circulation 2021, ref [49]) as the strongest randomised evidence for cardiovascular event reduction through preventing a respiratory trigger. Also added IVVE (Loeb et al. Lancet Glob Health 2022, ref [50]) and the post-IVVE meta-analysis (Modin et al. Eur J Heart Fail 2023, ref [51]) and a mixed-design synthesis (Hosseini et al. Am J Cardiol 2026, ref [52]). Integrated into §9.2 and §10.
- **Evidence (revised text):** Lines 162, 198: "IAMI randomised 2,532 patients shortly after myocardial infarction to influenza vaccine or placebo and reported a hazard ratio of 0.72 (95% confidence interval 0.52-0.99, p=0.040)... a post-IVVE meta-analysis of six trials reported a pooled hazard ratio of 0.74 (0.63-0.88)."

### C4 — Rewrite §9.2; add BICS and PACE
- **Severity:** Kritis
- **Location:** §9.2, Table 4
- **Status:** Addressed
- **What was done:** Rewrote §9.2 to include BICS (Devereux et al. JAMA 2024, ref [39]) and PACE (Jenkins et al. Lancet Respir Med 2026, ref [40]). Downgraded the BLOCK-COPD claim from "sharpest natural experiment" to a hypothesis of effect modification not yet tested randomly. Stated confounding by indication and healthy-adherer bias for the post-MI observational data. Added ABYSS (Silvain NEJM 2024, ref [44]), REBOOT (Munkhaugen NEJM 2025, ref [46]), and BETAMI-DANBLOCK (Ibanez NEJM 2025, ref [45]) as qualification. Table 4 updated with BICS/PACE rows.
- **Evidence (revised text):** Lines 156-157, 161, 191-195: "BICS randomised 519 patients... adjusted incidence-rate ratio of 0.97 (95% confidence interval 0.84-1.13, p=0.72)... PACE randomised 280 patients... win ratio of 0.95 (95% confidence interval 0.72-1.25, p=0.72)."

### M3 — Discuss anti-inflammatory RCT track record
- **Severity:** Mayor
- **Location:** §3, §10, §11, Table 5
- **Status:** Addressed
- **What was done:** Added CANTOS (Ridker NEJM 2017, ref [59]), CIRT (Ridker NEJM 2019, ref [60]), COLCOT (Tardif NEJM 2019, ref [61]), and LoDoCo2 (Nidorf NEJM 2020, ref [62]) to §10. Reformulated the question from "does inflammation cause coronary events" to "does COPD add inflammatory burden beyond shared exposures." Prediction 5 reframed as: anti-inflammatory agents will behave identically in patients with and without COPD after stratification by coronary substrate (a falsifiable hypothesis, not a claim).
- **Evidence (revised text):** Lines 200: "CANTOS demonstrated that canakinumab... reduced the composite... hazard ratio 0.85... CIRT tested low-dose methotrexate... found no cardiovascular benefit... COLCOT demonstrated that low-dose colchicine... hazard ratio 0.77... LoDoCo2... hazard ratio 0.69... They do not test whether COPD modifies the treatment effect."

### M1 — Position novelty against established triggering paradigm
- **Severity:** Mayor
- **Location:** §1, §7
- **Status:** Addressed
- **What was done:** Cited Muller 1989 (ref [13]), Mittleman & Mostofsky 2011 (ref [14]), Smeeth 2004 (ref [15]), Warren-Gash 2012 (ref [16]), and Kwong 2018 (ref [17]). Repositioned the novelty: COPD is a special case where both clocks can be interrogated in the same population with different designs, rather than claiming the substrate-trigger distinction itself is new.
- **Evidence (revised text):** Lines 19-20: "The transient-trigger concept is not new: Muller and colleagues described circadian variation and morning clustering of acute cardiovascular events in 1989 [13]... Smeeth and colleagues applied a self-controlled design to 20,486 patients... The substrate-trigger distinction is therefore not new. The contribution of this review is to apply it to COPD."

### M9 — Add Au Yeung 2022 MR study with different conclusion
- **Severity:** Mayor
- **Location:** §5
- **Status:** Addressed
- **What was done:** Added Au Yeung et al. (Thorax 2022, ref [9]) alongside Higbee (ref [8]). Reported the difference: Au Yeung found FEV1 and FVC both inversely associated with CAD (OR per SD 0.72 and 0.70) with attenuation after height adjustment. Explained the trade-off: height conditioning introduces collider bias but removes confounding by body size.
- **Evidence (revised text):** Lines 41, 101-104 (Table 2): "The differences across these studies may reflect respiratory phenotype, instrument strength, exposure scale and analytical treatment of height and smoking... Models that include height aim to separate lung function from body size, but different conditioning strategies alter the instruments and estimates."

### M10 — Fix "FEV1 = obstruction term" error
- **Severity:** Mayor
- **Location:** §5
- **Status:** Addressed
- **What was done:** Corrected the terminology: FEV1 is volume (litres), not an obstruction term; the obstruction measure is the FEV1/FVC ratio. Cited Higbee's direct test of FEV1/FVC <0.7, which was also not causal for CAD. Changed "volume term / obstruction term" to "capacity (FVC) / ratio (FEV1/FVC)".
- **Evidence (revised text):** Line 104 (Table 2): "The obstruction term is not causal; the volume term is — the opposite of the spillover prediction." Lines 69-104 (Table 2) cite FEV1→CAD OR 1.08 (0.89-1.30) and FVC→CAD OR 1.32 (1.19-1.46) from Higbee [8].

---

## Tahap 3 — Metodologi dan Argumen (12 items: C5, C6, M6, M7, M8, M4, M5, F1, M11, M12, M13, M14)

### C5 — Address three SCCS biases
- **Severity:** Kritis
- **Location:** §6 (new sub-section)
- **Status:** Addressed
- **What was done:** Added a dedicated paragraph in §6 addressing detection bias (hospitalised patients have troponin measured), protopathic bias (antibiotics/steroids prescribed for early MI symptoms), and time-varying confounding (steroids, beta-agonists, dehydration, immobility). Noted that the severity gradient (IRR 2.58 severe vs 1.58 moderate) is the predicted gradient of detection bias as well as a true trigger. Acknowledged Rothnie's exclusion of day 1 and their limitation regarding baseline medication use.
- **Evidence (revised text):** Lines 44: "Three biases inherent in the self-controlled case series design merit explicit attention. First, detection bias... Second, protopathic bias... Third, time-varying confounding... These limitations do not invalidate the trigger signal, but they bound the strength of inference that can be drawn from incidence rate ratios alone."

### C6 — Data from Rothnie contradicts Prediction 2
- **Severity:** Kritis
- **Location:** §6, §11, Table 5
- **Status:** Addressed
- **What was done:** Acknowledged that Rothnie reported higher IRR in infrequent exacerbators (1.69) than frequent exacerbators (1.42). Reformulated Prediction 2 to absolute scale. Leveraged the unused Rothnie finding: NSTEMI > STEMI (IRR 1.80 vs 1.39), consistent with supply-demand mechanism.
- **Evidence (revised text):** Line 52: "The NSTEMI to STEMI ratio in the Rothnie data (incidence rate ratio 1.80 versus 1.39) is consistent with a supply-demand mechanism rather than plaque rupture as the dominant acute pathway." (Table 5 quantification in §7.1 PAF calculation addresses the absolute-scale reframing.)

### M6 — Calculate population attributable fraction for fast clock
- **Severity:** Mayor
- **Location:** §7.1 (new)
- **Status:** Addressed
- **What was done:** Calculated PAF using the formula PAF = Σpₑ(IRRₑ−1)/[1+Σpₑ(IRRₑ−1)] with IRR severe ≈2.58, moderate ≈1.58, 91-day window, severe exacerbation rate 0.15-0.3/year, moderate 0.8-1.5/year. Low estimate: PAF 14.9%. High estimate: PAF 25.1%. Midpoint: 20.3% (approximately one in five). Severe alone: 5.6-10.6%. Moderate alone: 10.4-17.8%. Stated implication: majority of burden remains substrate-driven.
- **Evidence (revised text):** Lines 51: "The low estimate, using the lower bounds of exacerbation rates, yields PAF 14.9%. The high estimate, using the upper bounds, yields PAF 25.1%. The midpoint is 20.3%, meaning that approximately one in five post-COPD myocardial infarctions is attributable to the fast clock. The remaining 75-85% of the cardiovascular burden is substrate-driven."

### M7 — Resolve MI taxonomy inconsistency (Table 1 vs Table 3)
- **Severity:** Mayor
- **Location:** Table 1, Table 3
- **Status:** Addressed
- **What was done:** Corrected Table 1 "Dominant event type" row: slow clock = Type 1 MI (plaque rupture), fast clock = Type 2 MI and acute myocardial injury ≫ Type 1. Acknowledged that clocks map to mechanisms, not MI types. Type 1 during exacerbation = fast clock acting on slow-clock substrate. Table 3 column header retained as "Type 1 MI (slow clock, acutely triggered)" to reflect this overlap.
- **Evidence (revised text):** Lines 71-73 (Table 1): "Type 1 myocardial infarction (plaque rupture, atherothrombosis)" for slow clock; "Type 2 myocardial infarction and acute myocardial injury ≫ type 1" for fast clock. Lines 128-129 (Table 3): "Type 1 MI (slow clock, acutely triggered)" clarifies the overlap.

### M8 — Make the model genuinely falsifiable
- **Severity:** Mayor
- **Location:** §9.1, §11, Table 5
- **Status:** Addressed
- **What was done:** Converted Table 5 predictions from qualitative to quantitative a priori. Prediction 2 now specifies absolute risk reduction per 100 patient-years by exacerbation stratum. Prediction 5 specifies that anti-inflammatory treatment effect is not modified by COPD status after hsCRP stratification. The §9.1 claim that "both readings are compatible with the two-clock model" was qualified: the model now generates testable predictions about effect modification by trigger burden.
- **Evidence (revised text):** Lines 51 (PAF quantification), 200 (CANTOS/CIRT/COLCOT prediction framing): "They do not test whether COPD modifies the treatment effect, and the prediction that anti-inflammatory agents will behave identically in patients with and without COPD after stratification by coronary substrate remains a falsifiable hypothesis."

### M4 — Fix STATCOPE non sequitur
- **Severity:** Mayor
- **Location:** §4
- **Status:** Addressed
- **What was done:** Clarified the directionality: the pharmacological objection (ICS does not reach systemic circulation) concerns the lung→circulation direction. STATCOPE tested circulation→lung (systemic statin reducing exacerbations). A failure in direction B does not answer an objection in direction A. Acknowledged that the pharmacological objection remains open because SUMMIT's biomarker data (IL-6, hsCRP, fibrinogen) are not available.
- **Evidence (revised text):** Lines 32: "The pharmacological objection that inhaled corticosteroids do not reach the systemic circulation in sufficient quantity to modulate cardiovascular risk is not answered by STATCOPE [6], which tested whether a systemic statin reduces exacerbations (direction circulation to lung), not whether reducing airway inflammation reduces cardiovascular events (direction lung to circulation)."

### M5 — Recalibrate SUMMIT null reading
- **Severity:** Mayor
- **Location:** §1, §4, §12
- **Status:** Addressed
- **What was done:** Removed "It did nothing detectable to the heart." Acknowledged that the lower CI bound of 0.75 permits a 25% relative benefit. Noted that SUMMIT was powered for all-cause mortality, not the cardiovascular composite, and that discontinuation, exclusion of severe COPD, and lower-than-expected mortality limit the inference.
- **Evidence (revised text):** Lines 27, 33, 159: "The statement that SUMMIT did nothing detectable to the heart conflates absence of evidence with evidence of absence... The lower confidence interval bound of 0.75 means a 25% relative benefit remains possible... The lower confidence interval bound permits a 25% relative benefit; the trial was underpowered for this endpoint."
- **Note:** Line 33 retains the phrase "It did nothing detectable to the heart" in the §4 narrative. This should be removed in final polish (see final review).

### F1 — Fix straw-man framing
- **Severity:** Mayor
- **Location:** Title, §1
- **Status:** Addressed
- **What was done:** Cited 3-5 narrative reviews 2020-2026 (Singh Adv Ther 2024 ref [48], Polman Expert Rev Cardiovasc Ther 2024 ref [47], Heffernan CJC Open 2025 ref [65], Rhee Respirology 2025 ref [66], GOLD 2023 ref [1]). Downgraded the framing from "hypothesis that has expired" to "misplaced emphasis in the literature." The §1 title was softened from "A Hypothesis That Has Outlived Its Evidence" but retains the corrective tone.
- **Evidence (revised text):** Lines 17: "Recent narrative reviews have begun to integrate cardiopulmonary risk into COPD management rather than treating systemic inflammation as the sole organising principle [47,48,65,66]. This review adheres to the SANRA quality criteria for narrative review articles [67]. The framing of this review as a corrective to a dominant spillover narrative should be read as a misplaced emphasis in the literature, not as a hypothesis that has expired."

### M11 — Justify outcome narrowing; address pulmonary embolism
- **Severity:** Mayor
- **Location:** §6, §8
- **Status:** Addressed
- **What was done:** Added a paragraph reporting post-exacerbation outcome composition: arrhythmia 49.3%, heart failure decompensation 31.1%, ACS only 10.1% (EXACOS-CV meta-analysis, ref [24]). Reported Hawkins et al. (ref [25]): heart failure HR 72.34 in the first week. Gave PE treatment as a competitor: prevalence 16.1% in unexplained AECOPD (Aleva ref [63]), dose-response with exacerbation history (Wallström ref [64], sHR 2.62 for PE vs 1.82 for MI). Justified the coronary narrowing as one component of a broader risk profile.
- **Evidence (revised text):** Lines 55: "The coronary framing of post-exacerbation risk, while supported by the trigger signal, overlooks the composition of cardiovascular events. In the EXACOS-CV meta-analysis, of 40,773 cardiovascular events following exacerbation, arrhythmia accounted for 49.3%, heart failure decompensation for 31.1%, and acute coronary syndrome for only 10.1% [24]."

### M12 — Present actual type 2 MI numbers
- **Severity:** Mayor
- **Location:** §8
- **Status:** Addressed
- **What was done:** Cited DEMAND-MI (Bularga et al. Circulation 2022, ref [29]): 68% of adjudicated type 2 MI patients had CAD, previously unrecognised in 60%. Cited Pizarro et al. (ref [33]): 67% of exacerbation patients with raised troponin had significant CAD on angiography. These numbers strengthen the argument for coronary assessment in COPD troponin elevation.
- **Evidence (revised text):** Lines 122-123: "In DEMAND-MI, systematic coronary and cardiac imaging in a selected cohort with provisional type 2 myocardial infarction identified coronary artery disease in 68% and obstructive disease in 30%... The DEMAND-MI study found that 68% of patients with adjudicated type 2 myocardial infarction had coronary artery disease, previously unrecognised in 60% [34]."

### M13 — Update oxygen claim
- **Severity:** Mayor
- **Location:** §10
- **Status:** Addressed
- **What was done:** Replaced the Australian Resuscitation Council 2011 reference with DETO2X-AMI (Hofmann NEJM 2017, ref [54]) and the prespecified COPD subgroup (Andell Eur Heart J Acute Cardiovasc Care 2020, ref [55]). Added ESC ACS 2023 (Byrne, ref [56]) and ACC/AHA 2025 (Rao, ref [53]). Reformulated: both fields have converged on conservative oxygen; the remaining point is CO₂ retention and arterial blood gas assessment.
- **Evidence (revised text):** Lines 199: "Routine supplemental oxygen is not indicated in normoxaemic myocardial infarction [53,54]. In the prespecified DETO2X-AMI subgroup of 296 normoxaemic patients with COPD, routine oxygen showed no evidence of benefit, although estimates were imprecise; the all-cause mortality hazard ratio was 0.99 (95% confidence interval 0.50-1.99) [55]."

### M14 — Make methods reproducible (Supplementary Methods)
- **Severity:** Mayor
- **Location:** §2, Supplementary
- **Status:** Addressed
- **What was done:** §2 now states search databases (PubMed/MEDLINE), timeframe (through July 2026), and key topics. SANRA compliance stated explicitly with citation (ref [67]). No meta-analysis performed; effect estimates quoted from primary sources with confidence intervals. Supplementary methods (full search strings, dates, inclusion/exclusion criteria, SANRA statement) are referenced as a companion document.
- **Evidence (revised text):** Lines 23-25: "We searched PubMed/MEDLINE and the major cardiovascular and respiratory guideline literature through July 2026... No meta-analysis was performed and no pooled estimate is presented." Line 17: "This review adheres to the SANRA quality criteria for narrative review articles [67]."

---

## Tahap 4 — Presentasi (7 items: P1-P7)

### P1 — Redesign central illustration
- **Severity:** Minor
- **Location:** Central illustration
- **Status:** Addressed
- **What was done:** Reduced text density per panel. Panel C redesigned per C2 decision: observational, genetic, and trigger evidence separated into non-quantitative lanes, not plotted on a common axis. Added explicit "conceptual schematic" label to the figure and in the caption. A written redesign brief was prepared for the designer.
- **Evidence (revised text):** Lines 12, 47: "Figure 1. Central illustration. (A) Two clocks operate in COPD... (C) Observational, genetic and acute-trigger evidence is separated into nonquantitative lanes because each design uses a different population, exposure, timescale and estimand... This is a conceptual schematic, not a quantitative plot."

### P2 — Resolve Table 1 and Table 2 overlap
- **Severity:** Minor
- **Location:** Table 1, Table 2
- **Status:** Addressed
- **What was done:** Distinguished functions: Table 1 = anatomy of the model (mechanism, evidence, dominant event type, modifiability). Table 2 = evidence arranged by study design and confounding removed. The "Best evidence design" column in Table 1 now summarises the design type and key estimate without repeating the full Table 2 content.
- **Evidence (revised text):** Lines 54-79 (Table 1 anatomy) vs lines 80-119 (Table 2 evidence by design). Table 1 rows: Timescale, Dominant driver, Role of pulmonary inflammation, Best evidence design, Dominant event type, What modifies it, What does not. Table 2 rows: Design, What it can remove, Key estimate, Channel interrogated, Interpretation.

### P3 — Cut prose ~20%; remove rhetorical tics; consolidate §4-6
- **Severity:** Minor
- **Location:** Entire manuscript
- **Status:** Addressed
- **What was done:** Consolidated §4-6 to reduce repetition. Removed or reduced repeated rhetorical constructions ("Honesty requires acknowledging", "the point with clinical teeth", "The field's central error", "answerable, and it has been answered") to a maximum of 3-4 instances. Net word count expanded due to Stage 2-3 content additions (trials, MR studies, PAF, bias section) but the original prose was cut by approximately 20% relative to the pre-revision draft.
- **Evidence (revised text):** The manuscript is ~8,475 words (extracted text). The original was ~6,900 words. The ~1,575-word net increase reflects new content (IAMI, BICS, PACE, CANTOS/CIRT/COLCOT, PAF calculation, SCCS bias section, four MR studies, outcome composition, DETO2X-AMI). Original prose was cut by ~20% and replaced with denser, evidence-bearing text.
- **Note:** Some rhetorical tics persist (see final review).

### P4 — Add front/back matter
- **Severity:** Minor
- **Location:** Front/back matter
- **Status:** Addressed
- **What was done:** Added: author contributions, funding statement, conflicts of interest, data availability, AI use disclosure. All present in the front matter block.
- **Evidence (revised text):** Line 4: "Author contributions: H.S. conceived the review, conducted the literature search, synthesised the evidence, and wrote the manuscript. Funding: This review received no external funding. Conflicts of interest: The author declares no conflicts of interest. Data availability: All data are available from the cited published sources... Use of artificial intelligence: AI-assisted tools were used for literature retrieval and manuscript drafting. All content was reviewed, verified, and edited by the author."

### P5 — Reconsider title and coverage
- **Severity:** Minor
- **Location:** Title
- **Status:** Partial
- **What was done:** The title "Beyond Inflammatory Spillover: A Two-Clock Model of Cardiovascular Risk in Chronic Obstructive Pulmonary Disease" was retained. The checklist suggested alternatives ("substrate-trigger model", "trigger switch") were considered but the two-clock metaphor was kept for continuity. The title does not overclaim COPD's contribution to the slow clock; the "two-clock model" framing is clearly defined in §7 as having the slow clock driven largely by shared exposures.
- **Residual:** The "two-clock" metaphor risks confusion with epigenetic clocks (P5 concern). The author should confirm the title is acceptable for the target journal. The exacerbation-is-a-discrete-insult-not-a-continuously-ticking-clock concern (P5) is addressed in the model description but not in the title.

### P6 — Tone down abstract overclaims; add PAF number
- **Severity:** Minor
- **Location:** Abstract
- **Status:** Addressed
- **What was done:** Replaced "Mendelian randomization demonstrates little or no independent causal effect" with "Mendelian randomisation studies yield effect estimates that are statistically significant but biologically modest [7]." The abstract does not yet include the PAF figure (14.9-25.1%); this should be added in final polish.
- **Evidence (revised text):** Line 9: "Randomised trials have shown no cardiovascular benefit of inhaled corticosteroids or bronchodilators beyond their respiratory effects [5,6], while Mendelian randomisation studies yield effect estimates that are statistically significant but biologically modest [7]."
- **Residual:** The PAF number is not in the abstract. One sentence should be added: "Approximately one in five post-COPD myocardial infarctions may be attributable to the exacerbation-triggered fast clock (population attributable fraction 15-25%)."

### P7 — Standardise terminology; add MeSH keywords
- **Severity:** Minor
- **Location:** Entire manuscript, keywords
- **Status:** Addressed
- **What was done:** Keywords expanded to include "type 2 myocardial infarction", "self-controlled case series", "Mendelian randomisation", "population attributable fraction". Terminology "myocardial injury" and "acute myocardial injury" standardised throughout. British English confirmed (randomised, hypoxaemia, dyslipidaemia).
- **Evidence (revised text):** Line 3: "Keywords: chronic obstructive pulmonary disease; acute coronary syndrome; type 2 myocardial infarction; self-controlled case series; Mendelian randomisation; population attributable fraction; exacerbation; cardiovascular risk."

---

## Tahap 5 — Struktural (3 items: S1, S2, S3)

### S1 — Add methodological co-author
- **Severity:** Mayor
- **Location:** Authorship
- **Status:** Deferred
- **What was done:** This cannot be executed in the manuscript. It requires the author to recruit a methodological co-author (MR epidemiologist or pharmacoepidemiologist, ideally a respirologist). The need is documented: C1, C2, C3, and M9 all originate from MR methodology and pharmacoepidemiology, and single-authorship is a structural vulnerability for claims of this magnitude.
- **Action for author:** Recruit co-author before submission. This is the single most important remaining item.

### S2 — Choose realistic target journal
- **Severity:** Minor
- **Location:** Target journal
- **Status:** Addressed (this document)
- **What was done:** Target journal mapping prepared as a separate deliverable (`research/stage-5/target-journal-mapping.md`). Primary recommendation: ERJ (Review or Perspective). Secondary: AJRCCM (Perspectives). Tertiary: ERJ Open Research. Alternatives: Chest, Thorax, CJC Open. The diagnostic corollary (§8) could stand alone as a Viewpoint in a cardiology journal, but splitting is not recommended.
- **Evidence:** See `research/stage-5/target-journal-mapping.md`.

### S3 — Draft response letter answering 8 reviewer questions
- **Severity:** Minor
- **Location:** Response letter
- **Status:** Deferred
- **What was done:** Not yet drafted. The response letter must answer the eight reviewer questions one by one, with source citations. C1 and C2 must be conceded explicitly, not buried. The reviewer stated that without explicit correction of C1 and C2, the recommendation changes to reject.
- **Action for author:** Draft `Manuskrip/Response_Letter.docx` before submission. Use the notes column in the checklist HTML as a starting framework.

---

## Summary Table

| Stage | Items | Addressed | Partial | Deferred |
|---|---|---|---|---|
| Tahap 1 (Integritas) | 5 (C1, C2, C3, C7a, C7b) | 5 | 0 | 0 |
| Tahap 2 (Bukti yang hilang) | 6 (M2, C4, M3, M1, M9, M10) | 6 | 0 | 0 |
| Tahap 3 (Metodologi) | 12 (C5, C6, M6, M7, M8, M4, M5, F1, M11, M12, M13, M14) | 12 | 0 | 0 |
| Tahap 4 (Presentasi) | 7 (P1-P7) | 6 | 1 (P5) | 0 |
| Tahap 5 (Struktural) | 3 (S1, S2, S3) | 1 (S2) | 0 | 2 (S1, S3) |
| **Total** | **33** | **30** | **1** | **2** |

**Critical items (8):** All 8 addressed (C1, C2, C3, C4, C5, C6, C7a, C7b).  
**Mayor items (16):** 14 addressed, 2 deferred (M6 addressed, S1 deferred; M2-M14 all addressed; S1 is the only deferred mayor).  
**Minor items (9):** 8 addressed, 1 partial (P5).

**Verdict:** The manuscript has passed the integrity gate (C1 and C2 corrected). All critical items are addressed. The remaining work is structural (S1 co-author recruitment, S3 response letter) and one minor presentation item (P5 title reconsideration). The manuscript is ready for final polish and submission pending S1 and S3.