# SynBio Final Project: Logic-Gated Biosensor for PDAC

## Data-Driven Design of a Logic-Gated Biosensor via Unbiased Transcriptomic Profiling of Pancreatic Tumor Microenvironment

### Overview

This project implements a fully automated, data-driven computational pipeline to identify optimal candidate gene pairs for a synthetic biology **AND-gate biosensor** targeting **pancreatic ductal adenocarcinoma (PDAC)**. The second-generation (v2) pipeline integrates differential expression analysis, same-cohort validation, machine learning classification (Lasso, RF, XGBoost), explainable AI (SHAP), orthogonality scoring, Hill-equation-based mathematical modeling, and single-cell transcriptomics validation.

### Key Result

**Selected AND-gate pair: CEACAM5 (cell adhesion) AND CST1 (tumor microenvironment secretion)**

| Metric | Value |
|--------|-------|
| Discovery AUC | **0.984** |
| Validation AUC (GSE62452) | **0.873** |
| External AUC (GSE28735) | **0.896** |
| Sensitivity (Discovery) | **92.1%** |
| Specificity (Discovery) | **100.0%** |
| Orthogonality (Tumor Spearman r) | **0.355 (Low correlation)** |
| Single-Cell Co-expression (Tumor vs Normal) | **10.8% vs 0.0%** |

### Pipeline Architecture

```
TCGA-PAAD + GTEx Data → Preprocessing & DE Analysis
↳ Same-cohort Validation (GSE62452) → Stable Gene Filtering
  ↳ Model-Consensus Selection (Lasso, RF, XGBoost)
    ↳ SHAP Threshold Inference → Orthogonality Scoring
      ↳ AND Gate Modeling & External Validation (GSE28735)
        ↳ Single-cell RNA-seq Validation (GSE154778) & Report Generation
```

### Project Structure

```
├── analysis_v2/                  # Core V2 analysis pipeline and report generation
│   ├── pipeline_v2.py            # Main pipeline script
│   └── generate_reports_v2.py    # Report compiler
├── scrna_validation/             # Single-cell RNA-seq validation pipeline
│   ├── scripts/                  # scRNA analysis scripts
│   ├── tables/                   # scRNA result tables
│   └── figures/                  # scRNA validation plots
├── results_v2/                   # Pipeline execution results (tables & figures)
├── reports_v2/                   # Compiled final reports (EN/ZH, PDF/Docx/MD)
├── src_v1_archive/               # Archived first-generation scripts
├── reports_v1_archive/           # Archived first-generation reports
├── results_v1_archive/           # Archived first-generation results
├── nchc_bridge.py                # NCHC SSH automation bridge
├── requirements.txt              # Python dependencies
└── environment.yml               # Conda environment
```

### Data Sources

- **Discovery Cohort**: TCGA-PAAD (n=178) + GTEx Normal Pancreas (n=167) via UCSC Xena
- **Same-Cohort Validation**: GSE62452 (n=130) from GEO
- **External Validation**: GSE28735 (n=90) from GEO
- **Single-Cell Validation**: GSE154778 (n=14,924 cells) from GEO

### How to Reproduce

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the V2 Core Pipeline
python3 analysis_v2/pipeline_v2.py

# 3. Run Single-Cell RNA-seq Validation
# Execute scripts sequentially in scrna_validation/scripts/
python3 scrna_validation/scripts/01_search_scrna_spatial_datasets.py
python3 scrna_validation/scripts/02_download_or_prepare_dataset.py
python3 scrna_validation/scripts/03_process_scrna_dataset.py
python3 scrna_validation/scripts/04_validate_ceacam5_cst1_scrna.py
python3 scrna_validation/scripts/05_validate_ceacam5_cst1_spatial.py
python3 scrna_validation/scripts/06_generate_scrna_spatial_report.py

# 4. Generate Final Reports (Markdown, PDF, Docx)
python3 analysis_v2/generate_reports_v2.py
```

### Compute Infrastructure

Executed on **NCHC** (National Center for High-performance Computing) biomedical node `t3-c4.nchc.org.tw`, automated via the Antigravity NCHC Bridge.

### License

This project is for academic/educational purposes (SynBio Final Project).
