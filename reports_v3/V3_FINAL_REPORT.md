# V3 Research Report: Unbiased Ensemble Validation Pipeline for PDAC Biosensor Discovery

## Abstract
Pancreatic Ductal Adenocarcinoma (PDAC) suffers from extreme lethality, motivating computational exploration of cell-intrinsic synthetic logic-gate inputs. We present a third-generation (v3) computational pipeline to prioritize tumor-high, normal-low candidate input gene pairs. Using an ensemble of SAGA Elastic Net Logistic Regression, Random Forest, and XGBoost, we prioritized candidate inputs and derived consensus activation thresholds. The default top100/top200 search spaces select **PKM + ADAM22**, while smaller top20/top50 search spaces select a different pair, so current pair selection is promising but not fully search-space invariant. GSE28735 locked external validation (containing 45 tumor and 45 normal samples) achieved sensitivity of **80.0%** and specificity of **82.2%** (ROC-AUC = **0.8588**, TP=36, FP=8, TN=37, FN=9). Downstream single-cell RNA-seq validation on GSE154778 using a preliminary marker-score-based targeted validation suggests low T-cell/Treg co-expression, but tumor-compartment double positivity is low and heterogeneous.

---

## 1. Introduction
Synthetic biology CAR AND-gate circuits require two input promoter signals to trigger therapeutic activation. If either signal is expressed in healthy tissues, or if the two signals reside in the same normal cells, off-target toxicity occurs. Conversely, if their joint expression in cancer cells is rare, therapeutic efficacy collapses. This study presents a rigorous computational framework to discover inputs that exhibit high diagnostic accuracy, platform-robust thresholds, and zero off-target immune co-expression.

---

## 2. Machine Learning Prioritization & Consensus Ranking
Our pipeline trained SAGA Elastic Net Logistic Regression on standardized stable features alongside Random Forest and XGBoost. The default top100 consensus-gene search prioritized **PKM + ADAM22** as the top candidate.

### Consolidated Model Performance (Discovery)
* **Elastic Net (l1_ratio=0.5)**: ROC-AUC = 1.0000
* **Random Forest**: ROC-AUC = 0.8930 (ensemble performance)

---

## 3. Thresholds & Pair Search Sweeps
Thresholds estimated using TreeSHAP polynomial fit zero-crossings for each model:
* **PKM**: $K_A = 0.8047$ (instability std = 0.0052)
* **ADAM22**: $K_B = 0.6239$ (instability std = 0.0331)

Sweeping the consensus genes from top 20 to top 200 (exact counts verified: top20=190, top50=1225, top100=4950, top200=19900 pairs) shows that **PKM + ADAM22** is the top pair in the default top100 and expanded top200 spaces. However, top20/top50 select **OCIAD2 + EDIL3**, and the top20-pair overlap across expanded search spaces is low. This means v3 improves audit discipline, but pair ranking remains sensitive to the candidate-gene search boundary.

---

## 4. Locked External Validation
Evaluated once on GSE28735 after final pair freezing, the AND gate achieved:
* **Tumor Sample Count**: 45
* **Normal Sample Count**: 45
* **Sensitivity**: 80.0%
* **Specificity**: 82.2%
* **ROC-AUC**: 0.8588
* **Confusion Matrix Counts**: TP=36, FP=8, TN=37, FN=9
* **Spearman Correlation in Tumors**: 0.111 (low-to-moderate correlation / partial independence)

Approximate 95% uncertainty intervals:
* **Sensitivity CI**: 66.2% to 89.1%
* **Specificity CI**: 68.7% to 90.7%
* **ROC-AUC CI**: 0.780 to 0.937

These intervals are approximate because only aggregate locked-validation outputs are versioned. Future runs should export sample-level gate scores to support bootstrap or DeLong intervals.

---

## 5. Preliminary scRNA-seq validation
We annotated GSE154778 using independent canonical lineage markers via a preliminary marker-score-based targeted validation, ensuring that neither `PKM` nor `ADAM22` was used as an annotation marker.

* **Putative Malignant Ductal Cells co-expression**: **0.26%**
* **CAF co-expression**: **7.78%**
* **Tregs co-expression**: **0.00%**.
* **CD8 T-cell co-expression**: **1.27%**.
* **T-cell co-expression**: **0.56%**.

Patient-level auditing reveals that double-positivity in epithelial tumor cells is present in 9 out of 16 patients (median 0.68%, range 0.0% to 12.43%), representing significant inter-individual variation.

---

## 6. Conclusion
The v3 pipeline establishes **PKM + ADAM22** as a computationally prioritized, weakly redundant candidate pair with a true locked external-validation audit. It does not yet establish a clinically sensitive PDAC detector or an experimentally validated synthetic-biology circuit. The next required work is pair-ranking robustness, calibration and uncertainty analysis, full non-circular single-cell/spatial validation, and wet-lab feasibility review for implementing the two inputs.
