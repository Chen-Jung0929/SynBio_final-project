#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"
REPORTS_DIR = PROJECT_DIR / "reports_v5"


def pct(value):
    if pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.1f}%"


def generate_reports():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    final_pair_file = V5_TABLES_DIR / "v5_default_final_pair.csv"
    if not final_pair_file.exists():
        report_md = """# V5 Report: Single-Cell First Discovery

## Status

No V5 final pair has been generated yet.

Run:

```powershell
python analysis_v5\\01_scrna_discovery.py
python analysis_v5\\02_bulk_validation.py
```

If Phase 1 produces no candidates or Phase 2 lacks bulk inputs, the audit tables
in `results_v5/audit/` should record that unavailable status rather than
fabricating a final pair.
"""
        (REPORTS_DIR / "V5_FINAL_REPORT.md").write_text(report_md, encoding="utf-8")
        print("[-] V5 final pair not found. Wrote status-only report.")
        return

    best = pd.read_csv(final_pair_file).iloc[0]
    gene_a = best["gene_A"]
    gene_b = best["gene_B"]
    off_target = best.get("max_off_target_coexpr", best.get("off_target_coexpr", float("nan")))
    off_target_ct = best.get("max_off_target_compartment", "not reported")

    report_md = f"""# V5 Final Report: Single-Cell First Discovery

## 1. Executive Summary

V5 reverses the V1-V4 workflow. Instead of selecting genes from bulk RNA-seq and
then checking single-cell localization afterward, V5 first searches for AND-gate
pairs in malignant ductal / epithelial single cells and only then evaluates
bulk-cohort generalization.

This report should be interpreted as a computational candidate-prioritization
summary, not as evidence of a validated diagnostic or working synthetic circuit.

## 2. Current V5 Candidate

* **Gene A**: `{gene_a}`
* **Gene B**: `{gene_b}`

### Phase 1: Single-Cell Discovery Metrics

* **Target co-expression**: {pct(best['target_coexpr'])}
* **Max off-target co-expression**: {pct(off_target)} ({off_target_ct})
* **Patient-positive rate**: {pct(best.get('patient_positive_rate', float('nan')))}
* **Expression correlation**: {float(best['correlation']):.3f}

### Phase 2: Bulk Backward Validation Metrics

* **TCGA/GTEx bulk AUC**: {float(best['bulk_auc']):.3f}
* **Threshold instability**: {float(best['threshold_instability']):.3f}
* **Final V5 score**: {float(best['final_score']):.3f}

## 3. Interpretation

`{gene_a} + {gene_b}` is the current best V5 computational hypothesis under the
available filters. The key question is whether it remains target-prevalent,
off-target-low, patient-robust, and detectable in independent bulk cohorts.

This result does not prove biological causality, clinical diagnostic value, or
wet-lab implementability. It should be used to prioritize the next round of
validation and circuit-feasibility review.

## 4. Required Follow-Up

1. Confirm the malignant-cell annotation with an independent or curated label.
2. Validate off-target behavior across additional scRNA or spatial datasets.
3. Recompute external bulk validation with verified probe-to-gene mappings.
4. Evaluate wet-lab sensing modality, dynamic range, essentiality, and circuit
   implementation constraints.
"""
    (REPORTS_DIR / "V5_FINAL_REPORT.md").write_text(report_md, encoding="utf-8")
    print(f"[+] Wrote V5 Final Report to {REPORTS_DIR / 'V5_FINAL_REPORT.md'}")


if __name__ == "__main__":
    generate_reports()
