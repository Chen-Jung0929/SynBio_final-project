# V5 Final Report: Single-Cell First Discovery

## 1. Executive Summary

V5 reverses the V1-V4 workflow: candidate pairs are first discovered in
single-cell malignant ductal / epithelial cells, then intended to be validated
backward in bulk cohorts.

The current run produced **34 Phase-1 scRNA-first candidates** under
an exploratory relaxed threshold profile. This is useful progress, but it is not
a final biosensor result. The top Phase-1 pair still has high compartment-level
off-target co-expression, especially in mast cells, and bulk backward validation
is unavailable in this local worktree because the processed bulk expression
matrix is missing.

## 2. Current V5 Phase-1 Candidate

* **Top pair**: S100A14 + OCIAD2 (Phase 1 only; pending bulk validation)

### Phase 1 Metrics

* **Target co-expression**: 65.8%
* **Pooled off-target co-expression**: 8.5%
* **Max compartment off-target co-expression**: 25.7% (mast cells)
* **Patient-positive rate**: 100.0%
* **Expression correlation**: 0.387
* **Threshold profile**: `exploratory_relaxed_v5_0p60_target_0p10_pooled_offtarget`

### Phase 2 Bulk Backward Validation

* **Status**: UNAVAILABLE_BULK_INPUTS
* **Note**: Missing bulk expression matrix: data/processed/expression_matrix.csv.gz

## 3. Threshold-Profile Audit

| Profile | Passing pairs | Top pair | Target | Off-target | Off-target metric | Status |
|---|---:|---|---:|---:|---|---|
| strict_0p80_target_0p05_pooled_offtarget | 0 |  | NA | NA | pooled_off_target_coexpr | NO_PASSING_PAIRS |
| strict_0p80_target_0p05_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |
| intermediate_0p70_target_0p10_pooled_offtarget | 0 |  | NA | NA | pooled_off_target_coexpr | NO_PASSING_PAIRS |
| intermediate_0p70_target_0p10_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |
| relaxed_0p60_target_0p10_pooled_offtarget | 34 | S100A14+OCIAD2 | 65.8% | 8.5% | pooled_off_target_coexpr | PASSING_PAIRS_FOUND |
| relaxed_0p60_target_0p10_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |

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
