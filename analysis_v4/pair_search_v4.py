#!/usr/bin/env python3
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import os
from pathlib import Path

def classify_correlation(r):
    abs_r = abs(r)
    if abs_r < 0.2:
        return "weak correlation / high independence"
    elif abs_r < 0.4:
        return "low-to-moderate correlation / partial independence"
    elif abs_r < 0.6:
        return "moderate correlation"
    else:
        return "high redundancy risk"

def load_scrna_prior(prior_path):
    if not os.path.exists(prior_path):
        return None
    df = pd.read_csv(prior_path)
    prior_dict = {}
    for _, row in df.iterrows():
        g = row['gene']
        ct = row['cell_type']
        pct = row['percent_expressing_fraction']
        if g not in prior_dict:
            prior_dict[g] = {}
        prior_dict[g][ct] = pct
    return prior_dict

def calculate_scrna_score(gene_a, gene_b, prior_dict):
    """
    Computes a bonus for target expression and penalty for off-target expression.
    """
    if not prior_dict or gene_a not in prior_dict or gene_b not in prior_dict:
        return 0, 0, 0
        
    dict_a = prior_dict[gene_a]
    dict_b = prior_dict[gene_b]
    
    target_cts = ["epithelial / ductal tumor-origin cells", "tumor-associated epithelial / putative malignant ductal epithelial"]
    target_coexpr = 0
    for ct in target_cts:
        if ct in dict_a and ct in dict_b:
            target_coexpr = max(target_coexpr, min(dict_a[ct], dict_b[ct]))
            
    off_target_cts = [
        "Tregs", "CD8 T cells", "T cells", "B cells", "NK cells", 
        "macrophages / monocytes", "acinar-like cells", "endocrine cells", 
        "endothelial", "mast cells", "plasma cells"
    ]
    max_off_target_coexpr = 0
    for ct in off_target_cts:
        if ct in dict_a and ct in dict_b:
            max_off_target_coexpr = max(max_off_target_coexpr, min(dict_a[ct], dict_b[ct]))
            
    # scRNA Score calculation
    # target_coexpr is typically 0.01-0.20, off_target should be 0.
    scrna_bonus = target_coexpr
    scrna_penalty = 5.0 * max_off_target_coexpr
    
    return target_coexpr, max_off_target_coexpr, (scrna_bonus - scrna_penalty)

def run_pair_search(df_expr, df_meta, df_expr_val, df_meta_val, top_genes, df_thresh, alpha=0.2, beta=0.1, gamma=1.0, prior_path=None, out_path=None):
    """
    Evaluates pairwise combinations using V4 logic (integrating scRNA-seq prior).
    """
    gene_to_thresh = dict(zip(df_thresh["gene"], df_thresh["K_final"]))
    gene_to_instab = dict(zip(df_thresh["gene"], df_thresh["threshold_instability_score"]))
    
    prior_dict = load_scrna_prior(prior_path)
    
    is_pdac_disc = (df_meta["group"] == "PDAC").values
    is_pdac_val = (df_meta_val["group"] == "PDAC").values
    
    pair_results = []
    
    for i in range(len(top_genes)):
        for j in range(i + 1, len(top_genes)):
            gene_a = top_genes[i]
            gene_b = top_genes[j]
            
            if gene_a not in df_expr_val.index or gene_b not in df_expr_val.index:
                continue
                
            # Min-Max Scaling [0, 1] relative to discovery range
            exp_a_disc = df_expr.loc[gene_a].values
            min_a = np.min(exp_a_disc)
            max_a = np.max(exp_a_disc)
            range_a = max_a - min_a
            norm_a_disc = (exp_a_disc - min_a) / range_a if range_a > 0 else np.zeros(len(exp_a_disc))
            
            exp_a_val = df_expr_val.loc[gene_a].values
            norm_a_val = (exp_a_val - min_a) / range_a if range_a > 0 else np.zeros(len(exp_a_val))
            
            exp_b_disc = df_expr.loc[gene_b].values
            min_b = np.min(exp_b_disc)
            max_b = np.max(exp_b_disc)
            range_b = max_b - min_b
            norm_b_disc = (exp_b_disc - min_b) / range_b if range_b > 0 else np.zeros(len(exp_b_disc))
            
            exp_b_val = df_expr_val.loc[gene_b].values
            norm_b_val = (exp_b_val - min_b) / range_b if range_b > 0 else np.zeros(len(exp_b_val))
            
            K_a = gene_to_thresh.get(gene_a, 0.5)
            K_b = gene_to_thresh.get(gene_b, 0.5)
            instab_a = gene_to_instab.get(gene_a, 0)
            instab_b = gene_to_instab.get(gene_b, 0)
            
            and_disc = (norm_a_disc > K_a) & (norm_b_disc > K_b)
            and_val = (norm_a_val > K_a) & (norm_b_val > K_b)
            
            sens_disc = np.mean(and_disc[is_pdac_disc])
            spec_disc = np.mean(~and_disc[~is_pdac_disc])
            sens_val = np.mean(and_val[is_pdac_val])
            spec_val = np.mean(~and_val[~is_pdac_val])
            
            tumor_corr, _ = spearmanr(exp_a_disc[is_pdac_disc], exp_b_disc[is_pdac_disc])
            if np.isnan(tumor_corr):
                tumor_corr = 0.0
                
            performance_score = np.mean([sens_disc, spec_disc, sens_val, spec_val])
            redundancy_penalty = alpha * np.abs(tumor_corr)
            mean_instab = np.mean([instab_a, instab_b])
            instability_penalty = beta * mean_instab
            
            # scRNA Score calculation
            target_coexpr, off_target_coexpr, scrna_score = calculate_scrna_score(gene_a, gene_b, prior_dict)
            
            pair_score = performance_score - redundancy_penalty - instability_penalty + (gamma * scrna_score)
            
            pair_results.append({
                "gene_A": gene_a,
                "gene_B": gene_b,
                "K_final_A": K_a,
                "K_final_B": K_b,
                "discovery_sensitivity": sens_disc,
                "discovery_specificity": spec_disc,
                "GSE62452_sensitivity": sens_val,
                "GSE62452_specificity": spec_val,
                "tumor_spearman_r": tumor_corr,
                "threshold_instability_A": instab_a,
                "threshold_instability_B": instab_b,
                "mean_threshold_instability": mean_instab,
                "target_coexpr_est": target_coexpr,
                "max_off_target_coexpr_est": off_target_coexpr,
                "scrna_score": scrna_score,
                "performance_score": performance_score,
                "redundancy_penalty": redundancy_penalty,
                "threshold_instability_penalty": instability_penalty,
                "pair_score": pair_score,
                "redundancy_category": classify_correlation(tumor_corr)
            })
            
    df_pairs = pd.DataFrame(pair_results)
    if len(df_pairs) > 0:
        df_pairs = df_pairs.sort_values(by="pair_score", ascending=False)
        
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df_pairs.to_csv(out_path, index=False)
        print(f"[+] Saved V4 pair search results to {out_path} (top pair: {df_pairs.iloc[0]['gene_A']} + {df_pairs.iloc[0]['gene_B']} with score {df_pairs.iloc[0]['pair_score']:.4f})")
        
    return df_pairs

if __name__ == "__main__":
    # Test script directly if needed
    pass
