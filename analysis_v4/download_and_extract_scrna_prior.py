#!/usr/bin/env python3
import os
import urllib.request
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_DIR = PROJECT_DIR / "analysis_v4"
DOWNLOAD_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154778/suppl/GSE154778_dgeMtx.csv.gz"
TARGET_FILE = V4_DIR / "GSE154778_dgeMtx.csv.gz"

def main():
    V4_DIR.mkdir(parents=True, exist_ok=True)
    
    if not TARGET_FILE.exists():
        print(f"[*] Downloading {DOWNLOAD_URL} to {TARGET_FILE}...")
        try:
            def report_hook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    if block_num % 500 == 0:
                        print(f"[*] Downloaded: {downloaded / 1024**2:.2f} MB ({percent:.1f}%)")
            urllib.request.urlretrieve(DOWNLOAD_URL, TARGET_FILE, report_hook)
            print(f"[+] Download completed.")
        except Exception as e:
            print(f"[-] Download failed: {e}")
            import sys; sys.exit(1)
            
    print(f"[*] Loading scRNA expression matrix: {TARGET_FILE}")
    df = pd.read_csv(TARGET_FILE, index_col=0)
    print(f"[+] Loaded matrix of shape: {df.shape}")

    # Top 200 consensus genes
    V3_CONSENSUS_FILE = PROJECT_DIR / "results_v3/tables/model_consensus_feature_ranking_v3.csv"
    df_consensus = pd.read_csv(V3_CONSENSUS_FILE)
    top_genes = df_consensus["gene"].head(200).tolist()
    
    # We also need marker genes for cell-type classification!
    marker_genes = [
        "EPCAM", "KRT19", "SOX9", "CEACAM5", "MUC1", "CFTR",
        "PRSS1", "CPA1", "REG1A", "AMY2A", "COL1A1", "COL1A2", 
        "DCN", "LUM", "ACTA2", "FAP", "PECAM1", "VWF", "KDR",
        "CD3D", "CD3E", "CD2", "CD8A", "CD8B", "FOXP3", "IL2RA", 
        "CTLA4", "MS4A1", "CD79A", "LST1", "CD68", "CD14", "FCGR3A", 
        "C1QA", "TPSAB1", "CPA3"
    ]
    all_needed = list(set(top_genes + marker_genes))
    
    # Filter rows to only needed genes before transposing to save memory
    available_genes = [g for g in all_needed if g in df.index]
    df = df.loc[available_genes]
    
    print("[*] Initializing AnnData object...")
    adata = ad.AnnData(df.T)
    print(f"[+] AnnData shape: {adata.shape}")

    sc.pp.filter_cells(adata, min_genes=50) # lower threshold since we heavily filtered genes
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Classify cells
    def get_valid_markers(gene_list):
        return [g for g in gene_list if g in adata.var_names]

    marker_defs = {
        "malignant_ductal": get_valid_markers(["EPCAM", "KRT19", "SOX9", "CEACAM5", "MUC1"]),
        "normal_ductal": get_valid_markers(["EPCAM", "KRT19", "CFTR"]),
        "acinar": get_valid_markers(["PRSS1", "CPA1", "REG1A", "AMY2A"]),
        "fibroblast": get_valid_markers(["COL1A1", "COL1A2", "DCN", "LUM", "ACTA2", "FAP"]),
        "endothelial": get_valid_markers(["PECAM1", "VWF", "KDR"]),
        "t_cells": get_valid_markers(["CD3D", "CD3E", "CD2"]),
        "cd8_t_cells": get_valid_markers(["CD8A", "CD8B"]),
        "tregs": get_valid_markers(["FOXP3", "IL2RA", "CTLA4"]),
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
        epi_score = max(row["malignant_ductal"], row["normal_ductal"], row["acinar"])
        
        max_cat = np.argmax([immune_score, stromal_score, epi_score])
        
        if max_cat == 0:
            sub_cat = np.argmax([row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"]])
            if sub_cat == 0:
                if row["tregs"] > row["cd8_t_cells"] and row["tregs"] > 0.5:
                    cell_types.append("Tregs")
                elif row["cd8_t_cells"] > 0.5:
                    cell_types.append("CD8 T cells")
                else:
                    cell_types.append("T cells")
            elif sub_cat == 1:
                cell_types.append("B cells")
            elif sub_cat == 2:
                cell_types.append("macrophages / monocytes")
            else:
                cell_types.append("mast cells")
        elif max_cat == 1:
            sub_cat = np.argmax([row["fibroblast"], row["endothelial"]])
            if sub_cat == 0:
                cell_types.append("CAF / fibroblast")
            else:
                cell_types.append("endothelial")
        else:
            sub_cat = np.argmax([row["malignant_ductal"], row["normal_ductal"], row["acinar"]])
            if sub_cat == 2:
                cell_types.append("normal acinar")
            else:
                ceacam5_loc = adata.var_names.get_loc("CEACAM5") if "CEACAM5" in adata.var_names else -1
                if ceacam5_loc != -1:
                    val = adata.X[adata.obs_names.get_loc(idx), ceacam5_loc]
                    if not isinstance(val, (float, np.float32, np.float64)):
                        val = val.toarray()[0, 0]
                    if val > 0.2:
                        cell_types.append("malignant ductal / epithelial")
                    else:
                        cell_types.append("normal ductal")
                else:
                    cell_types.append("normal ductal")

    adata.obs['cell_type'] = cell_types

    # Compute percent expressing for top 200 genes
    print("[*] Computing cell-type percent expressing...")
    summary_records = []
    cts = sorted(adata.obs['cell_type'].unique())
    
    expr_dict = {}
    for g in top_genes:
        if g not in adata.var_names:
            expr_dict[g] = np.zeros(adata.n_obs)
            continue
        loc = adata.var_names.get_loc(g)
        col = adata.X[:, loc]
        expr_dict[g] = col.flatten() if isinstance(col, np.ndarray) else np.array(col.toarray()).flatten()
        
    for ct in cts:
        mask = adata.obs['cell_type'] == ct
        n_cells_sub = np.sum(mask)
        if n_cells_sub == 0: continue
            
        for g in top_genes:
            g_expr = expr_dict[g][mask]
            pct = np.mean(g_expr > 0)
            mean_e = np.mean(g_expr) if len(g_expr) > 0 else 0.0
            
            summary_records.append({
                "cell_type": ct,
                "gene": g,
                "mean_expression": mean_e,
                "percent_expressing_fraction": pct,
                "n_cells": n_cells_sub
            })
            
    df_prior = pd.DataFrame(summary_records)
    out_file = V4_DIR / "v4_scrna_gene_prior.csv"
    df_prior.to_csv(out_file, index=False)
    print(f"[+] Wrote scRNA prior to {out_file}")

if __name__ == "__main__":
    main()
