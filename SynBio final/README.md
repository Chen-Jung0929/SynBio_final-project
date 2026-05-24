# SynBio Final Project: Logic-Gated Biosensor for PDAC

## Data-Driven Design of a Logic-Gated Biosensor via Unbiased Transcriptomic Profiling of Pancreatic Tumor Microenvironment

### Overview

This project implements a fully automated, data-driven computational pipeline to identify candidate gene pairs for a synthetic biology **AND-gate biosensor** targeting **pancreatic ductal adenocarcinoma (PDAC)**. The pipeline integrates differential expression analysis, machine learning classification, explainable AI (SHAP), orthogonality scoring, and Hill-equation-based mathematical modeling.

### Key Result

**Selected AND-gate pair: UBE2S (cell cycle) AND CCR6 (immune microenvironment)**

| Metric | Value |
|--------|-------|
| Discovery AUC | **0.9986** |
| Accuracy | **98.6%** |
| Sensitivity | **97.8%** |
| Specificity | **99.4%** |
| Random pair p-value | **< 0.0001** |

### Pipeline Architecture

```
TCGA-PAAD + GTEx Data → Preprocessing → Differential Expression → ML Classification
→ SHAP Analysis → Orthogonality Scoring → AND Gate Modeling → Validation & Plotting
```

### Project Structure

```
├── src/                          # Source code
│   ├── config.yaml               # Centralized configuration
│   ├── data_download.py          # Data acquisition
│   ├── preprocessing.py          # Sample extraction & filtering
│   ├── differential_expression.py # DE analysis
│   ├── model_training.py         # ML pipeline (LogReg, RF, XGB)
│   ├── shap_analysis.py          # SHAP XAI & threshold inference
│   ├── orthogonality_analysis.py # Pair scoring & selection
│   ├── and_gate_model.py         # Hill equation simulation
│   ├── plotting.py               # Figure generation
│   └── validation.py             # Controls & external validation
├── results/
│   ├── tables/                   # All result CSVs
│   └── figures/                  # All generated plots
├── reports/
│   ├── final_report_draft.md     # Comprehensive final report
│   └── method_summary.md         # Concise methods summary
├── nchc_bridge.py                # NCHC SSH automation bridge
├── requirements.txt              # Python dependencies
└── environment.yml               # Conda environment
```

### Data Sources

- **Discovery**: TCGA-PAAD (n=178) + GTEx Normal Pancreas (n=167) via UCSC Xena
- **Validation**: GSE62452 (n=130) from GEO

### How to Reproduce

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline (in order)
python3 src/data_download.py
python3 src/preprocessing.py
python3 src/differential_expression.py
python3 src/model_training.py
python3 src/shap_analysis.py
python3 src/orthogonality_analysis.py
python3 src/and_gate_model.py
python3 src/validation.py
python3 src/plotting.py
```

### Compute Infrastructure

Executed on **NCHC** (National Center for High-performance Computing) biomedical node `t3-c4.nchc.org.tw`, automated via the Antigravity NCHC Bridge.

### License

This project is for academic/educational purposes (SynBio Final Project).
