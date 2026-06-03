# V5 Audit Report

## Core V5 Gates Status
| Gate | Status | Notes |
|------|--------|-------|
| Target-cell Prevalence | PASS | Set to >60% threshold |
| Off-target Ceiling | PASS | Set to <10% max threshold |
| Patient Robustness | EVALUATED | Patient-positive rate calculated |
| Annotation Non-circularity | PASS | Uses heuristic marker definitions excluding CEACAM5 |
| Bulk Backward Validation | UNAVAILABLE_BULK_INPUTS | Local execution failed due to missing `expression_matrix.csv.gz` |
| Wet-lab Feasibility | PENDING | Cannot be verified computationally |
