#!/usr/bin/env python3
"""Build the Stage 2 reference seed from the approved Stage 1 seed."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research" / "stage-1" / "reference-seed.tsv"
OUTPUT = ROOT / "research" / "stage-2" / "reference-seed.tsv"
FIELDS = [
    "order",
    "citation",
    "doi",
    "pmid",
    "study_design",
    "design_detail",
    "evidence_role",
    "source_quality",
    "disposition",
]


def row(citation, doi, pmid, study_design, design_detail, evidence_role, source_quality, disposition):
    return {
        "citation": citation,
        "doi": doi,
        "pmid": pmid,
        "study_design": study_design,
        "design_detail": design_detail,
        "evidence_role": evidence_role,
        "source_quality": source_quality,
        "disposition": disposition,
    }


ADDITIONS = {
    "m1": [
        row(
            "Muller JE, Tofler GH, Stone PH. Circadian variation and triggers of onset of acute cardiovascular disease. Circulation. 1989;79(4):733-743.",
            "10.1161/01.CIR.79.4.733",
            "2647318",
            "Review or commentary",
            "Historical review of circadian variation and acute cardiovascular triggers",
            "Substrate-trigger precedent",
            "Secondary conceptual evidence",
            "Added for M1 novelty calibration.",
        ),
        row(
            "Mittleman MA, Mostofsky E. Physical, psychological and chemical triggers of acute cardiovascular events: preventive strategies. Circulation. 2011;124(3):346-354.",
            "10.1161/CIRCULATIONAHA.110.968776",
            "21768552",
            "Review or commentary",
            "Narrative review of transient cardiovascular triggers",
            "Transient-trigger framework",
            "Secondary conceptual evidence",
            "Added for M1 novelty calibration.",
        ),
        row(
            "Smeeth L, Thomas SL, Hall AJ, Hubbard R, Farrington P, Vallance P. Risk of myocardial infarction and stroke after acute infection or vaccination. N Engl J Med. 2004;351(25):2611-2618.",
            "10.1056/NEJMoa041747",
            "15602021",
            "Observational study",
            "Self-controlled case series",
            "Acute respiratory infection trigger",
            "Primary within-person evidence",
            "Added for M1 respiratory-trigger precedent.",
        ),
        row(
            "Warren-Gash C, Hayward AC, Hemingway H, et al. Influenza infection and risk of acute myocardial infarction in England and Wales: a CALIBER self-controlled case series study. J Infect Dis. 2012;206(11):1652-1659.",
            "10.1093/infdis/jis597",
            "23048170",
            "Observational study",
            "Self-controlled case series using linked records",
            "Acute respiratory infection trigger",
            "Primary within-person evidence",
            "Added for M1 respiratory-trigger precedent.",
        ),
        row(
            "Kwong JC, Schwartz KL, Campitelli MA, et al. Acute myocardial infarction after laboratory-confirmed influenza infection. N Engl J Med. 2018;378(4):345-353.",
            "10.1056/NEJMoa1702090",
            "29365305",
            "Observational study",
            "Self-controlled case series with laboratory-confirmed influenza",
            "Influenza trigger",
            "Primary within-person evidence",
            "Added for M1 laboratory-confirmed trigger evidence.",
        ),
    ],
    "copd_beta": [
        row(
            "Devereux G, Cotton S, Nath M, McMeekin N, Campbell K, Chaudhuri R, et al. Bisoprolol in patients with chronic obstructive pulmonary disease at high risk of exacerbation: the BICS randomized clinical trial. JAMA. 2024;332(6):462-470.",
            "10.1001/jama.2024.8771",
            "38762800",
            "Randomised trial",
            "Double-blind placebo-controlled COPD trial",
            "Beta-blocker without cardiovascular indication",
            "Primary experimental evidence",
            "Added for C4.",
        ),
        row(
            "Jenkins CR, Martin A, Chang CL, Beasley R, Wrobel JP, McDonald VM, et al; PACE Investigators. Bisoprolol to prevent adverse cardiac events (PACE) in COPD: a multicentre, double-blind, randomised, controlled, phase 3 trial. Lancet Respir Med. 2026;14(3):203-214.",
            "10.1016/S2213-2600(25)00390-X",
            "41579873",
            "Randomised trial",
            "Double-blind placebo-controlled phase 3 COPD trial",
            "Broad cardiopulmonary prevention in COPD",
            "Primary experimental evidence",
            "Added for C4; corrected publication year to 2026.",
        ),
    ],
    "post_mi_beta": [
        row(
            "Silvain J, Cayla G, Ferrari E, Range G, Puymirat E, Delarche N, et al. Beta-blocker interruption or continuation after myocardial infarction. N Engl J Med. 2024;391(14):1277-1286.",
            "10.1056/NEJMoa2404204",
            "39213187",
            "Randomised trial",
            "Open-label noninferiority trial of interruption versus continuation after MI",
            "Long-term beta-blocker continuation after MI",
            "Primary experimental evidence",
            "Added for C4.",
        ),
        row(
            "Ibanez B, Latini R, Rossello X, Dominguez-Rodriguez A, Fernández-Vazquez F, Pelizzoni V, et al. Beta-blockers after myocardial infarction without reduced ejection fraction. N Engl J Med. 2025;393(19):1889-1900.",
            "10.1056/NEJMoa2504735",
            "40888702",
            "Randomised trial",
            "Open-label trial after invasively managed MI with LVEF greater than 40%",
            "Beta-blocker initiation after MI",
            "Primary experimental evidence",
            "Added for C4.",
        ),
        row(
            "Munkhaugen J, Kristensen AMD, Halvorsen S, Holmager T, Olsen MH, Bakken A, et al. Beta-blockers after myocardial infarction in patients without heart failure. N Engl J Med. 2025;393(19):1901-1911.",
            "10.1056/NEJMoa2505985",
            "40888716",
            "Randomised trial",
            "Open-label trial after MI with LVEF at least 40% and no heart failure",
            "Beta-blocker initiation after MI",
            "Primary experimental evidence",
            "Added for C4.",
        ),
    ],
    "vaccination": [
        row(
            "Fröbert O, Götberg M, Erlinge D, Akhtar Z, Christiansen EH, MacIntyre CR, et al. Influenza vaccination after myocardial infarction: a randomized, double-blind, placebo-controlled, multicenter trial. Circulation. 2021;144(18):1476-1484.",
            "10.1161/CIRCULATIONAHA.121.057042",
            "34459211",
            "Randomised trial",
            "Double-blind placebo-controlled vaccination trial after MI",
            "Influenza vaccination after MI",
            "Primary experimental evidence",
            "Added for M2.",
        ),
        row(
            "Loeb M, Roy A, Dokainish H, Dans A, Palileo-Villanueva LM, Karaye K, et al. Influenza vaccine to reduce adverse vascular events in patients with heart failure: a multinational randomised, double-blind, placebo-controlled trial. Lancet Glob Health. 2022;10(12):e1835-e1844.",
            "10.1016/S2214-109X(22)00432-6",
            "36400089",
            "Randomised trial",
            "Double-blind placebo-controlled vaccination trial in heart failure",
            "Influenza vaccination in heart failure",
            "Primary experimental evidence",
            "Added for M2; corrected author order.",
        ),
        row(
            "Modin D, Lassen MCH, Claggett B, Johansen ND, Keshtkar-Jahromi M, Skaarup KG, et al. Influenza vaccination and cardiovascular events in patients with ischaemic heart disease and heart failure: a meta-analysis. Eur J Heart Fail. 2023;25(9):1685-1692.",
            "10.1002/ejhf.2945",
            "37370193",
            "Systematic review or meta-analysis",
            "Post-IVVE cardiovascular RCT meta-analysis",
            "Pooled vaccination effect in IHD and heart failure",
            "High-level synthesis with moderate heterogeneity",
            "Added for M2.",
        ),
        row(
            "Hosseini K, Dastjerdi P, Sahzabi RY, Alipoor A, Masanabadi M, Rezvanian P, et al. Mortality and morbidity benefit after influenza vaccination in high cardiovascular risk population: a systematic review and meta-analysis. Am J Cardiol. 2026;269:147-155.",
            "10.1016/j.amjcard.2026.03.040",
            "41951138",
            "Systematic review or meta-analysis",
            "Mixed RCT and observational meta-analysis with reconstructed individual data",
            "Current broad cardiovascular vaccination synthesis",
            "Mixed-design synthesis",
            "Added for M2 with explicit noncausal limitation.",
        ),
    ],
    "inflammation": [
        row(
            "Ridker PM, Everett BM, Thuren T, MacFadyen JG, Chang WH, Ballantyne C, et al; CANTOS Trial Group. Antiinflammatory therapy with canakinumab for atherosclerotic disease. N Engl J Med. 2017;377(12):1119-1131.",
            "10.1056/NEJMoa1707914",
            "28845751",
            "Randomised trial",
            "Double-blind canakinumab trial after MI with residual inflammatory risk",
            "Pathway-specific anti-inflammatory efficacy",
            "Primary experimental evidence",
            "Added for M3.",
        ),
        row(
            "Ridker PM, Everett BM, Pradhan A, MacFadyen JG, Solomon DH, Zaharris E, et al; CIRT Investigators. Low-dose methotrexate for the prevention of atherosclerotic events. N Engl J Med. 2019;380(8):752-762.",
            "10.1056/NEJMoa1809798",
            "30415610",
            "Randomised trial",
            "Double-blind low-dose methotrexate cardiovascular trial",
            "Pathway-negative anti-inflammatory trial",
            "Primary experimental evidence",
            "Added for M3.",
        ),
        row(
            "Tardif JC, Kouz S, Waters DD, Bertrand OF, Diaz R, Maggioni AP, et al. Efficacy and safety of low-dose colchicine after myocardial infarction. N Engl J Med. 2019;381(26):2497-2505.",
            "10.1056/NEJMoa1912388",
            "31733140",
            "Randomised trial",
            "Double-blind colchicine trial within 30 days after MI",
            "Post-MI anti-inflammatory efficacy",
            "Primary experimental evidence",
            "Added for M3.",
        ),
        row(
            "Nidorf SM, Fiolet ATL, Mosterd A, Eikelboom JW, Schut A, Opstal TSJ, et al; LoDoCo2 Trial Investigators. Colchicine in patients with chronic coronary disease. N Engl J Med. 2020;383(19):1838-1847.",
            "10.1056/NEJMoa2021372",
            "32865380",
            "Randomised trial",
            "Double-blind colchicine trial after tolerance run-in",
            "Chronic coronary anti-inflammatory efficacy",
            "Primary experimental evidence with run-in limitation",
            "Added for M3.",
        ),
    ],
}


def main():
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        stage1 = {int(item["order"]): item for item in csv.DictReader(handle, delimiter="\t")}

    output = []
    for old_order in range(1, 45):
        output.append({key: stage1[old_order].get(key, "") for key in FIELDS if key != "order"})
        if old_order == 12:
            output.extend(ADDITIONS["m1"])
        if old_order == 33:
            output.extend(ADDITIONS["copd_beta"])
        if old_order == 36:
            output.extend(ADDITIONS["post_mi_beta"])
        if old_order == 38:
            output.extend(ADDITIONS["vaccination"])
        if old_order == 44:
            output.extend(ADDITIONS["inflammation"])

    if len(output) != 62:
        raise RuntimeError(f"Expected 62 records, built {len(output)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for index, item in enumerate(output, start=1):
            writer.writerow({"order": index, **item})
    print(f"Wrote {len(output)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
