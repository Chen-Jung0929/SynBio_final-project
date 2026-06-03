#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"
REPORTS_DIR = PROJECT_DIR / "reports_v5"


def pct(value):
    if value == "" or pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.1f}%"


def text(value):
    if value == "" or pd.isna(value):
        return ""
    return str(value)


def read_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def render_threshold_table(df_profiles):
    if df_profiles.empty:
        return "No threshold-profile audit is available."

    rows = [
        "| Profile | Passing pairs | Top pair | Target | Off-target | Off-target metric | Status |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for _, row in df_profiles.iterrows():
        rows.append(
            f"| {row['profile']} | {int(row['passing_pairs'])} | {text(row.get('top_pair', ''))} | "
            f"{pct(row.get('top_target_coexpr', ''))} | {pct(row.get('top_off_target', ''))} | "
            f"{row['off_target_metric']} | {row['audit_status']} |"
        )
    return "\n".join(rows)


def generate_reports():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    df_scrna = read_csv(V5_TABLES_DIR / "v5_scrna_candidates.csv")
    df_bulk = read_csv(V5_AUDIT_DIR / "v5_bulk_backward_validation_audit.csv")
    df_profiles = read_csv(V5_AUDIT_DIR / "v5_threshold_profile_summary.csv")

    if df_scrna.empty:
        best_str = "None"
        scrna_metrics = "No V5 scRNA-first candidates are available."
        candidate_count = 0
        max_compartment_status = "NO_CANDIDATES"
    else:
        best = df_scrna.iloc[0]
        best_str = f"{best['gene_A']} + {best['gene_B']} (Phase 1 only; pending bulk validation)"
        candidate_count = len(df_scrna)
        max_compartment_status = "REVIEW"
        if float(best["max_off_target_coexpr"]) > 0.10:
            max_compartment_status = "FAIL_COMPARTMENT_OFFTARGET_GT_10_PERCENT"
        scrna_metrics = f"""* **Target co-expression**: {pct(best['target_coexpr'])}
* **Pooled off-target co-expression**: {pct(best['pooled_off_target_coexpr'])}
* **Max compartment off-target co-expression**: {pct(best['max_off_target_coexpr'])} ({best['max_off_target_compartment']})
* **Patient-positive rate**: {pct(best['patient_positive_rate'])}
* **Expression correlation**: {float(best['correlation']):.3f}
* **Threshold profile**: `{best['threshold_profile']}`"""

    bulk_status = "MISSING"
    bulk_note = "No bulk backward-validation audit is available."
    if not df_bulk.empty:
        bulk_status = str(df_bulk.iloc[0].get("audit_status", "UNKNOWN"))
        bulk_note = str(df_bulk.iloc[0].get("note", ""))

    report_md = f"""# V5 Final Report: Single-Cell First Discovery

## 1. Executive Summary

V5 reverses the V1-V4 workflow: candidate pairs are first discovered in
single-cell malignant ductal / epithelial cells, then intended to be validated
backward in bulk cohorts.

The current run produced **{candidate_count} Phase-1 scRNA-first candidates** under
an exploratory relaxed threshold profile. This is useful progress, but it is not
a final biosensor result. The top Phase-1 pair still has high compartment-level
off-target co-expression, especially in mast cells, and bulk backward validation
is unavailable in this local worktree because the processed bulk expression
matrix is missing.

## 2. Current V5 Phase-1 Candidate

* **Top pair**: {best_str}

### Phase 1 Metrics

{scrna_metrics}

### Phase 2 Bulk Backward Validation

* **Status**: {bulk_status}
* **Note**: {bulk_note}

## 3. Threshold-Profile Audit

{render_threshold_table(df_profiles)}

## 4. Interpretation

The relaxed pooled off-target rule can produce candidate pairs, but this should
not be confused with passing a strict compartment-level safety screen. In the
current generated candidate set, no pair passes the stricter max-compartment
off-target profiles in `v5_threshold_profile_summary.csv`.

The correct current claim is:

```text
V5 produced exploratory scRNA-first candidate hypotheses, but no final validated
AND-gate biosensor input pair yet.
```

## 5. Required Next Work

1. Add or regenerate `data/processed/expression_matrix.csv.gz` so bulk backward
   validation can run.
2. Re-run threshold-profile sweeps and report strict, intermediate, and relaxed
   gates separately.
3. Treat mast-cell off-target co-expression as a major V5 design risk.
4. Validate candidate localization in an independent scRNA or spatial dataset.
5. Add wet-lab feasibility review before presenting any pair as a buildable
   synthetic-biology input module.
"""

    audit_md = f"""# V5 Audit Report

## Core V5 Gates

| Gate | Status | Evidence |
|---|---|---|
| scRNA-first Phase 1 executed | PASS | `results_v5/tables/v5_scrna_candidates.csv` has {candidate_count} rows |
| Threshold profile named | PASS | `threshold_profile` column present |
| Patient robustness measured | PASS | `patient_positive_rate` column present |
| Max off-target compartment reported | PASS | `max_off_target_compartment` column present |
| Strict max-compartment off-target gate | {max_compartment_status} | Top candidate max off-target = {pct(df_scrna.iloc[0]['max_off_target_coexpr']) if not df_scrna.empty else 'NA'} |
| Bulk backward validation | {bulk_status} | {bulk_note} |
| Wet-lab feasibility | PENDING | No promoter/sensor/dynamic-range feasibility review yet |

## Threshold-Profile Summary

{render_threshold_table(df_profiles)}

## Bottom Line

V5 is now producing auditable scRNA-first hypotheses. It has not yet produced a
final candidate suitable for wet-lab framing because compartment-level off-target
activation and missing bulk backward validation remain unresolved.
"""

    (REPORTS_DIR / "V5_FINAL_REPORT.md").write_text(report_md, encoding="utf-8")
    (REPORTS_DIR / "V5_AUDIT_REPORT.md").write_text(audit_md, encoding="utf-8")
    print(f"[+] Wrote V5 Final Report to {REPORTS_DIR / 'V5_FINAL_REPORT.md'}")
    print(f"[+] Wrote V5 Audit Report to {REPORTS_DIR / 'V5_AUDIT_REPORT.md'}")


if __name__ == "__main__":
    generate_reports()
