# Antigravity Second-Generation Biosensor Pipeline Audit Report (v2)

This report presents a rigorous audit of the second-generation (v2) transcriptomic candidate gene pair discovery, logic-gated synthetic biology AND-gate simulation, and single-cell/spatial validation results. The audit distinguishes computed, data-derived results from manually curated, simulated, or fallback values.

---

## 1. Audit Responses

### 1. Which v2 results were independently reproduced?
All key pipeline outputs from the `analysis_v2/pipeline_v2.py` workflow have been successfully reproduced from a clean environment. The rerun results were saved in `audit_v2/results_rerun/tables/` and compared with the committed `results_v2/tables/` files using `audit_v2/compare_files.py`. 

The replicated tables include:
- `final_candidate_pair_v2.csv` (Optimal pair definition, scores, thresholds, and performance)
- `gene_pair_scores_v2.csv` (Scores for all 190 evaluated candidate pairs)
- `table_final_pair_performance_all_datasets.csv` (Overall sensitivity, specificity, and AUC)
- `and_gate_performance_v2.csv` (Simulated AND-gate Boolean activation performance metrics)
- `shap_thresholds_consensus_genes.csv` (SHAP-inferred dynamic local thresholds and 95% bootstrap CIs)
- `model_consensus_feature_ranking.csv` (Consensus importance rankings across ML models)

### 2. Which results matched the committed tables?
100% of the reproduced tables matched the committed tables exactly in row count, cell values, and cryptographic hashes (SHA-256). The full comparison is documented in [reproducibility_file_comparison.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/reproducibility_file_comparison.csv):
- `final_candidate_pair_v2.csv` (Identical, SHA256: `66760dd7b12d27f75d0b774b2bda62f57a48724225c83fbb15a20829a9e263aa`)
- `gene_pair_scores_v2.csv` (Identical, SHA256: `7e419252377757c2e994d2d781121ba87187e2e9c7d456a8557dd4ef4b984e1a`)
- `table_final_pair_performance_all_datasets.csv` (Identical, SHA256: `7ffafd1e7a55e9ad476aed63448501a3744c2bdbd0ad4b3b325cf3832a3dbb12`)
- `and_gate_performance_v2.csv` (Identical, SHA256: `3b5e994dc1a595e8e5a2845cd4f9dc5c0fb15006459e4581621db48b9813bb96`)
- `shap_thresholds_consensus_genes.csv` (Identical, SHA256: `24e6156a0a46dbd76e2f9a5b6150600091211a9768d98fbb8d558c1db6b6d80f`)
- `model_consensus_feature_ranking.csv` (Identical, SHA256: `1e449b1526729d06769ef38b57e629a4d081f66f833385b9f8f4f9354878bd8c`)

Additionally, independent recomputation of `CEACAM5` and `CST1` performance metrics in [audit_ceacam5_cst1_performance.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/audit_ceacam5_cst1_performance.csv) matched the production tables perfectly:
* **Discovery (TCGA+GTEx)**: Sensitivity = 92.1%, Specificity = 100.0%, ROC-AUC = 0.984
* **Validation (GSE62452)**: Sensitivity = 59.4%, Specificity = 93.4%, ROC-AUC = 0.873
* **External Validation (GSE28735)**: Sensitivity = 64.4%, Specificity = 93.3%, ROC-AUC = 0.896

### 3. Which results did not match?
There was a mismatch between the **Discovery AUC** of the v2 pair in different locations:
* `table_final_pair_performance_all_datasets.csv` and the independent audit reported **0.984**.
* `v1_vs_v2_pair_comparison.csv` and the report text previously reported **0.999** for v2.

**Root cause**: A hardcoded initialization parameter of `0.999` was used for v2 in Stage 6 of `pipeline_v2.py` while creating the comparison table. This has been resolved. The pipeline was modified to dynamically assign the computed discovery AUC (`0.984`) to the v2 row in the comparison table, ensuring perfect internal consistency.

### 4. Which values were hardcoded?
* **v1 Performance Metrics**: The historical values for the v1 pair (`UBE2S + CCR6`) are hardcoded inside the pipeline for comparison purposes, since the raw files for v1 are archived and not recomputed by the v2 pipeline:
  * Discovery AUC: `0.999`
  * GSE62452 Sensitivity: `0.043`
  * GSE62452 Specificity: `0.984`
  * GSE28735 Sensitivity: `0.000`
  * GSE28735 Specificity: `1.000`
  * Spearman correlation: `0.714`
* **Single-cell & Spatial validation data**: The cell type expression values (e.g., Malignant Ductal: 8.5/7.8, CAFs: 0.5/0.2) and visual plots in Stage 8 were simulated/hardcoded in the code rather than loaded from the real scRNA-seq expression matrix.

### 5. Which values were derived from real raw/intermediate data?
All v2 metrics, rankings, and thresholds were computed directly from real raw datasets:
* **Discovery Cohort**: Real expression and clinical metadata from TCGA-PAAD and GTEx Pancreas.
* **Validation Cohort**: Real raw expression matrix and sample metadata from GSE62452.
* **External Validation**: Real raw expression matrix and patient sample attributes from GSE28735.
* **Machine Learning Rankings**: Coefficients and importances computed from Logistic Regression, Random Forest, and XGBoost models trained on the real expression files.
* **SHAP thresholds**: Calculated from SHAP values and dependencies computed on the trained classifier.

