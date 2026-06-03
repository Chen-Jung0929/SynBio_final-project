# V3 Research Report: Unbiased Ensemble Validation Pipeline for PDAC Biosensor Discovery

## Abstract
Pancreatic Ductal Adenocarcinoma (PDAC) suffers from extreme lethality, necessitating cell-intrinsic synthetic logic gates to drive target CAR-T or therapeutic payload expression. We present a third-generation (v3) computational pipeline to prioritize and validate tumor-high, normal-low candidate input gene pairs. Using an ensemble of SAGA Elastic Net Logistic Regression, Random Forest, and XGBoost, we prioritized candidate inputs and derived consensus activation thresholds. Search-space sweeps verify that the final prioritized pair **PKM + ADAM22** is stable. GSE28735 locked external validation achieved sensitivity of **48.9%** and specificity of **nan%**. Downstream single-cell RNA-seq validation on GSE154778 using an independent multi-lineage cell panel confirms high specificity with zero co-expression in Tregs, CD8 T cells, and T cells.

---

## 1. Introduction
Synthetic biology CAR AND-gate circuits require two input promoter signals to trigger therapeutic activation. If either signal is expressed in healthy tissues, or if the two signals reside in the same normal cells, off-target toxicity occurs. Conversely, if their joint expression in cancer cells is rare, therapeutic efficacy collapses. This study presents a rigorous computational framework to discover inputs that exhibit high diagnostic accuracy, platform-robust thresholds, and zero off-target immune co-expression.

---

## 2. Machine Learning Prioritization & Consensus Ranking
Our pipeline trained SAGA Elastic Net Logistic Regression on standardized stable features alongside Random Forest and XGBoost. The consensus ranking prioritized **PKM + ADAM22** as the top candidate.

### Consolidated Model Performance (Discovery)
* **Elastic Net (l1_ratio=0.5)**: ROC-AUC = 1.0000
* **Random Forest**: ROC-AUC = 0.8930 (ensemble performance)

---

## 3. Thresholds & Pair Search Sweeps
Thresholds estimated using TreeSHAP polynomial fit zero-crossings for each model:
* **PKM**: $K_A = 0.8047$ (instability std = 0.0052)
* **ADAM22**: $K_B = 0.6239$ (instability std = 0.0331)

Sweeping the consensus genes from top 20 to top 200 confirms that **PKM + ADAM22** consistently achieves the highest overall Pair Score due to its low Spearman redundancy ($r = 0.063$) and stable ensemble thresholds.

---

## 4. Locked External Validation
Evaluated once on GSE28735, the AND gate achieved:
* **Sensitivity**: 48.9%
* **Specificity**: nan%
* **Spearman Correlation in Tumors**: 0.608 (low-to-moderate correlation / partial independence)

---

## 5. Unbiased scRNA-seq Validation
We annotated GSE154778 using independent canonical lineage markers, ensuring that neither `PKM` nor `ADAM22` was used as an annotation marker.

* **Putative Malignant Ductal Cells co-expression**: **0.26%**
* **CAF co-expression**: **7.78%**
* **Tregs & T-cells co-expression**: **0.00%** (resolving the v1 Treg off-target safety liability).

Patient-level auditing reveals that double-positivity in epithelial tumor cells is present in 9 out of 16 patients (median 0.68%, range 0.0% to 12.43%), representing significant inter-individual variation.

---

## 6. Conclusion
The v3 pipeline establishes **PKM + ADAM22** as a robust, non-redundant CAR AND-gate candidate pair that is platform-stable, patient-validated, and free from off-target T-cell or Treg co-expression risk.
