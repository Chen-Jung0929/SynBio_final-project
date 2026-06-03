# V4 Audit Report: Biologically Integrated Pair Search

Date: 2026-06-04

## Summary

V4 successfully addresses the main v3 failure mode by selecting a pair with much
stronger target-compartment co-expression. The current V4 default pair is:

```text
OCIAD2 + CEACAM5
```

This pair is a stronger computational biosensor candidate than `PKM + ADAM22`
from the standpoint of malignant ductal / epithelial co-expression. However, V4
is not yet a complete final-project endpoint. Several audit gates remain open:
top-N stability is not reported, locked GSE28735 validation is not recomputed for
the V4 pair, and off-target co-expression is still measurable.

## Current Evidence

### Default V4 Pair

Source:

```text
results_v4/tables/v4_default_final_pair.csv
```

| Metric | Value |
|---|---:|
| Gene A | OCIAD2 |
| Gene B | CEACAM5 |
| Bulk performance score | 0.8487 |
| Discovery sensitivity | 94.38% |
| Discovery specificity | 100.00% |
| GSE62452 sensitivity | 81.16% |
| GSE62452 specificity | 63.93% |
| Tumor Spearman r | 0.523 |
| Redundancy category | moderate correlation |
| Target co-expression estimate | 92.12% |
| Max off-target co-expression estimate | 14.71% |
| Integrated scRNA score | 0.1859 |

## Single-Cell Compartment Check

For `OCIAD2 + CEACAM5`, the estimated pair co-expression by compartment is:

| Cell type | Pair co-expression estimate |
|---|---:|
| malignant ductal / epithelial | 92.12% |
| mast cells | 14.71% |
| B cells | 14.29% |
| CD8 T cells | 14.29% |
| Tregs | 11.11% |
| endothelial | 7.89% |
| CAF / fibroblast | 7.77% |
| macrophages / monocytes | 6.68% |
| T cells | 5.88% |
| normal acinar | 4.26% |
| normal ductal | 0.00% |

Interpretation:

- The malignant ductal / epithelial co-expression signal is strong.
- The pair is not perfectly tumor-specific; mast cells, B cells, CD8 T cells,
  and Tregs show measurable estimated co-expression.
- Normal ductal co-expression is estimated at 0.00% because CEACAM5 is absent in
  the current normal ductal summary even though OCIAD2 is highly prevalent there.

## Audit Gate Status

| Gate | Status | Evidence |
|---|---|---|
| V4 pair-search table exists | PASS | `results_v4/tables/v4_pair_search_results.csv` has 19,900 rows |
| Default V4 pair table exists | PASS | `results_v4/tables/v4_default_final_pair.csv` |
| scRNA prior exists | PASS | `analysis_v4/v4_scrna_gene_prior.csv` has 2,200 rows |
| V4 target-compartment reward is included | PASS | `target_coexpr_est` column present |
| V4 off-target penalty is included | PASS | `max_off_target_coexpr_est` and `scrna_score` columns present |
| Component scores are visible | PASS | bulk, redundancy, instability, target, off-target, and final score columns present |
| Top-N stability sweep exists | MISSING | no `results_v4/tables/topN_pair_stability_summary.csv` yet |
| Locked GSE28735 validation exists for V4 pair | MISSING | no V4 locked validation table yet |
| Patient-level target prevalence exists | MISSING | no V4 patient-level table yet |
| Circularity / annotation audit exists | MISSING | no V4 marker-overlap audit yet |
| Sample-level calibration or CI exists | MISSING | no V4 uncertainty table yet |

## Scientific Claim Discipline

Supported current claim:

```text
V4 identifies OCIAD2 + CEACAM5 as a computational candidate with strong
malignant ductal / epithelial co-expression and a transparent scRNA-integrated
pair score.
```

Unsupported current claims:

```text
The pair is fully tumor-specific.
The pair is clinically validated.
The pair is ready as a working synthetic circuit.
The biological alignment issue is completely resolved.
```

## Required Next Steps

1. Recompute or extend V4 to produce top20/top50/top100/top200 stability tables.
2. Evaluate the V4 pair on locked GSE28735 using the same true-lock discipline as
   v3.
3. Add patient-level prevalence for the target compartment.
4. Add a V4 circularity audit confirming candidate genes were not used to define
   the malignant ductal / epithelial label.
5. Report the maximum off-target compartment explicitly in machine-readable form.
6. Add uncertainty intervals for V4 bulk and locked-validation metrics.
7. Review wet-lab feasibility: promoter/sensor availability, dynamic range,
   input independence, essential-gene risks, and implementation modality.

## Bottom Line

V4 is a real scientific improvement over v3 because it moves the project from
bulk-only prioritization toward cell-compartment-aware biosensor design. It is
not yet the final endpoint. The current best use of V4 is as the new leading
candidate-generation framework, pending locked external validation, stability
audits, and wet-lab feasibility review.
