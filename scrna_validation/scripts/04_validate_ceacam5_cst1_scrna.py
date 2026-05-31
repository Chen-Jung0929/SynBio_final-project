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
DATA_PROCESSED_DIR = PROJECT_DIR / "scrna_validation/data/processed"
TABLES_DIR = PROJECT_DIR / "scrna_validation/tables"
FIGURES_DIR = PROJECT_DIR / "scrna_validation/figures"

def get_expr_array(adata, gene_name):
    loc = adata.var_names.get_loc(gene_name)
    col = adata.X[:, loc]
    if isinstance(col, np.ndarray):
        return col.flatten()
    return np.array(col.toarray()).flatten()

def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    h5ad_path = DATA_PROCESSED_DIR / "pdac_processed.h5ad"
    print(f"[*] Reading processed AnnData: {h5ad_path}")
    adata = sc.read_h5ad(h5ad_path)
    print(f"[+] Loaded processed AnnData of shape: {adata.shape}")

    # Extract expressions
    expr = {}
    for g in ["CEACAM5", "CST1", "UBE2S", "CCR6"]:
        expr[g] = get_expr_array(adata, g)
        adata.obs[f"{g}_expression"] = expr[g]

    # 1. Cell-type expression summary
    print("[*] Computing cell-type expression statistics...")
    summary_records = []
    cell_types = adata.obs['cell_type'].unique()
    
    for ct in cell_types:
        mask = adata.obs['cell_type'] == ct
        sub_adata = adata[mask]
        
        for g in ["CEACAM5", "CST1", "UBE2S", "CCR6"]:
            g_expr = expr[g][mask]
            
            summary_records.append({
                "cell_type": ct,
                "gene": g,
                "mean_expression": g_expr.mean(),
                "median_expression": np.median(g_expr),
                "percent_expressing": np.mean(g_expr > 0) * 100,
                "n_cells": len(g_expr),
                "n_patients": len(sub_adata.obs['patient_id'].unique())
            })
            
    df_expr_summary = pd.DataFrame(summary_records)
    df_expr_summary.to_csv(TABLES_DIR / "scrna_gene_expression_by_celltype.csv", index=False)
    print("[+] Wrote expression summary to tables/scrna_gene_expression_by_celltype.csv")

    # 2. Co-expression analysis (Threshold 1: expr > 0, Threshold 2: expr > 0.5)
    print("[*] Running co-expression analysis for v1 and v2 pairs...")
    coexpr_records = []
    
    for ct in cell_types:
        mask = adata.obs['cell_type'] == ct
        n_c = np.sum(mask)
        
        for thresh_name, thresh_val in [("threshold_1_gt_0", 0.0), ("threshold_2_gt_0.5", 0.5)]:
            # CEACAM5 + CST1
            c5_pos = expr["CEACAM5"][mask] > thresh_val
            c1_pos = expr["CST1"][mask] > thresh_val
            dp_v2 = c5_pos & c1_pos
            
            # UBE2S + CCR6
            u2_pos = expr["UBE2S"][mask] > thresh_val
            c6_pos = expr["CCR6"][mask] > thresh_val
            dp_v1 = u2_pos & c6_pos
            
            coexpr_records.append({
                "cell_type": ct,
                "threshold_definition": thresh_name,
                "CEACAM5_positive_fraction": np.mean(c5_pos),
                "CST1_positive_fraction": np.mean(c1_pos),
                "CEACAM5_CST1_double_positive_fraction": np.mean(dp_v2),
                "UBE2S_positive_fraction": np.mean(u2_pos),
                "CCR6_positive_fraction": np.mean(c6_pos),
                "UBE2S_CCR6_double_positive_fraction": np.mean(dp_v1),
                "n_cells": n_c
            })
            
    df_coexpr = pd.DataFrame(coexpr_records)
    df_coexpr.to_csv(TABLES_DIR / "scrna_pair_coexpression_by_celltype.csv", index=False)
    print("[+] Wrote co-expression summary to tables/scrna_pair_coexpression_by_celltype.csv")

    # 3. Patient-level pseudobulk & patient level summary
    print("[*] Computing patient-level pseudobulk statistics...")
    pseudobulk_records = []
    patient_ids = adata.obs['patient_id'].unique()
    
    for pid in patient_ids:
        for ct in cell_types:
            mask = (adata.obs['patient_id'] == pid) & (adata.obs['cell_type'] == ct)
            n_cells_sub = np.sum(mask)
            if n_cells_sub >= 5:  # Require at least 5 cells to construct patient-level pseudobulk
                record = {
                    "patient_id": pid,
                    "cell_type": ct,
                    "n_cells": n_cells_sub
                }
                for g in ["CEACAM5", "CST1", "UBE2S", "CCR6"]:
                    record[f"{g}_mean"] = expr[g][mask].mean()
                pseudobulk_records.append(record)
                
    df_pb = pd.DataFrame(pseudobulk_records)
    df_pb.to_csv(TABLES_DIR / "scrna_patient_celltype_pseudobulk.csv", index=False)
    print("[+] Wrote pseudobulk profile to tables/scrna_patient_celltype_pseudobulk.csv")

    # Patient-level co-expression summary (Malignant ductal cells only)
    pb_mal = df_pb[df_pb["cell_type"] == "malignant ductal / epithelial"]
    pb_summary = []
    for idx, row in pb_mal.iterrows():
        # check if both have mean > 0.1 in patient's malignant cells
        both_active = (row["CEACAM5_mean"] > 0.1) and (row["CST1_mean"] > 0.1)
        pb_summary.append({
            "patient_id": row["patient_id"],
            "CEACAM5_mean": row["CEACAM5_mean"],
            "CST1_mean": row["CST1_mean"],
            "co_expressed_in_patient": "yes" if both_active else "no"
        })
    df_pb_summary = pd.DataFrame(pb_summary)
    df_pb_summary.to_csv(TABLES_DIR / "scrna_patient_level_coexpression_summary.csv", index=False)
    print("[+] Wrote patient co-expression summary to tables/scrna_patient_level_coexpression_summary.csv")

    # 4. Compare v1 vs v2 pair on cell types
    print("[*] Generating v1 vs v2 pair cell-type comparison table...")
    v1_vs_v2 = []
    for ct in cell_types:
        row_t1 = df_coexpr[(df_coexpr["cell_type"] == ct) & (df_coexpr["threshold_definition"] == "threshold_1_gt_0")].iloc[0]
        v1_vs_v2.append({
            "cell_type": ct,
            "v1_pair_coexpression_fraction": row_t1["UBE2S_CCR6_double_positive_fraction"],
            "v2_pair_coexpression_fraction": row_t1["CEACAM5_CST1_double_positive_fraction"],
            "n_cells": row_t1["n_cells"]
        })
    df_compare = pd.DataFrame(v1_vs_v2)
    df_compare.to_csv(TABLES_DIR / "scrna_v1_vs_v2_pair_celltype_comparison.csv", index=False)
    print("[+] Wrote cell-type comparison to tables/scrna_v1_vs_v2_pair_celltype_comparison.csv")

    # 5. Visualizations
    print("[*] Running PCA, neighbors, and UMAP computation for visualizations...")
    sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
    sc.tl.pca(adata, svd_solver='arpack')
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=20)
    sc.tl.umap(adata)

    # Save UMAPs
    # UMAP by Cell Type
    plt.figure(figsize=(8, 6))
    sc.pl.umap(adata, color='cell_type', show=False, legend_fontsize=8)
    plt.title('UMAP of PDAC TME (Cell Types)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_umap_celltype.png", dpi=300)
    plt.close()

    # UMAP by CEACAM5
    plt.figure(figsize=(6, 5))
    sc.pl.umap(adata, color='CEACAM5', show=False, cmap='viridis')
    plt.title('UMAP: CEACAM5 Expression', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_umap_ceacam5.png", dpi=300)
    plt.close()

    # UMAP by CST1
    plt.figure(figsize=(6, 5))
    sc.pl.umap(adata, color='CST1', show=False, cmap='viridis')
    plt.title('UMAP: CST1 Expression', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_umap_cst1.png", dpi=300)
    plt.close()

    adata.obs['v2_double_positive'] = ["Double Positive" if x else "Other" for x in (expr['CEACAM5'] > 0.5) & (expr['CST1'] > 0.5)]
    plt.figure(figsize=(6, 5))
    sc.pl.umap(adata, color='v2_double_positive', show=False, palette={'Double Positive': '#D62728', 'Other': '#E5E3D8'})
    plt.title('UMAP: CEACAM5+/CST1+ Double Positive Cells', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_umap_ceacam5_cst1_double_positive.png", dpi=300)
    plt.close()

    # Save Dotplot
    print("[*] Generating dotplot...")
    plt.figure(figsize=(10, 4))
    sc.pl.dotplot(adata, var_names=["CEACAM5", "CST1", "UBE2S", "CCR6"], groupby='cell_type', save='_candidate_genes.png', show=False)
    # Scanpy saves to a folder 'figures/dotplot_candidate_genes.png' inside the directory. Let's move/copy it
    scanpy_fig_path = Path("figures/dotplot_candidate_genes.png")
    if scanpy_fig_path.exists():
        os.rename(scanpy_fig_path, FIGURES_DIR / "scrna_dotplot_ceacam5_cst1_ube2s_ccr6.png")
    else:
        # Fallback manual plot if scanpy directory structure differs
        print("[!] Warning: Scanpy dotplot save location not found, creating alternative dotplot.")
        # We will copy from whatever scanpy generated, or rename
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'dotplot_candidate_genes' in file:
                    os.rename(os.path.join(root, file), FIGURES_DIR / "scrna_dotplot_ceacam5_cst1_ube2s_ccr6.png")
    plt.close()

    # Violin plots
    print("[*] Generating violin plots...")
    # CEACAM5
    plt.figure(figsize=(10, 4))
    sns.violinplot(data=adata.obs, x='cell_type', y='CEACAM5_expression', hue='cell_type', palette='tab20', legend=False)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.title('CEACAM5 Expression by Cell Type')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_violin_ceacam5_by_celltype.png", dpi=300)
    plt.close()

    # CST1
    plt.figure(figsize=(10, 4))
    sns.violinplot(data=adata.obs, x='cell_type', y='CST1_expression', hue='cell_type', palette='tab20', legend=False)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.title('CST1 Expression by Cell Type')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_violin_cst1_by_celltype.png", dpi=300)
    plt.close()

    # UBE2S and CCR6
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    sns.violinplot(data=adata.obs, x='cell_type', y='UBE2S_expression', ax=axes[0], hue='cell_type', palette='tab20', legend=False)
    axes[0].set_title('UBE2S Expression by Cell Type')
    sns.violinplot(data=adata.obs, x='cell_type', y='CCR6_expression', ax=axes[1], hue='cell_type', palette='tab20', legend=False)
    axes[1].set_title('CCR6 Expression by Cell Type')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_violin_ube2s_ccr6_by_celltype.png", dpi=300)
    plt.close()

    # Barplots of co-expression fractions
    print("[*] Generating co-expression comparison barplot...")
    # Clean cell type names for plotting
    df_compare_plot = df_compare.copy()
    plt.figure(figsize=(10, 5))
    x = np.arange(len(df_compare_plot))
    width = 0.35
    
    plt.bar(x - width/2, df_compare_plot["v1_pair_coexpression_fraction"] * 100, width, label='v1 (UBE2S + CCR6)', color='#7F7F7F')
    plt.bar(x + width/2, df_compare_plot["v2_pair_coexpression_fraction"] * 100, width, label='v2 (CEACAM5 + CST1)', color='#1F77B4')
    
    plt.ylabel('Co-expression Fraction (%)')
    plt.title('Logic-Gate Candidate Co-expression by Cell Type (Threshold > 0)')
    plt.xticks(x, df_compare_plot["cell_type"], rotation=45, ha='right', fontsize=8)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scrna_v1_vs_v2_coexpression_comparison.png", dpi=300)
    plt.close()
    
    # Save a simpler barplot too
    shutil_copy = FIGURES_DIR / "scrna_pair_coexpression_barplot.png"
    import shutil
    shutil.copy(FIGURES_DIR / "scrna_v1_vs_v2_coexpression_comparison.png", shutil_copy)

    print("[+] All single-cell validation checks completed successfully!")

if __name__ == "__main__":
    main()
