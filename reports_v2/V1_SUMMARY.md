# Version 1 (v1) Pipeline Summary

## Original Implementation Parameters

1. **Original Discovery Dataset**: TCGA-PAAD primary tumors (N=178) combined with GTEx normal pancreas tissue (N=167).
2. **Original Validation Dataset**: GSE62452 microarray (69 tumor, 61 adjacent-normal).
3. **Original Selected Pair**: **UBE2S** + **CCR6**.
4. **Discovery Cohort Performance**:
   * Area Under ROC (AUC): **0.9986**
   * Accuracy: **98.6%**
   * Specificity: **99.4%**
   * Sensitivity: **97.8%**
5. **External Validation Performance (GSE62452)**:
   * Area Under ROC (AUC): **0.6480**
   * Accuracy: **48.5%**
   * Specificity: **98.4%**
   * Sensitivity: **4.3%** *(Extreme Sensitivity Collapse)*

## Main Limitations identified in v1

*   **Source Confounding**: TCGA (tumor) and GTEx (normal) cohorts are technically and clinically confounded. A classifier trained on this boundary risks learning batch differences rather than cancer biology.
*   **Single-Model Bias**: Feature selection relied strictly on L1 Logistic Regression coefficients and SHAP values derived from it.
*   **Redundancy in Pathway**: UBE2S and CCR6 show a Pearson correlation of **0.714** in tumors, indicating they may not represent orthogonal axes.
*   **Sensitivity Collapse**: Microarray and sequencing platform dynamic range differences caused the absolute RNA-seq derived thresholds to fail on GSE62452.
*   **Lack of Resolution**: Bulk tissue analysis could not identify cell-type-specific sources of the markers.
