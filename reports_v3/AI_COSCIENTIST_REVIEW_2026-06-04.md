# AI Co-Scientist Review: v3 Unbiased PDAC AND-Gate Biosensor Project

Review date: 2026-06-04  
Reviewed branch baseline: `origin/v3-pipeline-unbiased`  
Working branch: `codex/v3-ai-scientist-review`

## Executive Summary

The project has moved from a single attractive pair narrative into a substantially
more rigorous v3 workflow. The strongest new contribution is not that the final
pair is already biologically proven, but that the analysis now explicitly audits
model consensus, threshold instability, search-space dependence, locked external
validation, and circularity risk in single-cell validation.

The current default pair is:

```text
PKM AND ADAM22
```

The pair achieves locked GSE28735 external validation ROC-AUC 0.8588,
sensitivity 80.0%, and specificity 82.2%. This is useful but moderate evidence.
It should be described as a computationally prioritized candidate, not as a
validated PDAC detector or deployable synthetic-biology circuit.

## What Was Newly Added

1. `analysis_v3/` now implements a third-generation unbiased ensemble pipeline.
2. Pure L1 logistic regression was replaced with SAGA Elastic Net Logistic
   Regression plus Random Forest and XGBoost model consensus.
3. GSE62452 is used as a same-cohort validation filter before final pair choice.
4. GSE28735 is held out as a locked external validation cohort and loaded only
   after pair selection is frozen.
5. Top-N pair search sweeps now evaluate top 20, 50, 100, and 200 consensus
   gene search spaces with verified pair counts.
6. Threshold instability is explicitly audited across model-derived thresholds.
7. GSE28735 metadata parsing is audited to confirm 45 tumor and 45 normal
   samples.
8. scRNA validation now includes marker-overlap checks so candidate genes are
   not used as their own annotation markers.
9. Reports under `reports_v3/` are generated from tables to improve internal
   consistency.

## Main Strengths

- The v3 pipeline adds a true-lock audit for GSE28735, which directly addresses
  external-validation leakage risk.
- The output row-count audit verifies that pair-search tables are complete:
  top20 = 190, top50 = 1,225, top100 = 4,950, and top200 = 19,900 pairs.
- The final default pair has weak tumor Spearman correlation in discovery
  (`r = 0.063`) and locked external validation Spearman `r = 0.111`, supporting
  partial independence rather than redundant co-expression.
- The scRNA marker-overlap audit passes for the v3 candidate genes.
- The project now clearly distinguishes discovery, same-cohort validation, and
  locked external validation.

## Remaining Insufficiencies

### 1. Pair ranking is not yet search-space robust

The top-ranked pair changes with the candidate search boundary:

| Search space | Top-ranked pair |
|---:|---|
| Top 20 | OCIAD2 + EDIL3 |
| Top 50 | OCIAD2 + EDIL3 |
| Top 100 | PKM + ADAM22 |
| Top 200 | PKM + ADAM22 |

The top20-pair overlap across search spaces is low. For example, top100 vs
top200 shares only 3 of the top 20 pairs. This means the final pair is stable in
larger search spaces, but the pair-ranking landscape remains sensitive to the
candidate pool.

### 2. Bulk validation is moderate, not decisive

Locked GSE28735 validation:

| Metric | Value |
|---|---:|
| ROC-AUC | 0.8588 |
| Sensitivity | 80.0% |
| Specificity | 82.2% |
| TP / FP / TN / FN | 36 / 8 / 37 / 9 |

This is a useful improvement over failed external transfer in earlier versions,
but it is not enough to claim clinical diagnostic performance.

### 3. scRNA validation weakens cell-level biosensor interpretation

For the final pair, putative malignant ductal epithelial co-expression is only
0.26% by the current marker-score validation. CAF co-expression is 7.78%, and
small nonzero CD8/T-cell co-expression is present. This suggests that bulk-level
classification performance may not translate cleanly into cell-level AND-gate
activation.

### 4. Thresholds are still computational decision boundaries

The current K values are model-derived expression thresholds. They are not
biochemical affinities, promoter activation constants, or experimentally measured
sensor tuning values. This remains a major wet-lab translation gap.

### 5. Uncertainty reporting has started, but remains incomplete

This review branch adds approximate locked-validation 95% intervals from the
aggregate GSE28735 table. Sensitivity, specificity, and accuracy use Wilson
intervals; ROC-AUC uses a Hanley-McNeil approximation. The next statistical
layer should export sample-level gate scores and add bootstrap or DeLong AUC
intervals, calibration curves, and decision-threshold sensitivity for the final
ON/OFF call.

### 6. Spatial validation remains incomplete

The reports correctly state that spatial coordinates were not completed. Any
tissue colocalization claim should remain future work until real spatial data are
processed.

## Recommended Next Steps

1. Export sample-level GSE28735 gate scores and replace approximate aggregate
   uncertainty intervals with bootstrap or DeLong intervals.
2. Add a threshold perturbation analysis for the final v3 pair, not only
   threshold-instability reporting.
3. Test whether top-ranked pairs remain stable under resampling of discovery
   samples and under alternative pair-score weights.
4. Add calibration plots or reliability curves for model outputs if probabilities
   are used in downstream interpretation.
5. Prioritize full non-circular scRNA validation with unsupervised clustering,
   copyKAT/inferCNV-style malignant-cell support, and patient-level prevalence.
6. Complete real spatial validation only if Visium or equivalent coordinate files
   are locally available.
7. Add a wet-lab feasibility table for each candidate gene: promoter availability,
   expected cell localization, essential housekeeping risk, expression dynamic
   range, and feasible sensing architecture.
8. Keep report claims bounded: computational prioritization, not biological
   causality; locked external validation, not clinical utility; model threshold,
   not biochemical Kd.

## AI Research-Team Notes

The AI Co-Scientist toolkit was initialized under `.ai_scientist/` for this
project. The biomedical board emphasized claim discipline, cohort definition,
leakage-resistant validation, reproducible workflows, and evidence grading. The
security auditor found no critical exposed secrets, but recommended stronger
`.gitignore` credential patterns and explicit handling of pseudonymous
patient-level sample IDs.

## Current Status

The project is worth continuing. The most valuable next push is not another
presentation polish pass; it is robustness and translational feasibility:

```text
search-space robustness
plus sample-level uncertainty and calibration
plus full single-cell/spatial validation
plus wet-lab implementability review
```
