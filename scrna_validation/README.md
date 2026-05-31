# Single-Cell & Spatial Validation (Archived Circular Annotation Version)

> [!WARNING]
> This folder contains the **archived circular annotation version** of the single-cell validation. 
> It contains a methodological flaw where candidate genes were used during cell-type classification.
> For the corrected, independent validation, please refer to the [scrna_validation_independent](file:///Users/Janet/Documents/Antigravity/SynBio%20final/scrna_validation_independent) directory.

This directory contains the pipeline and results for the real single-cell RNA-seq validation of the PDAC AND-gate biosensor candidate pairs using circular classification rules.

## Folders
* **`data/`**: Raw and processed single-cell transcriptomic matrices.
* **`scripts/`**: Sequential validation execution scripts.
* **`tables/`**: Computed cell-type and patient-level verification tables.
* **`figures/`**: Single-cell diagnostic and cell-type expression visualizations.

## Key Verification Results
* **Dataset Used**: GSE154778 (Lin et al. 2020)
* **Statistics**: 14,924 cells, 22,217 genes across 16 patients (10 primary, 6 metastases).
* **CEACAM5 + CST1 (v2)**: Supported by **Category A (Strong cell-intrinsic support)**. Co-expression is highly specific to the malignant ductal compartment (10.8%), with absolute safety in healthy normal pancreatic cells (0.0% in normal ductal and acinar cells).
* **UBE2S + CCR6 (v1)**: Rejected as cell-intrinsic. Co-expression in cancer cells is near-zero (0.9%), and it exhibits a high risk of off-target activation in regulatory T cells (16.2% in Tregs).
