#!/usr/bin/env python3
"""Approximate uncertainty intervals for locked GSE28735 validation metrics.

This script uses only the locked aggregate validation table. It does not reload
GSE28735 and therefore preserves the true-lock audit boundary. Sensitivity,
specificity, and accuracy use Wilson score intervals. ROC-AUC uses the
Hanley-McNeil large-sample approximation because sample-level gate scores are
not stored in the repository.
"""

from pathlib import Path
import math
import pandas as pd


PROJECT_DIR = Path(__file__).parent.parent.resolve()
TABLES_DIR = PROJECT_DIR / "results_v3" / "tables"
INPUT_PATH = TABLES_DIR / "locked_gse28735_final_validation.csv"
OUTPUT_PATH = TABLES_DIR / "locked_gse28735_uncertainty_intervals.csv"


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def wilson_interval(successes, n, z=1.959963984540054):
    if n <= 0:
        return (float("nan"), float("nan"))
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    half_width = z * math.sqrt((p * (1 - p) / n) + (z2 / (4 * n * n))) / denom
    return (clamp01(center - half_width), clamp01(center + half_width))


def hanley_mcneil_auc_interval(auc, n_pos, n_neg, z=1.959963984540054):
    """Approximate AUC CI from Hanley and McNeil's variance formula."""
    if n_pos <= 1 or n_neg <= 1:
        return (float("nan"), float("nan"), float("nan"))
    q1 = auc / (2 - auc)
    q2 = (2 * auc * auc) / (1 + auc)
    variance = (
        auc * (1 - auc)
        + (n_pos - 1) * (q1 - auc * auc)
        + (n_neg - 1) * (q2 - auc * auc)
    ) / (n_pos * n_neg)
    se = math.sqrt(max(0.0, variance))
    return (clamp01(auc - z * se), clamp01(auc + z * se), se)


def main():
    df = pd.read_csv(INPUT_PATH)
    row = df.iloc[0]

    tp = int(row["TP"])
    fp = int(row["FP"])
    tn = int(row["TN"])
    fn = int(row["FN"])
    n_pos = tp + fn
    n_neg = tn + fp
    n_total = n_pos + n_neg

    sensitivity = tp / n_pos
    specificity = tn / n_neg
    accuracy = (tp + tn) / n_total
    auc = float(row["ROC_AUC"])

    sens_low, sens_high = wilson_interval(tp, n_pos)
    spec_low, spec_high = wilson_interval(tn, n_neg)
    acc_low, acc_high = wilson_interval(tp + tn, n_total)
    auc_low, auc_high, auc_se = hanley_mcneil_auc_interval(auc, n_pos, n_neg)

    out = pd.DataFrame(
        [
            {
                "dataset": "GSE28735",
                "gene_A": row["gene_A"],
                "gene_B": row["gene_B"],
                "metric": "sensitivity",
                "estimate": sensitivity,
                "ci_method": "Wilson score 95% CI",
                "ci_low": sens_low,
                "ci_high": sens_high,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "note": "Computed from locked aggregate confusion matrix.",
            },
            {
                "dataset": "GSE28735",
                "gene_A": row["gene_A"],
                "gene_B": row["gene_B"],
                "metric": "specificity",
                "estimate": specificity,
                "ci_method": "Wilson score 95% CI",
                "ci_low": spec_low,
                "ci_high": spec_high,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "note": "Computed from locked aggregate confusion matrix.",
            },
            {
                "dataset": "GSE28735",
                "gene_A": row["gene_A"],
                "gene_B": row["gene_B"],
                "metric": "accuracy",
                "estimate": accuracy,
                "ci_method": "Wilson score 95% CI",
                "ci_low": acc_low,
                "ci_high": acc_high,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "note": "Computed from locked aggregate confusion matrix.",
            },
            {
                "dataset": "GSE28735",
                "gene_A": row["gene_A"],
                "gene_B": row["gene_B"],
                "metric": "ROC_AUC",
                "estimate": auc,
                "ci_method": "Hanley-McNeil approximate 95% CI",
                "ci_low": auc_low,
                "ci_high": auc_high,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "note": (
                    f"Approximate SE={auc_se:.4f}. Prefer bootstrap or DeLong CI "
                    "after sample-level gate scores are exported."
                ),
            },
        ]
    )
    out.to_csv(OUTPUT_PATH, index=False)
    print(f"[+] Wrote locked validation uncertainty intervals to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
