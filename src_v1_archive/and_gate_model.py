#!/usr/bin/env python3
import os
import sys
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def hill_equation(x, K, n):
    """
    Hill equation: f(x) = x^n / (K^n + x^n)
    """
    # Clip to avoid division by zero or negative values
    x = np.clip(x, 0, None)
    K = np.clip(K, 1e-6, None)
    return (x ** n) / (K ** n + x ** n)

def run_and_gate_simulation(df_expr, df_meta, tables_dir, and_config):
    print("[*] Starting AND gate mathematical modeling...")
    
    # Load final selected pair
    pair_path = tables_dir / "final_candidate_pair.csv"
    if not pair_path.exists():
        print(f"[-] Final pair not found at {pair_path}. Run orthogonality_analysis.py first.")
        sys.exit(1)
        
    df_pair = pd.read_csv(pair_path)
    gene_a = df_pair.loc[0, "gene_A"]
    gene_b = df_pair.loc[0, "gene_B"]
    
    # Load SHAP thresholds
    df_thresh = pd.read_csv(tables_dir / "shap_threshold_candidates.csv").set_index("gene")
    thresh_a_raw = df_thresh.loc[gene_a, "inferred_threshold"]
    thresh_b_raw = df_thresh.loc[gene_b, "inferred_threshold"]
    
    print(f"[*] Simulating AND gate biosensor for inputs: {gene_a} and {gene_b}")
    print(f"[*] Raw SHAP thresholds: {gene_a} = {thresh_a_raw:.3f}, {gene_b} = {thresh_b_raw:.3f}")
    
    # Get expression data for the two genes
    expr_a = df_expr.loc[gene_a].values
    expr_b = df_expr.loc[gene_b].values
    y_true = (df_meta.set_index("sample_id").loc[df_expr.columns]["group"] == "PDAC").astype(int).values
    
    # Rescale expression values to [0, 1] range using MinMax scaling
    min_a, max_a = np.min(expr_a), np.max(expr_a)
    min_b, max_b = np.min(expr_b), np.max(expr_b)
    
    norm_a = (expr_a - min_a) / (max_a - min_a)
    norm_b = (expr_b - min_b) / (max_b - min_b)
    
    # Map the thresholds to the [0, 1] range as well
    K_a = (thresh_a_raw - min_a) / (max_a - min_a)
    K_b = (thresh_b_raw - min_b) / (max_b - min_b)
    
    print(f"[*] Rescaled Hill K parameters: K_A = {K_a:.3f}, K_B = {K_b:.3f}")
    
    # Sweep parameters
    hill_coeffs = and_config["hill_coefficients"]
    leakiness_levels = and_config["leakiness_levels"]
    v_max = and_config["v_max"]
    
    sweep_results = []
    
    for n in hill_coeffs:
        for p_basal in leakiness_levels:
            # AND gate output: Output = P_basal + V_max * f(A) * f(B)
            # Clip output to V_max to respect biological maximum output limits
            output = p_basal + v_max * hill_equation(norm_a, K_a, n) * hill_equation(norm_b, K_b, n)
            output = np.clip(output, 0, v_max)
            
            # Evaluate as classifier (using Youden's Index to find optimal threshold on output)
            auc = roc_auc_score(y_true, output)
            
            # Find best classification threshold
            best_thresh = 0.5
            best_acc = 0.0
            best_spec = 0.0
            best_sens = 0.0
            
            for t in np.linspace(0.0, 1.0, 101):
                preds = (output > t).astype(int)
                acc = accuracy_score(y_true, preds)
                if acc > best_acc:
                    best_acc = acc
                    best_thresh = t
                    best_sens = recall_score(y_true, preds)
                    # Specificity = TN / (TN + FP) = Recall of class 0
                    best_spec = recall_score(1 - y_true, 1 - preds)
            
            sweep_results.append({
                "Hill_n": n,
                "P_basal": p_basal,
                "ROC_AUC": auc,
                "Optimal_Threshold": best_thresh,
                "Accuracy": best_acc,
                "Sensitivity": best_sens,
                "Specificity": best_spec,
                "Dynamic_Range": v_max - p_basal
            })
            
    df_sweep = pd.DataFrame(sweep_results).sort_values(by="ROC_AUC", ascending=False)
    sweep_out = tables_dir / "and_gate_parameter_sweep.csv"
    df_sweep.to_csv(sweep_out, index=False)
    print(f"[+] Saved parameter sweep results to {sweep_out}")
    print(df_sweep.head(10).to_string(index=False))
    
    # Final best AND gate model selection
    best_sweep = df_sweep.iloc[0]
    best_n = int(best_sweep["Hill_n"])
    best_p_basal = best_sweep["P_basal"]
    
    # Compute output with best parameters
    best_output = best_p_basal + v_max * hill_equation(norm_a, K_a, best_n) * hill_equation(norm_b, K_b, best_n)
    best_output = np.clip(best_output, 0, v_max)
    best_preds = (best_output > best_sweep["Optimal_Threshold"]).astype(int)
    
    # Save best parameters and final metrics
    final_perf = pd.DataFrame([{
        "gene_A": gene_a,
        "gene_B": gene_b,
        "Hill_n": best_n,
        "P_basal": best_p_basal,
        "K_A": K_a,
        "K_B": K_b,
        "Optimal_Threshold": best_sweep["Optimal_Threshold"],
        "ROC_AUC": best_sweep["ROC_AUC"],
        "Accuracy": best_sweep["Accuracy"],
        "Sensitivity": best_sweep["Sensitivity"],
        "Specificity": best_sweep["Specificity"]
    }])
    perf_out = tables_dir / "and_gate_performance.csv"
    final_perf.to_csv(perf_out, index=False)
    print(f"[+] Saved final AND gate model performance to {perf_out}")
    print(final_perf.to_string(index=False))

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    run_and_gate_simulation(df_expr, df_meta, tables_dir, config["and_gate"])

if __name__ == "__main__":
    main()
