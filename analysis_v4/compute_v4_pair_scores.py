#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V3_RESULTS_FILE = PROJECT_DIR / "results_v3/tables/pair_search_ensemble_threshold_top200.csv"
PRIOR_FILE = PROJECT_DIR / "analysis_v4/v4_scrna_gene_prior.csv"
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"

def load_scrna_prior():
    df = pd.read_csv(PRIOR_FILE)
    prior_dict = {}
    for _, row in df.iterrows():
        g = row['gene']
        ct = row['cell_type']
        pct = row['percent_expressing_fraction']
        if g not in prior_dict:
            prior_dict[g] = {}
        prior_dict[g][ct] = pct
    return prior_dict

def main():
    V4_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    print("[*] Loading V3 Top 200 pairs...")
    df_pairs = pd.read_csv(V3_RESULTS_FILE)
    print(f"[+] Loaded {len(df_pairs)} pairs.")
    
    print("[*] Loading scRNA prior...")
    prior_dict = load_scrna_prior()
    
    target_cts = ["malignant ductal / epithelial"]
    off_target_cts = [
        "CAF / fibroblast", "endothelial", 
        "Tregs", "CD8 T cells", "T cells", "B cells", 
        "macrophages / monocytes", "mast cells", 
        "normal acinar", "normal ductal"
    ]
    
    target_coexprs = []
    off_target_coexprs = []
    scrna_scores = []
    new_pair_scores = []
    
    GAMMA = 5.0  # Weight of the scRNA prior vs Bulk RNA-seq performance
    
    for _, row in df_pairs.iterrows():
        gene_a = row['gene_A']
        gene_b = row['gene_B']
        
        dict_a = prior_dict.get(gene_a, {})
        dict_b = prior_dict.get(gene_b, {})
        
        target_coexpr = 0
        for ct in target_cts:
            if ct in dict_a and ct in dict_b:
                target_coexpr = max(target_coexpr, min(dict_a[ct], dict_b[ct]))
                
        max_off_target = 0
        for ct in off_target_cts:
            if ct in dict_a and ct in dict_b:
                max_off_target = max(max_off_target, min(dict_a[ct], dict_b[ct]))
                
        # Target bonus and Off-target penalty
        # Since CAFs and Immune cells are highly confounding in bulk RNA-seq, heavily penalize off_target.
        scrna_score = target_coexpr - (5.0 * max_off_target)
        
        target_coexprs.append(target_coexpr)
        off_target_coexprs.append(max_off_target)
        scrna_scores.append(scrna_score)
        
        # New Pair Score
        bulk_perf = row['performance_score']
        red_pen = row['redundancy_penalty']
        inst_pen = row['threshold_instability_penalty']
        
        # We ensure scRNA score plays a strong decisive role
        final_score = bulk_perf - red_pen - inst_pen + (GAMMA * scrna_score)
        new_pair_scores.append(final_score)
        
    df_pairs['target_coexpr_est'] = target_coexprs
    df_pairs['max_off_target_coexpr_est'] = off_target_coexprs
    df_pairs['scrna_score'] = scrna_scores
    df_pairs['pair_score'] = new_pair_scores
    
    # Re-sort by new pair score
    df_pairs = df_pairs.sort_values(by="pair_score", ascending=False)
    
    out_path = V4_TABLES_DIR / "v4_pair_search_results.csv"
    df_pairs.to_csv(out_path, index=False)
    
    best_p = df_pairs.iloc[0]
    print(f"\n[!] V4 Final Selected Pair: {best_p['gene_A']} + {best_p['gene_B']}")
    print(f"    scRNA Score: {best_p['scrna_score']:.4f}")
    print(f"    Performance Score: {best_p['performance_score']:.4f}")
    print(f"    Target Coexpr: {best_p['target_coexpr_est']:.4f}")
    print(f"    Off-target max Coexpr: {best_p['max_off_target_coexpr_est']:.4f}")
    print(f"    New Pair Score: {best_p['pair_score']:.4f}")
    
    # Save the default pair summary
    pd.DataFrame([best_p]).to_csv(V4_TABLES_DIR / "v4_default_final_pair.csv", index=False)

if __name__ == "__main__":
    main()
