# Reproducibility and Quality Control Log

## Software and Environment Parameters

1. **Python Version**: `/opt/anaconda3/bin/python` (Python 3.13.0)
2. **Analytical Libraries**:
   * scikit-learn (1.7.2)
   * xgboost (3.2.0)
   * shap (0.52.0)
   * pandas, numpy, scipy, matplotlib, seaborn
3. **Deterministic Random Seed**: `42` applied to all estimators and splits.

## Reproducibility Commands

To reproduce the Stage 1 to Stage 8 computational pipeline, run:
```bash
python analysis_v2/pipeline_v2.py
```
This generates all tables under `results_v2/tables/` and figures under `results_v2/figures/`.
