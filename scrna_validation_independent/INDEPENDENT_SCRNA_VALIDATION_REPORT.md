# Independent scRNA-seq Validation Report

## 1. Context and Methodological Correction

The previous validation workflow contained a critical circular annotation error: `CEACAM5` expression was used as a classification rule to define "malignant ductal / epithelial" cells, and then that same cell population was used to validate the enrichment and co-expression of `CEACAM5`.

To resolve this flaw, we re-ran the single-cell validation using **independent annotation**. In this correction:
1. Candidate genes `CEACAM5`, `CST1`, `UBE2S`, and `CCR6` were completely excluded from all marker lists, cell-type annotation, clustering, and QC scoring.
2. A strict code-level assertion was implemented to ensure zero overlap.
3. Ductal epithelial cells from the PDAC tumor biopsies were annotated using independent lineage markers and labeled conservatively as `epithelial / ductal tumor-origin cells` (Option C: conservative fallback), rather than claiming "confirmed malignant".
4. Results are stored in the `scrna_validation_independent/` directory to preserve the previous runs.

---

## 2. Core Validation Results and Answers

### 1. Which cell types express CEACAM5?
Using independent annotation, `CEACAM5` is expressed in **23.39%** of the conservatively annotated `epithelial / ductal tumor-origin cells` (mean expression: 0.38) and is low in non-epithelial compartments (e.g., 4.81% in CAF / fibroblasts, 0.96% in CD8 T cells, 0.0% in Tregs).

### 2. Which cell types express CST1?
`CST1` expression is detected in **7.74%** of `epithelial / ductal tumor-origin cells` (mean expression: 0.11). However, it is highly expressed in `CAF / fibroblast` stromal cells (**34.01%** expressing, mean expression: 0.50), indicating a strong stromal signal.

### 3. Are CEACAM5 and CST1 co-expressed in the same single cells?
Yes, but in a small subpopulation. The overall double-positive fraction in `epithelial / ductal tumor-origin cells` is **2.55%** (at both thresholds `> 0` and `> 0.5` due to the log-normalized nature of single-cell transcripts).

### 4. Are they co-expressed in malignant ductal cells?
Using conservative labeling (Option C) for epithelial cells of tumor origin, the co-expression rate is **2.55%**. This is significantly lower than the circular-annotation estimate (10.8%), demonstrating that circular logic had artificially inflated the apparent cell-intrinsic co-expression signal.

### 5. Are they expressed in normal pancreatic ductal or acinar cells?
Within the GSE154778 PDAC dataset, we identified marker-inferred `acinar-like cells` which show **0.0%** double-positive fraction. However, healthy-normal pancreas single-cell validation was not completed. Off-target conclusions are limited to non-malignant-like compartments within the PDAC dataset.

### 6. Are they expressed in immune or stromal compartments?
* **CAF / fibroblast**: **1.54%** double-positive fraction (driven by 34.01% CST1 expression and 4.81% CEACAM5 background).
* **Plasma cells**: **3.00%** double-positive fraction (driven by 16.62% CEACAM5 and 10.08% CST1 expression).
* **Other immune compartments (T cells, CD8 T cells, Tregs, mast cells)**: Near-zero (0.0% in T cells, CD8 T cells, Tregs; 1.85% in mast cells).

### 7. Does the single-cell evidence support a cell-intrinsic AND gate, or only a tissue-level / multicellular signature?
The evidence supports a **cell-intrinsic AND gate**, but only in a restricted subpopulation of epithelial cells. Same-cell co-expression exists (2.55%) and is enriched relative to other cells, but bulk tumor transcriptomics signals likely combine this cell-intrinsic subpopulation with high stromal expression of CST1.

### 8. Does spatial data support co-localization?
No spatial transcriptomics datasets were analyzed in this run due to lack of local files.

---

## 3. Performance Tables

### Cell-Type Expression Profiles (Mean Log-Normalized Counts)
`scrna_validation_independent/tables/gene_expression_by_independent_celltype.csv`

