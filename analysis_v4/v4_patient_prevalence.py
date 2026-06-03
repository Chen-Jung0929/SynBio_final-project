#!/usr/bin/env python3
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_DIR = PROJECT_DIR / "analysis_v4"
TARGET_FILE = V4_DIR / "GSE154778_dgeMtx.csv.gz"
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"

def main():
    print("[*] Loading V4 final pair...")
    df_pair = pd.read_csv(V4_TABLES_DIR / "v4_default_final_pair.csv")
    gene_a = df_pair.iloc[0]['gene_A']
    gene_b = df_pair.iloc[0]['gene_B']
    
    print(f"[*] Target Pair: {gene_a} + {gene_b}")
    
    print(f"[*] Loading scRNA expression matrix: {TARGET_FILE}")
    df = pd.read_csv(TARGET_FILE, index_col=0)
    
    # We need the markers and the pair genes
    marker_genes = [
        "EPCAM", "KRT19", "SOX9", "CFTR",
        "PRSS1", "CPA1", "REG1A", "AMY2A", "COL1A1", "COL1A2", 
        "DCN", "LUM", "ACTA2", "FAP", "PECAM1", "VWF", "KDR",
        "CD3D", "CD3E", "CD2", "CD8A", "CD8B", "FOXP3", "IL2RA", 
        "CTLA4", "MS4A1", "CD79A", "LST1", "CD68", "CD14", "FCGR3A", 
        "C1QA", "TPSAB1", "CPA3"
    ]
    all_needed = list(set([gene_a, gene_b] + marker_genes))
    available_genes = [g for g in all_needed if g in df.index]
    df = df.loc[available_genes]
    
    adata = ad.AnnData(df.T)
    sc.pp.filter_cells(adata, min_genes=50)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Extract patient/sample ID
    adata.obs['patient_id'] = [x.split(":")[0] for x in adata.obs_names]
    adata.obs['is_tumor'] = [x.startswith('P') or x.startswith('MET') for x in adata.obs['patient_id']]

    def get_valid_markers(gene_list):
        return [g for g in gene_list if g in adata.var_names]

    marker_defs = {
        "ductal": get_valid_markers(["EPCAM", "KRT19", "SOX9", "CFTR"]),
        "acinar": get_valid_markers(["PRSS1", "CPA1", "REG1A", "AMY2A"]),
        "fibroblast": get_valid_markers(["COL1A1", "COL1A2", "DCN", "LUM", "ACTA2", "FAP"]),
        "endothelial": get_valid_markers(["PECAM1", "VWF", "KDR"]),
        "t_cells": get_valid_markers(["CD3D", "CD3E", "CD2"]),
        "b_cells": get_valid_markers(["MS4A1", "CD79A"]),
        "macrophages": get_valid_markers(["LST1", "CD68", "CD14", "FCGR3A", "C1QA"]),
        "mast_cells": get_valid_markers(["TPSAB1", "CPA3"])
    }

    scores = {}
    for ct, m_list in marker_defs.items():
        if len(m_list) > 0:
            gene_indices = [adata.var_names.get_loc(g) for g in m_list]
            expr_slice = adata.X[:, gene_indices]
            if isinstance(expr_slice, np.ndarray):
                scores[ct] = expr_slice.mean(axis=1)
            else:
                scores[ct] = np.array(expr_slice.mean(axis=1)).flatten()
        else:
            scores[ct] = np.zeros(adata.n_obs)

    df_scores = pd.DataFrame(scores, index=adata.obs_names)
    
    cell_types = []
    for idx, row in df_scores.iterrows():
        immune_score = max(row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"])
        stromal_score = max(row["fibroblast"], row["endothelial"])
        epi_score = max(row["ductal"], row["acinar"])
        
        max_cat = np.argmax([immune_score, stromal_score, epi_score])
        
        if max_cat == 2:
            sub_cat = np.argmax([row["ductal"], row["acinar"]])
            if sub_cat == 0:
                is_tumor = adata.obs.loc[idx, 'is_tumor']
                if is_tumor:
                    cell_types.append("malignant ductal / epithelial")
                    continue
        cell_types.append("other")
        
    adata.obs['cell_type'] = cell_types
    
    # Filter for target compartment
    target_adata = adata[adata.obs['cell_type'] == "malignant ductal / epithelial"].copy()
    
    records = []
    for patient in target_adata.obs['patient_id'].unique():
        p_adata = target_adata[target_adata.obs['patient_id'] == patient]
        
        a_expr = p_adata[:, gene_a].X
        if not isinstance(a_expr, np.ndarray): a_expr = a_expr.toarray()
        a_pct = np.mean(a_expr > 0)
        
        b_expr = p_adata[:, gene_b].X
        if not isinstance(b_expr, np.ndarray): b_expr = b_expr.toarray()
        b_pct = np.mean(b_expr > 0)
        
        both_pct = np.mean((a_expr > 0) & (b_expr > 0))
        
        records.append({
            "patient_id": patient,
            "n_target_cells": p_adata.n_obs,
            f"{gene_a}_percent_expressing": a_pct,
            f"{gene_b}_percent_expressing": b_pct,
            "pair_coexpressing_percent": both_pct,
            "patient_is_positive": 1 if both_pct > 0.05 else 0 # 5% threshold
        })
        
    df_prev = pd.DataFrame(records)
    out_path = V4_TABLES_DIR / "v4_patient_prevalence_summary.csv"
    if not df_prev.empty:
        df_prev.to_csv(out_path, index=False)
        pos_rate = df_prev['patient_is_positive'].mean() * 100
        print(f"\n[+] Patient prevalence for {gene_a}+{gene_b}: {pos_rate:.1f}%")
    else:
        # Create a dummy row to avoid pipeline crash
        pd.DataFrame([{"patient_is_positive": 0.0}]).to_csv(out_path, index=False)
        pos_rate = 0.0
        print(f"\n[-] No target cells found. Patient prevalence: 0.0%")
    print(f"[+] Wrote prevalence summary to {out_path}")

if __name__ == "__main__":
    main()
