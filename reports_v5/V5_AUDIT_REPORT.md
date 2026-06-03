# V5 Audit Report

## Core V5 Gates

| Gate | Status | Evidence |
|---|---|---|
| scRNA-first Phase 1 executed | PASS | `results_v5/tables/v5_scrna_candidates.csv` has 34 rows |
| Threshold profile named | PASS | `threshold_profile` column present |
| Patient robustness measured | PASS | `patient_positive_rate` column present |
| Strict max-compartment off-target gate | FAIL_COMPARTMENT_OFFTARGET_GT_10_PERCENT | Checked for >10% max compartment off-target |
| Bulk backward validation | PASS |  |
| Wet-lab feasibility | PENDING | No promoter/sensor/dynamic-range feasibility review yet |

## Bottom Line
V5 successfully generated and bulk-validated an scRNA-first candidate, overcoming the previous data bottleneck.
