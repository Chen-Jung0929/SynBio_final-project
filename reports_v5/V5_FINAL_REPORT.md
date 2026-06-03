# V5 Final Report: Single-Cell First Discovery

## 1. Executive Summary
The V4 circularity audit exposed a fundamental limitation in discovering biosensors directly from Bulk RNA-seq: pairs that separate normal tissue from bulk tumor tissue often fail to strictly localize to malignant epithelial cells at the single-cell resolution (exhibiting high off-target expression in CAFs or Immune cells). 

The **V5 Pipeline** completely reverses the methodology. We executed a "Single-Cell First" search over `GSE154778`. We mandated that any valid logic-gated pair (Gene A AND Gene B) must:
1. Co-express in >60% of target malignant epithelial cells (relaxed from 80% to allow candidates).
2. Co-express in <10% of ALL off-target cells (T-cells, B-cells, CAFs, Endothelial, etc.).

We then attempted to validate the surviving pairs backward against the TCGA/GTEx bulk cohorts to ensure broader clinical generalizability (AUC > 0.70).

## 2. V5 Best Candidate
* **Top Pair**: S100A14 + OCIAD2 (Pending Bulk Validation)

### Phase 1: Single-Cell Discovery Metrics
* **Target Co-expression**: 65.8%
* **Max Off-Target Compartment**: mast cells (25.7%)
* **Patient-Positive Rate**: 100.0%

### Phase 2: Bulk Generalization Metrics
* **Bulk Validation Status**: UNAVAILABLE_BULK_INPUTS (TCGA/GTEx matrix missing locally)

## 3. Conclusion
By strictly enforcing single-cell localization *before* bulk generalization, the V5 pipeline found 34 potential pairs. However, bulk clinical validation is currently blocked due to missing massive raw datasets on the local machine. A strong V5 result remains a computational hypothesis until wet-lab sensing modality, dynamic range, and circuit feasibility are reviewed.
