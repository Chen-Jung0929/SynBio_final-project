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
        is_target = row['is_target_compartment'] == 1
        
        if g not in prior_dict:
            prior_dict[g] = {}
        prior_dict[g][ct] = {
            'pct': pct,
            'is_target': is_target
        }
    return prior_dict

def main():
    V4_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    print("[*] Loading V3 Top 200 pairs...")
    df_pairs = pd.read_csv(V3_RESULTS_FILE)
    print(f"[+] Loaded {len(df_pairs)} pairs.")
    
    print("[*] Loading unbiased scRNA prior...")
    prior_dict = load_scrna_prior()
    
    target_coexprs = []
    off_target_coexprs = []
    max_off_target_ct = []
    scrna_scores = []
    new_pair_scores = []
    
    GAMMA = 5.0  # scRNA weighting
    
    for _, row in df_pairs.iterrows():
        gene_a = row['gene_A']
        gene_b = row['gene_B']
        
        dict_a = prior_dict.get(gene_a, {})
        dict_b = prior_dict.get(gene_b, {})
        
        target_coexpr = 0.0
        max_off_target = 0.0
        max_off_ct_name = "None"
        
        # Iterate through cell types to compute coexpr
        common_cts = set(dict_a.keys()).intersection(set(dict_b.keys()))
        for ct in common_cts:
            coexpr = min(dict_a[ct]['pct'], dict_b[ct]['pct'])
            
            if dict_a[ct]['is_target']:
                # For our updated annotations, there is only one target compartment.
                if coexpr > target_coexpr:
                    target_coexpr = coexpr
            else:
                if coexpr > max_off_target:
                    max_off_target = coexpr
                    max_off_ct_name = ct
                
        scrna_score = target_coexpr - (GAMMA * max_off_target)
        
        target_coexprs.append(target_coexpr)
        off_target_coexprs.append(max_off_target)
        max_off_target_ct.append(max_off_ct_name)
        scrna_scores.append(scrna_score)
        
        # New Pair Score
        bulk_perf = row['performance_score']
        red_pen = row['redundancy_penalty']
        inst_pen = row['threshold_instability_penalty']
        
        final_score = bulk_perf - red_pen - inst_pen + (GAMMA * scrna_score)
        
        # STRICT BIOLOGICAL REQUIREMENT:
        # A biosensor must activate in the tumor. If target co-expression is < 10%, 
        # it is physically useless regardless of how mathematically stable it is in bulk.
        if target_coexpr < 0.10:
            final_score = -999.0
            
        new_pair_scores.append(final_score)
        
    df_pairs['target_coexpr_est'] = target_coexprs
    df_pairs['max_off_target_coexpr_est'] = off_target_coexprs
    df_pairs['max_off_target_compartment'] = max_off_target_ct
    df_pairs['scrna_score'] = scrna_scores
    df_pairs['pair_score'] = new_pair_scores
    
    # Re-sort by new pair score
    df_pairs = df_pairs.sort_values(by="pair_score", ascending=False)
    
    out_path = V4_TABLES_DIR / "v4_pair_search_results.csv"
    df_pairs.to_csv(out_path, index=False)
    
    best_p = df_pairs.iloc[0]
    print(f"\n[!] V4 Final Unbiased Selected Pair: {best_p['gene_A']} + {best_p['gene_B']}")
    print(f"    scRNA Score: {best_p['scrna_score']:.4f}")
    print(f"    Performance Score: {best_p['performance_score']:.4f}")
    print(f"    Target Coexpr: {best_p['target_coexpr_est']:.4f}")
    print(f"    Off-target max Coexpr: {best_p['max_off_target_coexpr_est']:.4f} ({best_p['max_off_target_compartment']})")
    print(f"    New Pair Score: {best_p['pair_score']:.4f}")
    
    pd.DataFrame([best_p]).to_csv(V4_TABLES_DIR / "v4_default_final_pair.csv", index=False)

if __name__ == "__main__":
    main()
