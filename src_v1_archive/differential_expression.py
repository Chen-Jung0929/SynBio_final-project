#!/usr/bin/env python3
import os
import sys
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import ranksums
from statsmodels.stats.multitest import multipletests
from sklearn.metrics import roc_auc_score

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_de_analysis(df_expr, df_meta, tables_dir, de_config):
    print("[*] Running differential expression analysis...")
    
    # Align sample ids
    samples = df_expr.columns.tolist()
    df_meta = df_meta.set_index("sample_id").loc[samples]
    
    is_pdac = (df_meta["group"] == "PDAC").values
    is_normal = (df_meta["group"] == "Normal").values
    
    pdac_cols = df_expr.columns[is_pdac]
    normal_cols = df_expr.columns[is_normal]
    
    print(f"[*] Comparing PDAC (N={len(pdac_cols)}) vs Normal (N={len(normal_cols)})")
    
    results = []
    
    count = 0
    total = len(df_expr)
    
    for gene, row in df_expr.iterrows():
        pdac_vals = row[is_pdac].values
        normal_vals = row[is_normal].values
        
        # Calculate means
        mean_pdac = np.mean(pdac_vals)
        mean_normal = np.mean(normal_vals)
        
        # Log2 fold change (since values are log2(tpm+0.001), difference is log2FC)
        log2fc = mean_pdac - mean_normal
        
        # Wilcoxon rank-sum test
        stat, pval = ranksums(pdac_vals, normal_vals)
        
        # AUC (Area Under ROC)
        # Labels: 1 for PDAC, 0 for Normal
        y_true = np.concatenate([np.ones(len(pdac_vals)), np.zeros(len(normal_vals))])
        y_scores = np.concatenate([pdac_vals, normal_vals])
        try:
            auc = roc_auc_score(y_true, y_scores)
        except ValueError:
            auc = 0.5 # Default if all values are identical
            
        # Specificity score: What fraction of Normal samples have expression below the 10th percentile of Tumor?
        # A high specificity score means normal tissue is very clean relative to the tumor range
        p10_pdac = np.percentile(pdac_vals, 10)
        spec_score = np.mean(normal_vals < p10_pdac)
        
        results.append({
            "gene": gene,
            "mean_pdac": mean_pdac,
            "mean_normal": mean_normal,
            "log2fc": log2fc,
            "p_value": pval,
            "auc": auc,
            "specificity_score": spec_score
        })
        
        count += 1
        if count % 10000 == 0:
            print(f"    Calculated {count}/{total} genes...")
            
    df_de = pd.DataFrame(results)
    
    # Filter out NaNs and run FDR correction
    df_de = df_de.dropna(subset=["p_value"])
    p_vals = df_de["p_value"].values
    reject, fdr_vals, _, _ = multipletests(p_vals, alpha=0.05, method="fdr_bh")
    df_de["fdr"] = fdr_vals
    
    # Save discovery DEGs
    out_de_path = tables_dir / "differential_expression_discovery.csv"
    df_de.to_csv(out_de_path, index=False)
    print(f"[+] Saved all DE results to {out_de_path}")
    
    # Filter candidates
    # abs(log2fc) > log2fc_threshold, fdr < fdr_threshold, tumor-high preferred (log2fc > 0), and auc >= auc_threshold
    lfc_t = de_config["log2fc_threshold"]
    fdr_t = de_config["fdr_threshold"]
    auc_t = de_config["auc_threshold"]
    
    candidates = df_de[
        (df_de["log2fc"] >= lfc_t) & 
        (df_de["fdr"] < fdr_t) & 
        (df_de["auc"] >= auc_t)
    ].sort_values(by="auc", ascending=False)
    
    out_cand_path = tables_dir / "top_tumor_high_candidates.csv"
    candidates.to_csv(out_cand_path, index=False)
    print(f"[+] Identified {len(candidates)} tumor-high candidates with FDR<{fdr_t}, Log2FC>={lfc_t}, AUC>={auc_t}.")
    print(f"[+] Saved candidates to {out_cand_path}")
    
    # Show top 10 candidates
    print("\n--- Top 10 Tumor-High Candidates ---")
    print(candidates[["gene", "log2fc", "fdr", "auc", "specificity_score"]].head(10).to_string(index=False))

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    
    print(f"[*] Loading preprocessed files:\n    - {expr_path}\n    - {meta_path}")
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    run_de_analysis(df_expr, df_meta, tables_dir, config["de_analysis"])

if __name__ == "__main__":
    main()
