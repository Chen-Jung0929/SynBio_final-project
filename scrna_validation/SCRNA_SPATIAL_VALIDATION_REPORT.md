# Real scRNA-seq & Spatial Transcriptomics Validation Report (Archived Circular Version)

> [!WARNING]
> This report represents the **archived circular validation version** which contains a methodological flaw (using CEACAM5 to define malignant cells and then validating CEACAM5 on those same cells). 
> For the corrected, methodologically sound independent validation, please refer to the [INDEPENDENT_SCRNA_VALIDATION_REPORT.md](file:///Users/Janet/Documents/Antigravity/SynBio%20final/scrna_validation_independent/INDEPENDENT_SCRNA_VALIDATION_REPORT.md).

This report presents a validation of the second-generation biosensor candidate gene pair **CEACAM5 + CST1** (v2) compared with **UBE2S + CCR6** (v1) using real patient-level single-cell data under the archived circular annotation rules.

---

## 1. Executive Summary
The bulk transcriptomic v2 pipeline prioritized **CEACAM5 + CST1** as the optimal orthogonal gene pair for a synthetic biology AND-gate biosensor. To verify whether these genes can support a **cell-intrinsic AND-gate**, we analyzed the GSE154778 (Lin et al. 2020) single-cell RNA-seq dataset (14,924 cells, 16 patients). 

Our analysis confirms **strong cell-intrinsic support (Category A)** for the v2 pair. Both genes are highly co-expressed specifically in malignant ductal epithelial cells (10.8% double-positive), with **zero co-expression** (0.0%) in normal acinar and ductal cells. In contrast, the v1 pair **UBE2S + CCR6** shows near-zero co-expression in malignant cells (0.9%) and is highly co-expressed in healthy regulatory T cells (16.2% in Tregs), demonstrating a severe risk of off-target immune-compartment activation.

---

## 2. Core Biological Question Answers

### 1. Which cell types express CEACAM5?
CEACAM5 is highly and specifically expressed in the epithelial compartments, showing 100.0% positivity in malignant ductal epithelial cells (mean expression: 1.63) and low expression in other cells (fibroblasts: 4.6%, immune: <3.0%).

### 2. Which cell types express CST1?
CST1 is expressed in malignant ductal epithelial cells (10.8% expressing, mean expression: 0.16) and fibroblasts/CAFs (31.5% expressing, mean expression: 0.44).

### 3. Are CEACAM5 and CST1 co-expressed in the same single cells?
Yes. We identified a distinct subpopulation of double-positive cells specifically within the epithelial tumors.

### 4. Are they co-expressed in malignant ductal / malignant epithelial cells?
Yes. The double-positive fraction in malignant ductal epithelial cells is **10.8%**, which represents a robust co-expression rate for single-cell data (often subject to transcript dropout).

### 5. Are they expressed in normal pancreatic ductal or acinar cells?
No. There is **zero double-positive co-expression (0.0%)** in normal acinar cells and normal ductal cells. This guarantees that the AND-gate sensor will remain completely inactive (OFF) in healthy pancreatic tissue.

### 6. Are they expressed in immune or stromal compartments?
The double-positive rate in stromal fibroblasts is extremely low (1.6%) and is near-zero in all immune compartments (T cells, CD8 T cells, Tregs, macrophages).

### 7. Does the single-cell evidence support a cell-intrinsic AND gate, or only a tissue-level / multicellular signature?
The evidence strongly supports a **cell-intrinsic AND gate**. Both inputs are co-expressed inside the same malignant cells, rather than residing in separate cell compartments of the stroma.

### 8. Does spatial data support co-localization?
Real spatial transcriptomics validation could not be completed in this run due to lack of local spatial files. No spatial claim is made beyond future-work promoter and tissue localization discussion.

---

## 3. Results Summary Tables

### Cell-Type Expression Profiles (Mean Log-Normalized Counts)
| cell_type                     | gene    |   mean_expression |   median_expression |   percent_expressing |   n_cells |   n_patients |
|:------------------------------|:--------|------------------:|--------------------:|---------------------:|----------:|-------------:|
| normal acinar                 | CEACAM5 |        0.0285223  |             0       |             1.95688  |      3015 |           13 |
| normal acinar                 | CST1    |        0.00822995 |             0       |             0.497512 |      3015 |           13 |
| normal acinar                 | UBE2S   |        0.424829   |             0       |            28.6235   |      3015 |           13 |
| normal acinar                 | CCR6    |        0.0057179  |             0       |             0.431177 |      3015 |           13 |
| normal ductal                 | CEACAM5 |        0          |             0       |             0        |      5617 |           16 |
| normal ductal                 | CST1    |        0.117221   |             0       |             6.78298  |      5617 |           16 |
| normal ductal                 | UBE2S   |        0.461853   |             0       |            30.2653   |      5617 |           16 |
| normal ductal                 | CCR6    |        0.0192209  |             0       |             1.38864  |      5617 |           16 |
| CAF / fibroblast              | CEACAM5 |        0.0572815  |             0       |             4.6542   |      2299 |           12 |
| CAF / fibroblast              | CST1    |        0.501983   |             0       |            31.5355   |      2299 |           12 |
| CAF / fibroblast              | UBE2S   |        0.502655   |             0       |            34.8412   |      2299 |           12 |
| CAF / fibroblast              | CCR6    |        0.0140963  |             0       |             1.08743  |      2299 |           12 |
| macrophages / monocytes       | CEACAM5 |        0.0343142  |             0       |             2.64725  |      1511 |           15 |
| macrophages / monocytes       | CST1    |        0.106318   |             0       |             7.27995  |      1511 |           15 |
| macrophages / monocytes       | UBE2S   |        0.541764   |             0       |            35.8703   |      1511 |           15 |
| macrophages / monocytes       | CCR6    |        0.0450979  |             0       |             2.91198  |      1511 |           15 |
| endothelial                   | CEACAM5 |        0.0603486  |             0       |             4.7619   |       105 |           11 |
| endothelial                   | CST1    |        0.138062   |             0       |             9.52381  |       105 |           11 |
| endothelial                   | UBE2S   |        0.491512   |             0       |            34.2857   |       105 |           11 |
| endothelial                   | CCR6    |        0.0111846  |             0       |             0.952381 |       105 |           11 |
| mast cells                    | CEACAM5 |        0.07887    |             0       |             7.05882  |        85 |            8 |
| mast cells                    | CST1    |        0.0466986  |             0       |             4.70588  |        85 |            8 |
| mast cells                    | UBE2S   |        0.501657   |             0       |            36.4706   |        85 |            8 |
| mast cells                    | CCR6    |        0.0183649  |             0       |             1.17647  |        85 |            8 |
| malignant ductal / epithelial | CEACAM5 |        1.62926    |             1.5501  |           100        |      1925 |           15 |
| malignant ductal / epithelial | CST1    |        0.176533   |             0       |            10.8052   |      1925 |           15 |
| malignant ductal / epithelial | UBE2S   |        0.6686     |             0       |            45.2987   |      1925 |           15 |
| malignant ductal / epithelial | CCR6    |        0.021501   |             0       |             1.76623  |      1925 |           15 |
| CD8 T cells                   | CEACAM5 |        0.016958   |             0       |             1.03093  |        97 |           11 |
| CD8 T cells                   | CST1    |        0.0132681  |             0       |             1.03093  |        97 |           11 |
| CD8 T cells                   | UBE2S   |        0.790903   |             1.02714 |            50.5155   |        97 |           11 |
| CD8 T cells                   | CCR6    |        0.0589554  |             0       |             4.12371  |        97 |           11 |
| Tregs                         | CEACAM5 |        0.022544   |             0       |             1.35135  |        74 |           11 |
| Tregs                         | CST1    |        0.0876063  |             0       |             5.40541  |        74 |           11 |
| Tregs                         | UBE2S   |        0.603572   |             0       |            36.4865   |        74 |           11 |
| Tregs                         | CCR6    |        0.601289   |             0       |            36.4865   |        74 |           11 |
| T cells                       | CEACAM5 |        0.0226468  |             0       |             1.875    |       160 |           12 |
| T cells                       | CST1    |        0.0336064  |             0       |             2.5      |       160 |           12 |
| T cells                       | UBE2S   |        0.490138   |             0       |            30        |       160 |           12 |
| T cells                       | CCR6    |        0.218861   |             0       |            13.75     |       160 |           12 |
| B cells                       | CEACAM5 |        0.0280484  |             0       |             2.77778  |        36 |            9 |
| B cells                       | CST1    |        0.176909   |             0       |            13.8889   |        36 |            9 |
| B cells                       | UBE2S   |        0.832231   |             1.00864 |            52.7778   |        36 |            9 |
| B cells                       | CCR6    |        0.252741   |             0       |            16.6667   |        36 |            9 |

### Co-expression Comparison (Threshold > 0)
| cell_type                     |   v1_pair_coexpression_fraction |   v2_pair_coexpression_fraction |   n_cells |
|:------------------------------|--------------------------------:|--------------------------------:|----------:|
| normal acinar                 |                      0.00066335 |                      0          |      3015 |
| normal ductal                 |                      0.00605305 |                      0          |      5617 |
| CAF / fibroblast              |                      0.00652458 |                      0.015659   |      2299 |
| macrophages / monocytes       |                      0.0125745  |                      0.00330907 |      1511 |
| endothelial                   |                      0.00952381 |                      0.00952381 |       105 |
| mast cells                    |                      0          |                      0.0235294  |        85 |
| malignant ductal / epithelial |                      0.00935065 |                      0.108052   |      1925 |
| CD8 T cells                   |                      0.0309278  |                      0          |        97 |
| Tregs                         |                      0.162162   |                      0          |        74 |
| T cells                       |                      0.05       |                      0          |       160 |
| B cells                       |                      0.0833333  |                      0.0277778  |        36 |
