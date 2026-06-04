# SynBio Final Project: PDAC Logic-Gated Biosensor Discovery

## Project Conclusion: The V5 "Single-Cell First" Breakthrough

This repository documents the evolution of our computational pipeline to discover a two-input synthetic-biology AND-gate biosensor for Pancreatic Ductal Adenocarcinoma (PDAC). 

After iterating through multiple generations (V1 to V4), the project faced a critical biological bottleneck: **Bulk-First discovery is fundamentally flawed for logic-gated synthetic circuits.** In V4, we discovered that gene pairs mathematically optimized to separate PDAC from Normal tissue in Bulk RNA-seq often exhibited high off-target expression in the tumor microenvironment (e.g., Cancer-Associated Fibroblasts, Immune cells) rather than strictly localizing to the malignant ductal epithelial cells themselves.

**The Solution: The V5 Pipeline**
We reversed the methodology. V5 implements a **Single-Cell First** discovery approach.
1. **Phase 1 (scRNA Discovery)**: The pipeline strictly demands that candidate pairs must co-express in malignant ductal cells (>60%) while maintaining low co-expression (<10%) across *all* off-target compartments (fibroblasts, T-cells, B-cells, macrophages, etc.). 
2. **Phase 2 (Bulk Clinical Validation)**: Only pairs that pass the strict single-cell biological constraint are validated backward against the massive TCGA/GTEx bulk cohorts for true clinical generalization.

## The Final Validated Candidate

By successfully bridging high-resolution single-cell screening with robust bulk generalizability, the V5 pipeline produced a computational breakthrough. Out of 11 million possible pairs, 34 passed the single-cell constraints, and exactly **13** successfully generalized to Bulk RNA-seq with AUC > 0.70.

🏆 **The V5 Champion Pair: `S100A14` AND `GPX1`**

### Key Metrics:
* **Target Co-expression**: 60.6% (Malignant Ductal / Epithelial)
* **Pooled Off-target Co-expression**: 9.2%
* **Patient-Positive Rate**: 100.0%
* **Bulk AUC (TCGA/GTEx)**: 0.963
* **Threshold Instability**: 0.048

This candidate achieves an outstanding Bulk AUC of 0.963 while guaranteeing target localization to the malignant compartment, resolving the circularity and off-target expression issues that plagued V1-V4.

## Handover Instructions for Human Team Members

The codebase is fully modular and has been automated for reproducibility.

### Environment Setup
```powershell
# Create environment
pip install -r requirements.txt
```

### Reproducing the V5 Results
The V5 pipeline scripts are located in `analysis_v5/`. To reproduce the final results from scratch:

1. **Run scRNA Discovery (Phase 1)**
   ```powershell
   python analysis_v5\01_scrna_discovery.py
   ```
   *Generates `results_v5/tables/v5_scrna_candidates.csv` (34 candidates).*

2. **Download and Extract TCGA Bulk Data (Phase 2 Data Prep)**
   ```powershell
   python src\data_download.py
   python analysis_v5\02c_extract_bulk_for_candidates.py
   ```
   *Downloads raw data and efficiently extracts a lightweight matrix for the 34 candidates, outputting to `data/processed/expression_matrix_v5.csv.gz`.*

3. **Run Bulk Validation (Phase 2)**
   ```powershell
   python analysis_v5\02_bulk_validation.py
   ```
   *Validates candidates on the extracted bulk matrix and selects the final pair.*

4. **Generate Reports (Phase 3)**
   ```powershell
   python analysis_v5\03_generate_reports.py
   ```
   *Compiles the final `V5_FINAL_REPORT.md` and `V5_AUDIT_REPORT.md`.*

### Main Directories
* `analysis_v5/`: Contains the state-of-the-art V5 single-cell-first scripts.
* `reports_v5/`: The finalized markdown reports and audits for V5.
* `results_v5/`: The quantitative tables output by the V5 pipeline.
* `src/`: Shared data download and preprocessing utilities.
* `analysis_v1` - `analysis_v4`: Archived pipelines demonstrating the progression of our hypothesis.

## Future Work (Wet-Lab Translation)
The computational discovery phase is now officially wrapped up. The next steps are purely experimental:
1. Validate `S100A14 + GPX1` localization via Spatial Transcriptomics or Multiplex IF.
2. Select appropriate synthetic biology promoters for these genes.
3. Conduct in vitro feasibility studies (dynamic range and leakiness testing).

**End of Project Report.**
