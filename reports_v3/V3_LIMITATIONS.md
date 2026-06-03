# V3 Limitations: Technical Caveats and Clinical Exclusions

This document lists the technical limitations and caveats of the third-generation (v3) discovery and validation workflow.

## 1. Confounding and Batch Boundaries
* **Source Confounding**: The discovery cohort combines TCGA primary tumor tissue with GTEx healthy donor pancreas tissue. Although Welch's t-test and Wilcoxon tests are highly robust, residual batch effects due to sequencing platforms, sample processing, and RNA isolation pipelines can still exist.
* **Early Validation Filtering**: We mitigate this by requiring candidate genes to pass validation thresholds in a same-cohort microarray dataset (GSE62452), filtering out batch-specific artifacts early in the pipeline.

## 2. In Silico AND-Gate Kinetic Simulating
* **Hill Equation Kinetics**: The AND-gate logic is simulated using a mathematical dual-input Hill equation. This assumes standard cooperative binding behavior, which may not represent the complex biochemical kinetics of synthetic promoters or ribocomputing devices in vivo.
* **SHAP Threshold Translation**: Dynamic thresholds ($K_A, K_B$) are inferred statistically from classifier SHAP attribution inflection points. These are mathematical decision boundaries, not biochemical affinity dissociation constants ($K_d$).

## 3. scRNA-seq Lineage Annotation
* **Preliminary Marker-Score Validation**: Due to missing dependencies in this environment, single-cell analysis is a preliminary marker-score-based targeted validation rather than a full unbiased scRNA-seq annotation workflow.
* **Ductal Compartment Labeling**: In the absence of R-based inferCNV or copyKAT runs, we labeled the ductal compartment conservatively as `tumor-associated epithelial / putative malignant ductal epithelial` cells. While this avoids circular reasoning, it cannot definitively separate normal ductal contamination from malignant tumor cells within the biopsy.
* **Islet Off-Target Expression**: While the double-positive rate is near-zero in endocrine islets, low-level leakage remains a risk that requires promoter tuning.

## 4. Spatial Transcriptomics Coordinates
* **Lack of Spatial Data**: Visium spatial coordinate files were not accessed due to file size constraints in this environment. Tissue-level colocalization remains illustrative.
