# Codex V4 Review Handoff

Date: 2026-06-04  
Branch context: `codex/v3-ai-scientist-review` plus Antigravity V4 draft files

## Current Situation

Antigravity has started a V4 pipeline under:

```text
analysis_v4/
```

Current draft scripts detected by Codex:

```text
analysis_v4/01_extract_scrna_prior.py
analysis_v4/pair_search_v4.py
analysis_v4/pipeline_v4.py
```

Codex intentionally did not edit those scripts in this pass to avoid concurrent
pipeline conflicts.

## Codex Contribution in This Pass

Codex added:

```text
reports_v4/V4_SCIENTIFIC_NARRATIVE_AND_COMPLETION_GATES.md
```

This document defines:

- why V4 is needed after the v3 `PKM + ADAM22` compartment failure;
- the updated scientific narrative for the final project;
- required V4 result tables and columns;
- completion gates for the course project;
- limitations that must stay visible in the final report.

## Local Execution Status

V4 could not be executed in this local Codex worktree because these data-derived
files are absent:

```text
data/processed/expression_matrix.csv.gz
scrna_validation_independent/data/processed/pdac_processed.h5ad
```

The V4 scripts pass Python syntax compilation, but their runtime behavior still
needs verification in the environment where those data files exist.

## Suggested Division of Labor

Antigravity:

- continue implementing and running `analysis_v4/`;
- generate `results_v4/tables/` and `results_v4/audit/`;
- push the V4 execution branch when first outputs exist.

Codex:

- review V4 outputs against the completion gates;
- generate `reports_v4/V4_AUDIT_REPORT.md`;
- update README and final project narrative after V4 results are real;
- keep claim discipline: computational prioritization, not clinical or wet-lab
  validation.

## Immediate Next Check After V4 Runs

Once V4 produces tables, inspect:

```text
results_v4/tables/v4_default_final_pair.csv
results_v4/tables/topN_pair_stability_summary.csv
results_v4/tables/pair_search_ensemble_threshold_top100.csv
analysis_v4/v4_scrna_gene_prior.csv
```

The first scientific question is:

```text
Did V4 improve target-compartment co-expression without introducing unacceptable
immune, endocrine, acinar, or endothelial off-target co-expression?
```
