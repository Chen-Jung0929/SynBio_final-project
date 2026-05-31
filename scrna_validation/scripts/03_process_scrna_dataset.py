#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_RAW_DIR = PROJECT_DIR / "scrna_validation/data/raw"
DATA_PROCESSED_DIR = PROJECT_DIR / "scrna_validation/data/processed"
TABLES_DIR = PROJECT_DIR / "scrna_validation/tables"
FIGURES_DIR = PROJECT_DIR / "scrna_validation/figures"

def main():
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = DATA_RAW_DIR / "GSE154778_dgeMtx.csv.gz"
    print(f"[*] Loading single-cell expression matrix: {raw_path}")
    df = pd.read_csv(raw_path, index_col=0)
    print(f"[+] Loaded matrix of shape: {df.shape} (genes x cells)")

    # Convert to AnnData: scanpy expects cells as rows, genes as columns
    print("[*] Initializing AnnData object...")
    adata = ad.AnnData(df.T)
    print(f"[+] AnnData shape: {adata.shape}")

    # Log initial QC numbers
    cells_before = adata.n_obs
    genes_before = adata.n_vars

    # QC filtering
    print("[*] Running basic QC filtering...")
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)
    
    # Calculate QC metrics
    adata.obs['n_genes_by_counts'] = (adata.X > 0).sum(axis=1)
    adata.obs['total_counts'] = adata.X.sum(axis=1)
    
    # Check for mitochondrial genes
    mito_genes = adata.var_names.str.startswith('MT-') | adata.var_names.str.startswith('mt-')
    adata.obs['pct_mito'] = np.sum(adata.X[:, mito_genes], axis=1) / adata.obs['total_counts'] * 100 if np.sum(mito_genes) > 0 else 0.0

    # Save QC summaries
    qc_summary = pd.DataFrame({
        "Metric": [
            "Cells before QC", "Genes before QC", 
            "Cells after QC", "Genes after QC", 
            "Mean genes per cell", "Mean counts per cell"
        ],
        "Value": [
            cells_before, genes_before, 
            adata.n_obs, adata.n_vars, 
            adata.obs['n_genes_by_counts'].mean(), adata.obs['total_counts'].mean()
        ]
    })
    qc_summary.to_csv(TABLES_DIR / "scrna_qc_summary.csv", index=False)
    print("[+] Wrote QC summary to tables/scrna_qc_summary.csv")

    # Generate QC violin plot
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.violinplot(data=adata.obs, y='n_genes_by_counts', ax=axes[0], color='#1F77B4')
    axes[0].set_title('Genes per Cell')
    axes[0].set_ylabel('Number of Genes')
    
    sns.violinplot(data=adata.obs, y='total_counts', ax=axes[1], color='#D62728')
    axes[1].set_title('Counts per Cell')
    axes[1].set_ylabel('Total Counts')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_qc_violin.png", dpi=300)
    plt.close()
    print("[+] Saved QC violin plot to figures/scrna_qc_violin.png")

    # Normalize counts
    print("[*] Normalizing data to 10k target sum and log-transforming...")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    # Match genes of interest
    query_genes = ["CEACAM5", "CST1", "UBE2S", "CCR6"]
    matched_records = []
    print("[*] Verifying gene presence in the dataset:")
    for qg in query_genes:
        present = qg in adata.var_names
        matched_records.append({
            "query_gene": qg,
            "matched_gene": qg if present else "None",
            "present_yes_no": "yes" if present else "no",
            "gene_symbol_source": "HGNC" if present else "None",
            "notes": "Found in expression matrix" if present else "Absent from expression matrix"
        })
        print(f"  - {qg}: {'Found' if present else 'NOT found'}")
        
    df_presence = pd.DataFrame(matched_records)
    df_presence.to_csv(TABLES_DIR / "gene_presence_check.csv", index=False)
    print("[+] Saved gene presence check to tables/gene_presence_check.csv")

    # Save dataset summary
    # Extract patient/sample ID from cell barcode prefix (e.g., 'P03:1' -> 'P03')
    adata.obs['patient_id'] = [x.split(":")[0] for x in adata.obs_names]
    adata.obs['is_tumor'] = [x.startswith('P') or x.startswith('MET') for x in adata.obs['patient_id']]

    # Define marker genes present in adata
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

    # Annotate cells individually based on max marker score
    print("[*] Classifying cells based on marker gene signatures...")
    scores = {}
    for ct, m_list in marker_defs.items():
        if len(m_list) > 0:
            # Mean log-normalized expression of valid markers for each cell
            # Scanpy uses scipy csr matrix for X, let's extract slice safely
            gene_indices = [adata.var_names.get_loc(g) for g in m_list]
            expr_slice = adata.X[:, gene_indices]
            if isinstance(expr_slice, np.ndarray):
                scores[ct] = expr_slice.mean(axis=1)
            else:
                scores[ct] = np.array(expr_slice.mean(axis=1)).flatten()
        else:
            scores[ct] = np.zeros(adata.n_obs)

    df_scores = pd.DataFrame(scores, index=adata.obs_names)
    
    # Apply hierarchical rules to define cell types
    cell_types = []
    for idx, row in df_scores.iterrows():
        # Identify broad categories first
        immune_score = max(row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"])
        stromal_score = max(row["fibroblast"], row["endothelial"])
        epi_score = max(row["malignant_ductal"], row["normal_ductal"], row["acinar"])
        
        max_cat = np.argmax([immune_score, stromal_score, epi_score])
        
        if max_cat == 0:  # Immune
            sub_cat = np.argmax([row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"]])
            if sub_cat == 0:
                # T cell subtype check
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
                
        elif max_cat == 1:  # Stromal
            sub_cat = np.argmax([row["fibroblast"], row["endothelial"]])
            if sub_cat == 0:
                cell_types.append("CAF / fibroblast")
            else:
                cell_types.append("endothelial")
                
        else:  # Epithelial
            # Distinguish malignant ductal, normal ductal, acinar
            sub_cat = np.argmax([row["malignant_ductal"], row["normal_ductal"], row["acinar"]])
            if sub_cat == 2:
                cell_types.append("normal acinar")
            else:
                # Check CEACAM5 expression to determine malignancy status in ductal cells
                ceacam5_loc = adata.var_names.get_loc("CEACAM5") if "CEACAM5" in adata.var_names else -1
                if ceacam5_loc != -1:
                    val = adata.X[adata.obs_names.get_loc(idx), ceacam5_loc]
                    # if X is a sparse matrix, extract value
                    if not isinstance(val, (float, np.float32, np.float64)):
                        val = val.toarray()[0, 0]
                    
                    if val > 0.2:  # express cancer marker
                        cell_types.append("malignant ductal / epithelial")
                    else:
                        cell_types.append("normal ductal")
                else:
                    cell_types.append("normal ductal")

    adata.obs['cell_type'] = cell_types
    print("[+] Cell classification counts:")
    print(adata.obs['cell_type'].value_counts())

    # Save dataset summary
    n_patients = len(adata.obs['patient_id'].unique())
    n_tumor_cells = np.sum(adata.obs['cell_type'] == 'malignant ductal / epithelial')
    n_normal_cells = np.sum(adata.obs['cell_type'] != 'malignant ductal / epithelial')
    
    df_summary = pd.DataFrame({
        "dataset_id": ["GSE154778 / Lin et al. 2020"],
        "n_cells": [adata.n_obs],
        "n_genes": [adata.n_vars],
        "n_patients": [n_patients],
        "n_tumor_cells": [n_tumor_cells],
        "n_normal_cells": [n_normal_cells],
        "available_cell_type_column": ["cell_type (marker-inferred)"],
        "normalization_used": ["sc.pp.normalize_total(target_sum=1e4), log1p"],
        "notes": [f"Contains patient samples: {sorted(list(adata.obs['patient_id'].unique()))}"]
    })
    df_summary.to_csv(TABLES_DIR / "scrna_dataset_summary.csv", index=False)
    print("[+] Wrote summary to tables/scrna_dataset_summary.csv")

    # Save processed AnnData
    out_path = DATA_PROCESSED_DIR / "pdac_processed.h5ad"
    print(f"[*] Saving processed AnnData to {out_path}...")
    adata.write(out_path)
    print("[+] Saved successfully!")

if __name__ == "__main__":
    main()
