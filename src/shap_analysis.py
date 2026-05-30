#!/usr/bin/env python3
import os
import sys
import yaml
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.tree import DecisionTreeClassifier

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def extract_threshold_stump(expr_vals, shap_vals):
    """
    Fits a decision tree of depth 1 (stump) to find the split threshold on expression values
    that best separates positive and negative SHAP values.
    """
    if len(np.unique(expr_vals)) < 2:
        return np.mean(expr_vals)
    # Target: 1 if SHAP value > 0, else 0
    y_target = (shap_vals > 0).astype(int)
    if len(np.unique(y_target)) < 2:
        # If all SHAP values are on one side, threshold is just the median
        return np.median(expr_vals)
        
    clf = DecisionTreeClassifier(max_depth=1)
    clf.fit(expr_vals.reshape(-1, 1), y_target)
    threshold = clf.tree_.threshold[0]
    return threshold

def run_shap_analysis(models_dir, tables_dir, figures_dir):
    print("[*] Starting SHAP explainable AI analysis...")
    
    model_path = models_dir / "best_classifier.pkl"
    if not model_path.exists():
        print(f"[-] Model not found at {model_path}. Run model_training.py first.")
        sys.exit(1)
        
    model_data = joblib.load(model_path)
    model = model_data["model"]
    model_name = model_data["model_name"]
    features = model_data["features"]
    X_train = model_data["X_train"]
    y_train = model_data["y_train"]
    X_test = model_data["X_test"]
    
    print(f"[*] Loaded best model: {model_name}")
    
    # Calculate SHAP values
    print("[*] Computing SHAP values...")
    if "Logistic_Regression" in model_name:
        # Use LinearExplainer or Explainer
        explainer = shap.Explainer(model, X_train)
        shap_values_obj = explainer(X_train)
        shap_values = shap_values_obj.values
    else:
        # For Random Forest and XGBoost, use TreeExplainer
        explainer = shap.TreeExplainer(model)
        shap_values_obj = explainer(X_train)
        # TreeExplainer returns a list of arrays for multi-class/RF, or single array for XGBoost
        if isinstance(shap_values_obj.values, list):
            # For binary RF classifier, class 1 is index 1
            shap_values = shap_values_obj.values[1]
        elif len(shap_values_obj.values.shape) == 3:
            # Multi-class output shape (samples, features, classes)
            shap_values = shap_values_obj.values[:, :, 1]
        else:
            shap_values = shap_values_obj.values
            
    # Calculate mean absolute SHAP value for feature importance
    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    df_importance = pd.DataFrame({
        "gene": features,
        "mean_abs_shap": mean_abs_shap
    }).sort_values(by="mean_abs_shap", ascending=False)
    
    importance_out = tables_dir / "shap_feature_importance.csv"
    df_importance.to_csv(importance_out, index=False)
    print(f"[+] Saved SHAP feature importance to {importance_out}")
    print(df_importance.head(10).to_string(index=False))
    
    # Extract thresholds for the top candidates
    # We will estimate thresholds for the top 100 genes by SHAP importance
    top_shap_genes = df_importance["gene"].head(100).tolist()
    threshold_results = []
    
    # Ensure figures output directory exists
    figures_dir.mkdir(parents=True, exist_ok=True)
    dep_plots_dir = figures_dir / "shap_dependence_top_genes"
    dep_plots_dir.mkdir(parents=True, exist_ok=True)
    
    for gene in top_shap_genes:
        idx = features.index(gene)
        expr_vals = X_train[gene].values
        shap_vals = shap_values[:, idx]
        
        # Extract threshold using decision stump method
        threshold = extract_threshold_stump(expr_vals, shap_vals)
        
        # Uncertainty: bootstrap threshold estimation (95% CI)
        bootstrap_thresholds = []
        np.random.seed(42)
        for _ in range(100):
            boot_idx = np.random.choice(len(expr_vals), size=len(expr_vals), replace=True)
            boot_expr = expr_vals[boot_idx]
            boot_shap = shap_vals[boot_idx]
            try:
                boot_thresh = extract_threshold_stump(boot_expr, boot_shap)
                bootstrap_thresholds.append(boot_thresh)
            except:
                pass
                
        ci_lower = np.percentile(bootstrap_thresholds, 2.5) if bootstrap_thresholds else threshold
        ci_upper = np.percentile(bootstrap_thresholds, 97.5) if bootstrap_thresholds else threshold
        
        threshold_results.append({
            "gene": gene,
            "inferred_threshold": threshold,
            "ci_95_lower": ci_lower,
            "ci_95_upper": ci_upper,
            "mean_expression": np.mean(expr_vals),
            "median_expression": np.median(expr_vals)
        })
        
        # Plot and save dependence plot
        plt.figure(figsize=(6, 4))
        sns.scatterplot(x=expr_vals, y=shap_vals, alpha=0.7, color="darkcyan")
        plt.axhline(0, color="gray", linestyle="--", linewidth=1)
        plt.axvline(threshold, color="crimson", linestyle="-.", label=f"Threshold: {threshold:.3f}")
        plt.axvspan(ci_lower, ci_upper, color="crimson", alpha=0.15, label="95% CI")
        plt.title(f"SHAP Dependence Plot: {gene}")
        plt.xlabel("Log2(TPM + 0.001)")
        plt.ylabel("SHAP Value")
        plt.legend()
        plt.tight_layout()
        plt.savefig(dep_plots_dir / f"{gene}_shap_dependence.png", dpi=150)
        plt.close()
        
    df_thresholds = pd.DataFrame(threshold_results)
    thresholds_out = tables_dir / "shap_threshold_candidates.csv"
    df_thresholds.to_csv(thresholds_out, index=False)
    print(f"[+] Saved SHAP threshold candidates to {thresholds_out}")
    print(df_thresholds.head(10).to_string(index=False))

def main():
    config = load_config()
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    figures_dir = Path(__file__).parent.parent / config["results"]["figures_dir"]
    models_dir = Path(__file__).parent.parent / config["results"]["models_dir"]
    
    run_shap_analysis(models_dir, tables_dir, figures_dir)

if __name__ == "__main__":
    main()
