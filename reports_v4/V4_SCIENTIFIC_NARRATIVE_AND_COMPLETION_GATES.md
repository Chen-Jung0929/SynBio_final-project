# V4 Scientific Narrative and Completion Gates

Prepared by Codex with AI Co-Scientist support  
Date: 2026-06-04

## Why V4 Is Needed

The v3 pipeline improved statistical discipline, but it also exposed a central
synthetic-biology problem: a bulk-transcriptomic pair can classify tumor samples
while still failing as a cell-level AND-gate input pair.

The v3 default pair, `PKM + ADAM22`, has a true locked GSE28735 external
validation audit, but single-cell validation shows very low co-expression in the
putative malignant ductal epithelial compartment. For a real logic-gated
biosensor, the crucial question is not only:

```text
Can this pair classify bulk tumor vs normal samples?
```

It is:

```text
Are both inputs co-expressed in the intended target cell compartment,
while remaining low in off-target compartments?
```

V4 should therefore integrate single-cell compartment evidence directly into the
pair-selection objective instead of using scRNA-seq only after the final pair has
already been chosen.

## Updated Scientific Narrative

The project should now be narrated as a staged computational design process:

1. V1 showed that a visually impressive bulk classifier can be misleading if
   cohort effects and biological implementation constraints are not handled.
2. V2 improved biological plausibility and single-cell support for earlier
   epithelial-marker-like candidates, but still required stronger unbiased
   selection and audit discipline.
3. V3 added unbiased ensemble prioritization, threshold-instability auditing,
   top-N search-space sweeps, and locked external validation. It selected
   `PKM + ADAM22`, but revealed that bulk performance alone is insufficient for
   a cell-level biosensor.
4. V4 is the biological integration stage: pair scoring must jointly optimize
   bulk discriminative performance, target-compartment co-expression, low
   off-target co-expression, low redundancy, and stable thresholds.

The strongest final claim should be:

```text
We built and audited a computational workflow for prioritizing candidate
two-input PDAC biosensor signals.
```

The final claim should not be:

```text
We validated a clinically deployable PDAC detector or experimentally working
synthetic circuit.
```

## V4 Pair-Selection Objective

V4 should keep the score interpretable. A transparent scoring model is preferred:

```text
V4 pair score =
  bulk performance score
+ target-compartment co-expression reward
- off-target co-expression penalty
- low-patient-prevalence penalty
- correlation / redundancy penalty
- threshold-instability penalty
```

Each term should be stored as a separate table column. This is more important
than squeezing the score into a single polished number.

## Required V4 Evidence

The V4 branch is not complete until it produces all of the following evidence.

### 1. scRNA Prior Table

Required path:

```text
analysis_v4/v4_scrna_gene_prior.csv
```

Required columns:

| Column | Purpose |
|---|---|
| `gene` | candidate gene |
| `cell_type` | cell compartment label |
| `mean_expression` | compartment-level mean expression |
| `percent_expressing_fraction` | fraction of cells with expression > 0 |
| `n_cells` | denominator for that compartment |
| `is_target_compartment` | whether this compartment is intended target biology |
| `is_off_target_compartment` | whether this compartment is penalized |
| `source_h5ad` | processed AnnData source |
| `annotation_version` | marker/annotation version used |

### 2. Pair-Search Tables

Required paths:

```text
results_v4/tables/pair_search_ensemble_threshold_top20.csv
results_v4/tables/pair_search_ensemble_threshold_top50.csv
results_v4/tables/pair_search_ensemble_threshold_top100.csv
results_v4/tables/pair_search_ensemble_threshold_top200.csv
```

Required columns:

| Column | Purpose |
|---|---|
| `gene_A`, `gene_B` | evaluated pair |
| `performance_score` | bulk discovery/GSE62452 performance term |
| `target_coexpr_est` | estimated target-compartment co-expression |
| `max_off_target_coexpr_est` | worst off-target co-expression |
| `scrna_score` | single-cell reward minus penalty |
| `tumor_spearman_r` | redundancy check |
| `mean_threshold_instability` | K stability check |
| `pair_score` | final transparent composite |

### 3. Search-Space Stability Summary

Required path:

```text
results_v4/tables/topN_pair_stability_summary.csv
```

This table must show whether the final V4 candidate is stable across top20,
top50, top100, and top200 candidate spaces. If the top pair changes, the report
must state that clearly.

### 4. Final Pair Table

Required path:

```text
results_v4/tables/v4_default_final_pair.csv
```

The default V4 pair should come from the predeclared top100 search space unless
the report explicitly justifies a different default.

### 5. V4 Audit Report

Required path:

```text
reports_v4/V4_AUDIT_REPORT.md
```

The audit must answer:

1. Was the scRNA prior generated before pair ranking?
2. Were candidate genes excluded from annotation markers or otherwise audited for
   circularity?
3. Were target and off-target compartments explicitly defined before ranking?
4. Were all top-N pair-search row counts complete?
5. Did the final pair remain stable across search spaces?
6. Did V4 preserve or improve locked external validation relative to V3?
7. Did V4 improve target-compartment co-expression relative to `PKM + ADAM22`?
8. Does any off-target compartment show unacceptable leakage?

## Completion Gates for the Course Project

The project is ready for final course presentation only when these gates are met:

| Gate | Required state |
|---|---|
| Scientific claim | bounded to computational prioritization |
| Bulk validation | discovery, GSE62452, and locked GSE28735 clearly separated |
| Cell-level support | target and off-target compartment evidence reported |
| Reproducibility | runnable scripts and generated result tables committed |
| Auditability | row counts, data-source usage, and circularity checks documented |
| Limitations | no clinical utility, causality, or wet-lab validation overclaim |
| Next-step design | wet-lab feasibility path and failure modes listed |

## Current Blocking Facts

In this Codex worktree, the raw data needed to execute V4 are not present:

```text
data/processed/expression_matrix.csv.gz
scrna_validation_independent/data/processed/pdac_processed.h5ad
```

Therefore, this branch can currently define V4's review and report contract, but
cannot independently verify V4 execution until Antigravity or another compute
environment supplies the required data-derived outputs.

## Recommended Final Project Framing

Use this framing in the final report and slides:

```text
The project evolved from bulk biomarker discovery into a biosensor-oriented
multi-level validation framework. V4 explicitly treats single-cell compartment
co-expression as a design requirement, because a synthetic AND gate must work in
cells, not only in bulk cohort statistics.
```

This framing is scientifically stronger than presenting any single pair as
already validated.