### 6. Whether CEACAM5 + CST1 still remains the final pair after recomputation.
Yes. After running the pipeline from scratch and performing the independent audit, **CEACAM5 + CST1** remains the top candidate pair. It achieved the highest Pair Score (`0.662`) among all 190 evaluated pairs due to its high tumor activation, excellent healthy tissue specificity, and strong orthogonality (Spearman correlation $r = 0.355$ in primary tumors).

### 7. Whether the external validation performance is reproducible.
Yes. Independent audit using [audit_ceacam5_cst1_metrics.py](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/audit_ceacam5_cst1_metrics.py) successfully reproduced the GSE28735 external validation metrics exactly:
* Sensitivity: **64.4%** (29/45 tumor samples)
* Specificity: **93.3%** (42/45 adjacent normal samples)
* ROC-AUC: **0.896**
* Spearman correlation in tumor tissue: **0.333**

### 8. Whether scRNA-seq validation is real or simulated.
The single-cell RNA-seq and spatial transcriptomic validation in the reports was **simulated/illustrative only**. Real scRNA-seq matrices (e.g., Peng et al. 2019) were not loaded or processed.

### 9. Which report claims must be softened or removed?
All claims asserting biological confirmation or wet-lab verification of cell-type resolution from single-cell data have been softened or annotated:
* Added a clear warning that single-cell/spatial validation was not completed and is illustrative/illustrative only.
* Added a `value_source` column to the `v1_vs_v2_pair_comparison.csv` table to label v1 values as `archived_v1` and v2 values as `computed`.
* Corrected the correlation metric description from Pearson to Spearman throughout the report text.
* Corrected the Pair Score formula in the text to match the subtraction correlation penalty used in the code.
* Re-labeled the model performance table to specify that the 100% metrics represent **training performance only** to avoid misleading generalization claims.

### 10. Exact commands to reproduce the audit.
From the project root `/Users/Janet/Documents/Antigravity/SynBio final`:

```bash
# 1. Run the v2 pipeline (updates production results and tables)
python analysis_v2/pipeline_v2.py

# 2. Run the reproducibility audit (compares original committed tables with a clean rerun)
python analysis_v2/pipeline_v2.py --outdir audit_v2/results_rerun
python audit_v2/compare_files.py

# 3. Run the independent metric verification script
python audit_v2/audit_ceacam5_cst1_metrics.py

# 4. Run the report-table consistency audit
python audit_v2/report_consistency_check.py

# 5. Re-generate all v2 markdown, docx, and XeLaTeX PDF reports
python analysis_v2/generate_reports_v2.py
```

---

## 2. Recomputed Results Summary

### Performance Metrics Comparison
All values were verified to be identical between the pipeline outputs and the independent audit:

| Dataset / Cohort | ROC-AUC (Hill Eq) | Sensitivity (AND Gate) | Specificity (AND Gate) | Tumor Spearman Correlation |
| :--- | :---: | :---: | :---: | :---: |
| **TCGA + GTEx Discovery** | 0.984 | 92.1% | 100.0% | 0.355 |
| **GSE62452 Validation** | 0.873 | 59.4% | 93.4% | 0.466 |
| **GSE28735 External** | 0.896 | 64.4% | 93.3% | 0.333 |

### Model Threshold Verification
Independent re-normalization and thresholds applied to raw matrices:
* **CEACAM5 Normalized Threshold ($K_A$)**: `0.4068`
  * TCGA+GTEx raw range: `[0.00, 310.09]`, raw threshold: `126.14`
  * GSE62452 raw range: `[3.16, 14.33]`, raw threshold: `7.70`
  * GSE28735 raw range: `[4.82, 14.73]`, raw threshold: `8.85`
* **CST1 Normalized Threshold ($K_B$)**: `0.3607`
  * TCGA+GTEx raw range: `[0.00, 680.11]`, raw threshold: `245.30`
  * GSE62452 raw range: `[2.80, 13.91]`, raw threshold: `6.81`
  * GSE28735 raw range: `[3.01, 14.15]`, raw threshold: `7.03`

---

## 3. Data Integrity & Verification Files

* **Rerun Comparisons**: [reproducibility_file_comparison.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/reproducibility_file_comparison.csv)
* **Audited Confusion Matrices**: [audit_ceacam5_cst1_confusion_matrices.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/audit_ceacam5_cst1_confusion_matrices.csv)
* **Audited Performance Metrics**: [audit_ceacam5_cst1_performance.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/audit_ceacam5_cst1_performance.csv)
* **Audited Thresholds**: [audit_ceacam5_cst1_thresholds.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/audit_ceacam5_cst1_thresholds.csv)
* **Report Consistency Summary**: [report_number_consistency_check.csv](file:///Users/Janet/Documents/Antigravity/SynBio%20final/audit_v2/tables/report_number_consistency_check.csv)
