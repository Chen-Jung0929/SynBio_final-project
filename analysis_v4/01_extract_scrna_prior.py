#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import scanpy as sc
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.resolve()
DATA_PROCESSED_DIR = PROJECT_DIR / "scrna_validation_independent/data/processed"
V3_CONSENSUS_FILE = PROJECT_DIR / "results_v3/tables/model_consensus_feature_ranking_v3.csv"
V4_DIR = PROJECT_DIR / "analysis_v4"

def get_expr_array(adata, gene_name):
    if gene_name not in adata.var_names:
        return np.zeros(adata.n_obs)
    loc = adata.var_names.get_loc(gene_name)
    col = adata.X[:, loc]
    if isinstance(col, np.ndarray):
        return col.flatten()
    return np.array(col.toarray()).flatten()

def main():
    V4_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load consensus genes (Top 200)
    print(f"[*] Reading consensus genes from {V3_CONSENSUS_FILE}")
    df_consensus = pd.read_csv(V3_CONSENSUS_FILE)
    top_genes = df_consensus["gene"].head(200).tolist()
    print(f"[+] Loaded {len(top_genes)} top consensus genes.")

    # 2. Load scRNA data
    h5ad_path = DATA_PROCESSED_DIR / "pdac_processed.h5ad"
    if not h5ad_path.exists():
        print(f"[-] ERROR: processed AnnData not found at {h5ad_path}")
        return
        
    print(f"[*] Reading processed AnnData: {h5ad_path}")
    adata = sc.read_h5ad(h5ad_path)
    print(f"[+] Loaded processed AnnData of shape: {adata.shape}")

    # 3. Compute cell-type expression statistics
    print("[*] Computing cell-type percent expressing...")
    summary_records = []
    cell_types = sorted(adata.obs['cell_type'].unique())
    
    # Pre-extract all gene expressions to avoid repeated lookups if possible
    expr_dict = {}
    for g in top_genes:
        expr_dict[g] = get_expr_array(adata, g)
        
    for ct in cell_types:
        mask = adata.obs['cell_type'] == ct
        n_cells_sub = np.sum(mask)
        if n_cells_sub == 0:
            continue
            
        for g in top_genes:
            g_expr = expr_dict[g][mask]
            pct_expressing = np.mean(g_expr > 0)
            mean_expr = np.mean(g_expr) if len(g_expr) > 0 else 0.0
            
            summary_records.append({
                "cell_type": ct,
                "gene": g,
                "mean_expression": mean_expr,
                "percent_expressing_fraction": pct_expressing,
                "n_cells": n_cells_sub
            })
            
    df_expr_summary = pd.DataFrame(summary_records)
    out_file = V4_DIR / "v4_scrna_gene_prior.csv"
    df_expr_summary.to_csv(out_file, index=False)
    print(f"[+] Wrote scRNA gene expression prior to {out_file}")

if __name__ == "__main__":
    main()
