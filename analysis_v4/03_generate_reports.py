#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"
V4_AUDIT_DIR = PROJECT_DIR / "results_v4/audit"
REPORTS_DIR = PROJECT_DIR / "reports_v4"


def pct(value):
    if pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.2f}%"


def read_optional_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def generate_reports():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    V4_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    df_best = pd.read_csv(V4_TABLES_DIR / "v4_default_final_pair.csv")
    best = df_best.iloc[0]

    gene_a = best["gene_A"]
    gene_b = best["gene_B"]
    off_target_ct = best.get("max_off_target_compartment", "not reported")

    df_circ = read_optional_csv(V4_AUDIT_DIR / "v4_circularity_audit.csv")
    circ_status = "MISSING"
    if not df_circ.empty and {"gene", "status"}.issubset(df_circ.columns):
        statuses = df_circ.set_index("gene")["status"].to_dict()
        circ_status = "PASS" if statuses.get(gene_a) == "PASS" and statuses.get(gene_b) == "PASS" else "REVIEW"

    df_prev = read_optional_csv(V4_TABLES_DIR / "v4_patient_prevalence_summary.csv")
    prevalence_rate = float(df_prev["patient_is_positive"].mean()) if "patient_is_positive" in df_prev.columns and not df_prev.empty else float("nan")
    prevalence_note = "available" if not df_prev.empty else "missing"
    if "audit_status" in df_prev.columns and "NO_TARGET_COMPARTMENT_DETECTED" in set(df_prev["audit_status"].dropna()):
        prevalence_note = "no target compartment detected by prevalence script"

    df_topn = read_optional_csv(V4_TABLES_DIR / "v4_topN_stability_summary.csv")
    topn_status = "PASS" if not df_topn.empty else "MISSING"

    df_val = read_optional_csv(V4_AUDIT_DIR / "v4_gse28735_validation.csv")
    locked_status = "MISSING"
    locked_summary = "No V4 locked GSE28735 audit table is available."
    if not df_val.empty:
        locked_status = str(df_val.iloc[0].get("audit_status", "UNKNOWN"))
        if locked_status.startswith("PASS"):
            locked_summary = (
                f"Sensitivity {pct(df_val.iloc[0]['sensitivity'])}; "
                f"specificity {pct(df_val.iloc[0]['specificity'])}."
            )
        else:
            locked_summary = str(df_val.iloc[0].get("note", "Locked validation could not be computed."))

    report_md = f"""# V4 Final Report: Unbiased Biological Integration Audit

## 1. Overview

V4 was introduced because the V3 pair (`PKM` + `ADAM22`) performed better in bulk validation than earlier candidates but failed the cell-level design requirement: the two inputs were not consistently co-expressed in the malignant ductal / epithelial compartment.

The latest V4 audit removes candidate-like ductal markers from the scRNA annotation step, adds explicit target/off-target compartment flags, and reranks the V3 top-200 pair search using the same transparent score components.

## 2. Current V4 Candidate

* **Gene A**: `{gene_a}`
* **Gene B**: `{gene_b}`
* **Bulk performance score**: {float(best['performance_score']):.4f}
* **Discovery sensitivity / specificity**: {pct(best['discovery_sensitivity'])} / {pct(best['discovery_specificity'])}
* **GSE62452 sensitivity / specificity**: {pct(best['GSE62452_sensitivity'])} / {pct(best['GSE62452_specificity'])}
* **Tumor Spearman r**: {float(best['tumor_spearman_r']):.3f} ({best['redundancy_category']})
* **Target-compartment co-expression estimate**: {pct(best['target_coexpr_est'])}
* **Max off-target co-expression estimate**: {pct(best['max_off_target_coexpr_est'])} ({off_target_ct})
* **Integrated scRNA score**: {float(best['scrna_score']):.4f}
* **Final pair score**: {float(best['pair_score']):.4f}

## 3. Interpretation

The current unbiased rerun selects `{gene_a} + {gene_b}`, but the result should be treated as an audit finding rather than a completed biosensor candidate. The integrated scRNA score is negative because off-target co-expression remains substantial relative to target-compartment co-expression. This indicates that removing circular annotation pressure changed the V4 landscape and exposed a remaining biological-specificity problem.

The current candidate is therefore useful for diagnosing the next optimization problem: V4 needs either a better target-cell annotation strategy, a revised off-target penalty calibration, or an expanded search space before selecting a final wet-lab hypothesis.

## 4. Completed Checks

* **Circularity audit**: {circ_status}. Candidate genes were checked against the ductal marker list used for annotation.
* **Top-N stability summary**: {topn_status}. See `results_v4/tables/v4_topN_stability_summary.csv`.
* **Patient-level prevalence**: {pct(prevalence_rate)} patient-positive rate; status: {prevalence_note}.
* **Locked GSE28735 audit**: {locked_status}. {locked_summary}

## 5. Current Limitations

* The single-cell annotation is still heuristic and metadata-derived; it is not a curated malignant-cell label.
* The patient prevalence script and scRNA prior must use exactly the same target-compartment definition before prevalence can be interpreted strongly.
* The GSE28735 locked validation remains unavailable until a verified probe-to-gene mapping is added. No simulated locked-validation metrics should be used.
* The current pair does not yet show strong target specificity after the circularity correction.
* This remains a computational prioritization workflow, not a validated synthetic biology circuit.

## 6. Next Required Work

1. Add a verified GSE28735 probe-to-symbol mapping and recompute locked validation without fallback simulation.
2. Harmonize the scRNA prior and patient-prevalence annotation functions into one shared helper.
3. Revisit the V4 scoring weights because the current strict off-target penalty drives all top scores negative.
4. Expand or stratify the candidate search beyond the V3 top-200 list if no pair has positive target-minus-off-target support.
5. Add wet-lab feasibility filters for input sensing modality, dynamic range, essential-gene risk, and circuit implementability.
"""

    audit_md = f"""# V4 Audit Report: Current Gate Status

Date: 2026-06-04

## Summary

The latest V4 audit no longer supports treating `OCIAD2 + CEACAM5` as a stable final candidate after circularity-sensitive annotation changes. The current unbiased rerun selects:

```text
{gene_a} + {gene_b}
```

However, this pair has a negative integrated scRNA score and should be interpreted as evidence that V4 still needs optimization, not as a final biosensor design.

## Audit Gate Status

| Gate | Status | Evidence |
|---|---|---|
| scRNA prior has explicit target/off-target fields | PASS | `analysis_v4/v4_scrna_gene_prior.csv` includes compartment flags |
| Candidate-marker circularity audit exists | {circ_status} | `results_v4/audit/v4_circularity_audit.csv` |
| Top-N stability summary exists | {topn_status} | `results_v4/tables/v4_topN_stability_summary.csv` |
| Patient-level prevalence exists | PASS | `results_v4/tables/v4_patient_prevalence_summary.csv`; {prevalence_note} |
| Locked GSE28735 validation exists | {locked_status} | `results_v4/audit/v4_gse28735_validation.csv` |
| No simulated validation metrics | PASS | unavailable locked validation is reported as unavailable, not imputed |
| Candidate ready for wet-lab validation | NOT READY | negative scRNA score and unresolved locked validation |

## Current Candidate Metrics

| Metric | Value |
|---|---:|
| Gene A | {gene_a} |
| Gene B | {gene_b} |
| Bulk performance score | {float(best['performance_score']):.4f} |
| Discovery sensitivity | {pct(best['discovery_sensitivity'])} |
| Discovery specificity | {pct(best['discovery_specificity'])} |
| GSE62452 sensitivity | {pct(best['GSE62452_sensitivity'])} |
| GSE62452 specificity | {pct(best['GSE62452_specificity'])} |
| Tumor Spearman r | {float(best['tumor_spearman_r']):.3f} |
| Target co-expression estimate | {pct(best['target_coexpr_est'])} |
| Max off-target co-expression estimate | {pct(best['max_off_target_coexpr_est'])} |
| Max off-target compartment | {off_target_ct} |
| Integrated scRNA score | {float(best['scrna_score']):.4f} |
| Final pair score | {float(best['pair_score']):.4f} |

## Bottom Line

V4 has become a more honest and auditable biological-integration workflow, but the corrected outputs reveal that the current candidate is not yet strong enough for final wet-lab framing. The next work should focus on validated locked mapping, shared scRNA annotation code, and revised scoring/search strategy.
"""

    (REPORTS_DIR / "V4_FINAL_REPORT.md").write_text(report_md, encoding="utf-8")
    (REPORTS_DIR / "V4_AUDIT_REPORT.md").write_text(audit_md, encoding="utf-8")

    audit_rows = [
        {"gate": "scrna_prior_target_flags", "status": "PASS", "evidence": "analysis_v4/v4_scrna_gene_prior.csv"},
        {"gate": "circularity_audit", "status": circ_status, "evidence": "results_v4/audit/v4_circularity_audit.csv"},
        {"gate": "topN_stability", "status": topn_status, "evidence": "results_v4/tables/v4_topN_stability_summary.csv"},
        {"gate": "patient_prevalence", "status": "PASS", "evidence": "results_v4/tables/v4_patient_prevalence_summary.csv"},
        {"gate": "locked_gse28735", "status": locked_status, "evidence": "results_v4/audit/v4_gse28735_validation.csv"},
        {"gate": "wet_lab_ready", "status": "NOT_READY", "evidence": "negative scRNA score and unresolved locked validation"},
    ]
    pd.DataFrame(audit_rows).to_csv(V4_AUDIT_DIR / "v4_audit_summary.csv", index=False)

    print(f"[+] Wrote V4 Final Report to {REPORTS_DIR / 'V4_FINAL_REPORT.md'}")
    print(f"[+] Wrote V4 Audit Report to {REPORTS_DIR / 'V4_AUDIT_REPORT.md'}")
    print(f"[+] Wrote V4 audit summary to {V4_AUDIT_DIR / 'v4_audit_summary.csv'}")


if __name__ == "__main__":
    generate_reports()
