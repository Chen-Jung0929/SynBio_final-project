# V4 Audit Report: Current Gate Status

Date: 2026-06-04

## Summary

The latest V4 audit no longer supports treating `OCIAD2 + CEACAM5` as a stable final candidate after circularity-sensitive annotation changes. The current unbiased rerun selects:

```text
NMU + CEP55
```

However, this pair has a negative integrated scRNA score and should be interpreted as evidence that V4 still needs optimization, not as a final biosensor design.

## Audit Gate Status

| Gate | Status | Evidence |
|---|---|---|
| scRNA prior has explicit target/off-target fields | PASS | `analysis_v4/v4_scrna_gene_prior.csv` includes compartment flags |
| Candidate-marker circularity audit exists | PASS | `results_v4/audit/v4_circularity_audit.csv` |
| Top-N stability summary exists | PASS | `results_v4/tables/v4_topN_stability_summary.csv` |
| Patient-level prevalence exists | PASS | `results_v4/tables/v4_patient_prevalence_summary.csv`; available |
| Locked GSE28735 validation exists | UNAVAILABLE_PROBE_MAPPING_REQUIRED | `results_v4/audit/v4_gse28735_validation.csv` |
| No simulated validation metrics | PASS | unavailable locked validation is reported as unavailable, not imputed |
| Candidate ready for wet-lab validation | NOT READY | negative scRNA score and unresolved locked validation |

## Current Candidate Metrics

| Metric | Value |
|---|---:|
| Gene A | NMU |
| Gene B | CEP55 |
| Bulk performance score | 0.7374 |
| Discovery sensitivity | 94.94% |
| Discovery specificity | 100.00% |
| GSE62452 sensitivity | 100.00% |
| GSE62452 specificity | 0.00% |
| Tumor Spearman r | 0.511 |
| Target co-expression estimate | 12.28% |
| Max off-target co-expression estimate | 9.68% |
| Max off-target compartment | T cells |
| Integrated scRNA score | -0.3611 |
| Final pair score | -1.1710 |

## Bottom Line

V4 has become a more honest and auditable biological-integration workflow, but the corrected outputs reveal that the current candidate is not yet strong enough for final wet-lab framing. The next work should focus on validated locked mapping, shared scRNA annotation code, and revised scoring/search strategy.
