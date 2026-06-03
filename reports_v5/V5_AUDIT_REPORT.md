# V5 Audit Report

## Core V5 Gates

| Gate | Status | Evidence |
|---|---|---|
| scRNA-first Phase 1 executed | PASS | `results_v5/tables/v5_scrna_candidates.csv` has 34 rows |
| Threshold profile named | PASS | `threshold_profile` column present |
| Patient robustness measured | PASS | `patient_positive_rate` column present |
| Max off-target compartment reported | PASS | `max_off_target_compartment` column present |
| Strict max-compartment off-target gate | FAIL_COMPARTMENT_OFFTARGET_GT_10_PERCENT | Top candidate max off-target = 25.7% |
| Bulk backward validation | UNAVAILABLE_BULK_INPUTS | Missing bulk expression matrix: data/processed/expression_matrix.csv.gz |
| Wet-lab feasibility | PENDING | No promoter/sensor/dynamic-range feasibility review yet |

## Threshold-Profile Summary

| Profile | Passing pairs | Top pair | Target | Off-target | Off-target metric | Status |
|---|---:|---|---:|---:|---|---|
| strict_0p80_target_0p05_pooled_offtarget | 0 |  | NA | NA | pooled_off_target_coexpr | NO_PASSING_PAIRS |
| strict_0p80_target_0p05_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |
| intermediate_0p70_target_0p10_pooled_offtarget | 0 |  | NA | NA | pooled_off_target_coexpr | NO_PASSING_PAIRS |
| intermediate_0p70_target_0p10_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |
| relaxed_0p60_target_0p10_pooled_offtarget | 34 | S100A14+OCIAD2 | 65.8% | 8.5% | pooled_off_target_coexpr | PASSING_PAIRS_FOUND |
| relaxed_0p60_target_0p10_max_compartment_offtarget | 0 |  | NA | NA | max_off_target_coexpr | NO_PASSING_PAIRS |

## Bottom Line

V5 is now producing auditable scRNA-first hypotheses. It has not yet produced a
final candidate suitable for wet-lab framing because compartment-level off-target
activation and missing bulk backward validation remain unresolved.