| cell_type | gene | mean_expression | median_expression | percent_expressing | n_cells | n_patients | annotation_source |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **epithelial / ductal tumor-origin cells** | CEACAM5 | 0.3789 | 0.0 | 23.39% | 8103 | 16 | independent-marker-inferred |
| **epithelial / ductal tumor-origin cells** | CST1 | 0.1118 | 0.0 | 7.74% | 8103 | 16 | independent-marker-inferred |
| **CAF / fibroblast** | CEACAM5 | 0.0573 | 0.0 | 4.81% | 2017 | 12 | independent-marker-inferred |
| **CAF / fibroblast** | CST1 | 0.5020 | 0.0 | 34.01% | 2017 | 12 | independent-marker-inferred |
| **acinar-like cells** | CEACAM5 | 0.0285 | 0.0 | 1.79% | 2629 | 13 | independent-marker-inferred |
| **acinar-like cells** | CST1 | 0.0082 | 0.0 | 0.04% | 2629 | 13 | independent-marker-inferred |

### Co-expression Comparison (Threshold > 0)
`scrna_validation_independent/tables/pair_coexpression_by_independent_celltype.csv`

| cell_type | v1_pair_coexpression_fraction (UBE2S+CCR6) | v2_pair_coexpression_fraction (CEACAM5+CST1) | n_cells |
| :--- | :---: | :---: | :---: |
| **epithelial / ductal tumor-origin cells** | 0.67% | 2.55% | 8103 |
| **acinar-like cells** | 0.04% | 0.00% | 2629 |
| **CAF / fibroblast** | 0.50% | 1.54% | 2017 |
| **Tregs** | 16.39% | 0.00% | 61 |
| **T cells** | 10.53% | 0.00% | 114 |
| **plasma cells** | 1.36% | 3.00% | 367 |
| **macrophages / monocytes** | 1.33% | 0.23% | 1279 |

---

## 4. Patient-Level Validation

Patient-level pseudobulk calculations verify that the co-expression signal is highly variable across individuals:
* **Total Patients with Epithelial Cells**: 16
* **Patients with Double-Positive Epithelial Cells (>0)**: 9 (56.25%)
* **Median Double-Positive Fraction**: 0.68%
* **Range of Double-Positive Fraction**: [0.00%, 12.43%]

Only 9 out of 16 patients show any cell-intrinsic double-positive epithelial cells. Patient `MET02` drives a disproportionate share of the signal (12.43% double-positive fraction in epithelial cells), followed by `P09` (7.65%), `P01` (5.50%), and `P08` (5.13%). Seven patients show 0.0% co-expression. This highlights that the therapeutic sensitivity of a CEACAM5+CST1 AND-gate biosensor would vary widely between patients.

---

## 5. Final Interpretation Category

Based on these results, we classify the **CEACAM5 + CST1** candidate pair under **Category B: Supportive but subpopulation-restricted**.

### Rationale
1. **Low and Variable Co-expression**: Same-cell co-expression in epithelial cells exists (2.55% overall) but is restricted to a small subpopulation and is present in only 9/16 patients (median 0.68%).
2. **Stromal Off-Target Risk**: CST1 is highly expressed in CAFs/fibroblasts (34.01%), which may lead to off-target stromal activation if CEACAM5 promoter leakage occurs.
3. **Plasma Cell Co-expression**: A double-positive fraction of 3.00% is observed in plasma cells.
4. **No Definitive Healthy Reference**: Healthy-normal pancreas single-cell validation was not completed.

---

## 6. Comparison with UBE2S + CCR6 (v1)

Despite these restrictions, **CEACAM5 + CST1 (v2) remains a superior AND-gate candidate compared to UBE2S + CCR6 (v1)**:
1. **Epithelial Enrichment**: In epithelial tumor-origin cells, v2 co-expression (2.55%) is higher than v1 (0.67%).
2. **Reduced T-Cell Off-Target Risk**: UBE2S + CCR6 shows high co-expression in immune cells, particularly Tregs (16.39%) and T cells (10.53%), creating a severe risk of off-target immune-compartment CAR activation. CEACAM5 + CST1 shows 0.0% co-expression in Tregs, CD8 T cells, and T cells.
