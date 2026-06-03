# SynBio Final Project: PDAC Logic-Gated Biosensor Discovery

## Current Branch Focus

This branch tracks the transition from the third-generation (`v3`) unbiased
pipeline into a fourth-generation (`v4`) biologically integrated search for
candidate two-input synthetic-biology AND-gate biosensor signals for pancreatic
ductal adenocarcinoma (PDAC).

The current default v3 pair was:

```text
PKM AND ADAM22
```

The current draft v4 pair is:

```text
OCIAD2 AND CEACAM5
```

V4 is now the active scientific direction because it integrates single-cell
target-compartment co-expression into pair selection. The V4 result is promising
but still under audit; it is not yet a completed or experimentally validated
biosensor.

Key locked external validation result:

| Dataset | Role | Result |
|---|---|---|
| TCGA + GTEx | Discovery | used for differential expression, model training, threshold estimation |
| GSE62452 | same-cohort validation filter | used during candidate filtering and pair scoring |
| GSE28735 | locked external validation | evaluated once after final pair freeze |

GSE28735 locked validation for `PKM + ADAM22`:

| Metric | Value |
|---|---:|
| ROC-AUC | 0.8588 |
| Sensitivity | 80.0% |
| Specificity | 82.2% |
| Tumor samples | 45 |
| Normal samples | 45 |

Approximate 95% intervals are now reported in
`results_v3/tables/locked_gse28735_uncertainty_intervals.csv`. These intervals
use aggregate locked-validation outputs. Future runs should export sample-level
gate scores for bootstrap or DeLong intervals.

## What Changed in v3

- Replaced the earlier single-pair narrative with an unbiased three-model
  ensemble workflow.
- Uses SAGA Elastic Net Logistic Regression, Random Forest, and XGBoost for
  model-consensus feature prioritization.
- Estimates per-gene activation thresholds from model-derived attribution
  behavior, then audits threshold instability.
- Searches all gene pairs across top 20, 50, 100, and 200 consensus-gene
  spaces.
- Keeps GSE28735 as a true locked external validation cohort, evaluated only
  after the default pair is frozen.
- Adds row-count, access-sequence, GSE28735 parsing, top-N stability, and
  scRNA marker-overlap audits.
- Adds corrected single-cell validation notes that distinguish preliminary
  marker-score validation from full unbiased scRNA annotation.

## Important Interpretation

The v3 result is stronger than v2 in audit discipline, but it is not yet a
biologically validated biosensor.

- `PKM + ADAM22` is stable only in the larger top100/top200 search spaces.
  The top20/top50 searches select `OCIAD2 + EDIL3`, so candidate choice remains
  sensitive to the initial gene pool.
- The top-20 pair overlap across search spaces is low, showing that pair-ranking
  robustness still needs improvement.
- Bulk-level locked validation is moderate, not near-perfect.
- scRNA validation is preliminary. It suggests low immune/Treg co-expression,
  but the putative malignant ductal epithelial double-positive rate is very low
  and patient-variable.
- The current claim should be: computationally prioritized candidate pair,
  not clinically deployable detector or experimentally validated circuit.

The v4 draft improves the biological alignment by selecting `OCIAD2 + CEACAM5`,
which has high malignant ductal / epithelial co-expression in the current scRNA
prior. However, V4 still needs top-N stability, locked GSE28735 validation,
patient-level target prevalence, circularity audit, uncertainty intervals, and
wet-lab feasibility review.

## Main Files

| Path | Purpose |
|---|---|
| `analysis_v3/pipeline_v3.py` | End-to-end v3 discovery, pair search, validation, audit generation |
| `analysis_v3/threshold_estimation_v3.py` | Three-model threshold estimation and instability audit |
| `analysis_v3/pair_search_v3.py` | Pair scoring across candidate-gene spaces |
| `analysis_v3/validation_v3.py` | Preliminary scRNA validation with marker-overlap audit |
| `analysis_v3/audit_v3_outputs.py` | Integrity, row-count, true-lock, and anti-bias audit checks |
| `analysis_v4/` | draft V4 scRNA-integrated candidate search scripts |
| `reports_v3/` | v3 methods, results, limitations, final report, and AI review |
| `reports_v4/` | V4 scientific narrative, audit, and collaboration handoff |
| `results_v3/tables/` | generated v3 tables |
| `results_v3/audit/` | generated v3 audit tables |
| `results_v4/tables/` | draft V4 pair-search outputs |
| `scrna_validation/` | v3 preliminary scRNA outputs plus archived circular-validation warning |
| `scrna_validation_independent/` | independent-validation archive for earlier candidate pairs |

## Reproduce and Audit

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the v3 pipeline:

```powershell
python analysis_v3\pipeline_v3.py
```

Regenerate v3 reports from generated tables:

```powershell
python analysis_v3\generate_reports_v3.py
```

Run the v3 output audit:

```powershell
python analysis_v3\audit_v3_outputs.py
```

The latest audit passed all implemented checks:

```text
All integrity, row-count, consistency, true-lock, and anti-bias checks passed.
```

## Data Governance

This repository stores public/cohort-level outputs and pseudonymous sample
identifiers from public datasets. Raw data folders are ignored by Git. The
patient-level IDs in generated scRNA tables are public dataset pseudonyms such
as `P01` or `MET01`, not direct identifiers, but they should still be treated as
research sample codes rather than clinical identifiers.

## Current Priority

See:

- `reports_v4/V4_AUDIT_REPORT.md`
- `reports_v4/V4_SCIENTIFIC_NARRATIVE_AND_COMPLETION_GATES.md`
- `reports_v3/AI_COSCIENTIST_REVIEW_2026-06-04.md`
- `reports_v3/V3_LIMITATIONS.md`
- `reports_v3/V3_AUDIT_REPORT.md`

The immediate next step is not more cosmetic reporting. It is V4 hardening:
finish top-N stability sweeps, recompute locked GSE28735 validation for
`OCIAD2 + CEACAM5`, add patient-level target prevalence and circularity audit,
then define the wet-lab feasibility path for sensing or implementing the two
inputs.
