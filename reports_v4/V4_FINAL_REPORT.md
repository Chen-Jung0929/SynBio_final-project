# V4 Final Report: Unbiased Biological Integration Audit

## 1. Overview

V4 was introduced because the V3 pair (`PKM` + `ADAM22`) performed better in bulk validation than earlier candidates but failed the cell-level design requirement: the two inputs were not consistently co-expressed in the malignant ductal / epithelial compartment.

The latest V4 audit removes candidate-like ductal markers from the scRNA annotation step, adds explicit target/off-target compartment flags, and reranks the V3 top-200 pair search using the same transparent score components.

## 2. Current V4 Candidate

* **Gene A**: `NMU`
* **Gene B**: `CEP55`
* **Bulk performance score**: 0.7374
* **Discovery sensitivity / specificity**: 94.94% / 100.00%
* **GSE62452 sensitivity / specificity**: 100.00% / 0.00%
* **Tumor Spearman r**: 0.511 (moderate correlation)
* **Target-compartment co-expression estimate**: 12.28%
* **Max off-target co-expression estimate**: 9.68% (T cells)
* **Integrated scRNA score**: -0.3611
* **Final pair score**: -1.1710

## 3. Interpretation

The current unbiased rerun selects `NMU + CEP55`, but the result should be treated as an audit finding rather than a completed biosensor candidate. The integrated scRNA score is negative because off-target co-expression remains substantial relative to target-compartment co-expression. This indicates that removing circular annotation pressure changed the V4 landscape and exposed a remaining biological-specificity problem.

The current candidate is therefore useful for diagnosing the next optimization problem: V4 needs either a better target-cell annotation strategy, a revised off-target penalty calibration, or an expanded search space before selecting a final wet-lab hypothesis.

## 4. Completed Checks

* **Circularity audit**: PASS. Candidate genes were checked against the ductal marker list used for annotation.
* **Top-N stability summary**: PASS. See `results_v4/tables/v4_topN_stability_summary.csv`.
* **Patient-level prevalence**: 8.33% patient-positive rate; status: available.
* **Locked GSE28735 audit**: UNAVAILABLE_PROBE_MAPPING_REQUIRED. Exact ID_REF gene-symbol match failed; no simulated validation metrics were emitted.

## 5. Current Limitations

* The single-cell annotation is still heuristic and metadata-derived; it is not a curated malignant-cell label.
* The patient prevalence script and scRNA prior must use exactly the same target-compartment definition before prevalence can be interpreted strongly.
* The GSE28735 locked validation remains unavailable until a verified probe-to-gene mapping is added. No simulated locked-validation metrics should be used.
* The current pair does not yet show strong target specificity after the circularity correction.
* This remains a computational prioritization workflow, not a validated synthetic biology circuit.

## 6. Next Required Work

1. Add a verified GSE28735 probe-to-symbol mapping and recompute locked validation without fallback simulation.
2. Harmonize the scRNA prior and patient-prevalence annotation functions into one shared helper.
3. Revisit the V4 scoring weights because the current strict off-target penalty drives all top scores negative.
4. Expand or stratify the candidate search beyond the V3 top-200 list if no pair has positive target-minus-off-target support.
5. Add wet-lab feasibility filters for input sensing modality, dynamic range, essential-gene risk, and circuit implementability.
