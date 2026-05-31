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
DATA_PROCESSED_DIR = PROJECT_DIR / "scrna_validation_independent/data/processed"
TABLES_DIR = PROJECT_DIR / "scrna_validation_independent/tables"
FIGURES_DIR = PROJECT_DIR / "scrna_validation_independent/figures"

def get_expr_array(adata, gene_name):
    if gene_name not in adata.var_names:
        return np.zeros(adata.n_obs)
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

    # Extract expression vectors
    expr = {}
    for g in ["CEACAM5", "CST1", "UBE2S", "CCR6"]:
        expr[g] = get_expr_array(adata, g)
        adata.obs[f"{g}_expression"] = expr[g]

    # 1. Cell-type expression summary
    print("[*] Computing cell-type expression statistics...")
    summary_records = []
    cell_types = sorted(adata.obs['cell_type'].unique())
    
    for ct in cell_types:
        mask = adata.obs['cell_type'] == ct
        sub_adata = adata[mask]
        
        for g in ["CEACAM5", "CST1", "UBE2S", "CCR6"]:
            g_expr = expr[g][mask]
            mean_val = g_expr.mean() if len(g_expr) > 0 else 0.0
            median_val = np.median(g_expr) if len(g_expr) > 0 else 0.0
            pct_expressing = np.mean(g_expr > 0) * 100 if len(g_expr) > 0 else 0.0
            n_patients = len(sub_adata.obs['patient_id'].unique()) if len(g_expr) > 0 else 0
            
            summary_records.append({
                "cell_type": ct,
                "gene": g,
                "mean_expression": mean_val,
                "median_expression": median_val,
                "percent_expressing": pct_expressing,
                "n_cells": len(g_expr),
                "n_patients": n_patients,
                "annotation_source": "independent-marker-inferred"
            })
            
    df_expr_summary = pd.DataFrame(summary_records)
    df_expr_summary.to_csv(TABLES_DIR / "gene_expression_by_independent_celltype.csv", index=False)
    print("[+] Wrote expression summary to tables/gene_expression_by_independent_celltype.csv")

    # 2. Co-expression analysis (Thresholds: expr > 0 and expr > 0.5)
    print("[*] Running co-expression analysis for v1 and v2 pairs...")
    coexpr_records = []
    
    for ct in cell_types:
        mask = adata.obs['cell_type'] == ct
        n_c = np.sum(mask)
        if n_c == 0:
            continue
        
        for thresh_name, thresh_val in [("threshold_1_gt_0", 0.0), ("threshold_2_gt_0.5", 0.5)]:
            c5_pos = expr["CEACAM5"][mask] > thresh_val
            c1_pos = expr["CST1"][mask] > thresh_val
            dp_v2 = c5_pos & c1_pos
            
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
    df_coexpr.to_csv(TABLES_DIR / "pair_coexpression_by_independent_celltype.csv", index=False)
    print("[+] Wrote co-expression summary to tables/pair_coexpression_by_independent_celltype.csv")

    # 3. Patient-level validation
    print("[*] Computing patient-level co-expression statistics...")
    patient_records = []
    patient_ids = sorted(adata.obs['patient_id'].unique())
    
    for pid in patient_ids:
        for ct in cell_types:
            mask = (adata.obs['patient_id'] == pid) & (adata.obs['cell_type'] == ct)
            n_cells_sub = np.sum(mask)
            if n_cells_sub > 0:
                c5_expr = expr["CEACAM5"][mask]
                c1_expr = expr["CST1"][mask]
                u2_expr = expr["UBE2S"][mask]
                c6_expr = expr["CCR6"][mask]
                
                # Double positive counts at both thresholds
                dp_v2_gt_0 = np.sum((c5_expr > 0) & (c1_expr > 0))
                dp_v2_gt_0_5 = np.sum((c5_expr > 0.5) & (c1_expr > 0.5))
                dp_v1_gt_0 = np.sum((u2_expr > 0) & (c6_expr > 0))
                dp_v1_gt_0_5 = np.sum((u2_expr > 0.5) & (c6_expr > 0.5))
                
                patient_records.append({
                    "patient_id": pid,
                    "cell_type": ct,
                    "CEACAM5_mean": c5_expr.mean(),
                    "CST1_mean": c1_expr.mean(),
                    "CEACAM5_CST1_double_positive_fraction_gt_0": dp_v2_gt_0 / n_cells_sub,
                    "CEACAM5_CST1_double_positive_fraction_gt_0_5": dp_v2_gt_0_5 / n_cells_sub,
                    "UBE2S_mean": u2_expr.mean(),
                    "CCR6_mean": c6_expr.mean(),
                    "UBE2S_CCR6_double_positive_fraction_gt_0": dp_v1_gt_0 / n_cells_sub,
                    "UBE2S_CCR6_double_positive_fraction_gt_0_5": dp_v1_gt_0_5 / n_cells_sub,
                    "n_cells": n_cells_sub
                })
                
    df_patient = pd.DataFrame(patient_records)
    df_patient.to_csv(TABLES_DIR / "patient_level_pair_coexpression.csv", index=False)
    print("[+] Wrote patient-level pair coexpression to tables/patient_level_pair_coexpression.csv")

    # Patient-level support summary (Epithelial cells only)
    epi_cell_type = "epithelial / ductal tumor-origin cells"
    df_epi_patient = df_patient[df_patient["cell_type"] == epi_cell_type]
    
    n_patients_with_epithelial = len(df_epi_patient)
    
    # We define double-positive presence as having at least one cell with expression > 0 (or expression > 0.5, we will report both or use gt_0 as the baseline)
    # Let's count patients where the double positive fraction at threshold > 0 is > 0 (meaning at least 1 cell is double-positive)
    n_patients_dp_gt_0 = np.sum(df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0"] > 0)
    n_patients_dp_gt_0_5 = np.sum(df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0_5"] > 0)
    
    median_dp_gt_0 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0"].median()
    min_dp_gt_0 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0"].min()
    max_dp_gt_0 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0"].max()
    
    median_dp_gt_0_5 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0_5"].median()
    min_dp_gt_0_5 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0_5"].min()
    max_dp_gt_0_5 = df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0_5"].max()
    
    support_summary = pd.DataFrame({
        "Metric": [
            "n_patients_with_epithelial_cells",
            "n_patients_with_CEACAM5_CST1_double_positive_epithelial_cells_gt_0",
            "n_patients_with_CEACAM5_CST1_double_positive_epithelial_cells_gt_0_5",
            "median_double_positive_fraction_gt_0",
            "range_double_positive_fraction_gt_0",
            "median_double_positive_fraction_gt_0_5",
            "range_double_positive_fraction_gt_0_5"
        ],
        "Value": [
            str(n_patients_with_epithelial),
            str(n_patients_dp_gt_0),
            str(n_patients_dp_gt_0_5),
            f"{median_dp_gt_0:.4f}",
            f"[{min_dp_gt_0:.4f}, {max_dp_gt_0:.4f}]",
            f"{median_dp_gt_0_5:.4f}",
            f"[{min_dp_gt_0_5:.4f}, {max_dp_gt_0_5:.4f}]"
        ]
    })
    support_summary.to_csv(TABLES_DIR / "patient_level_support_summary.csv", index=False)
    print("[+] Wrote patient support summary to tables/patient_level_support_summary.csv")

    # 4. Generate Visualizations
    print("[*] Computing PCA, neighbors, and UMAP coordinates...")
    # Select highly variable genes
    sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
    # PCA
    sc.tl.pca(adata, svd_solver='arpack')
    # Neighbors
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=20)
    # UMAP
    sc.tl.umap(adata)

    # Figure 1: UMAP by independent cell type
    print("  - Generating cell-type UMAP...")
    plt.figure(figsize=(9, 7))
    sc.pl.umap(adata, color='cell_type', show=False, legend_fontsize=8, palette='tab20')
    plt.title('UMAP of PDAC TME (Independent Cell Types)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "umap_independent_celltype.png", dpi=300)
    plt.close()

    # Figure 2: UMAP by CEACAM5
    print("  - Generating CEACAM5 UMAP...")
    plt.figure(figsize=(7, 6))
    sc.pl.umap(adata, color='CEACAM5', show=False, cmap='viridis')
    plt.title('UMAP: CEACAM5 Expression', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "umap_ceacam5.png", dpi=300)
    plt.close()

    # Figure 3: UMAP by CST1
    print("  - Generating CST1 UMAP...")
    plt.figure(figsize=(7, 6))
    sc.pl.umap(adata, color='CST1', show=False, cmap='viridis')
    plt.title('UMAP: CST1 Expression', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "umap_cst1.png", dpi=300)
    plt.close()

    # Figure 4: UMAP by CEACAM5+CST1 Double Positive (Threshold > 0.5)
    print("  - Generating double-positive UMAP...")
    adata.obs['v2_double_positive'] = [
        "Double Positive" if (c5 > 0.5 and c1 > 0.5) else "Other" 
        for c5, c1 in zip(expr['CEACAM5'], expr['CST1'])
    ]
    plt.figure(figsize=(7, 6))
    sc.pl.umap(
        adata, 
        color='v2_double_positive', 
        show=False, 
        palette={'Double Positive': '#D62728', 'Other': '#E5E3D8'}
    )
    plt.title('UMAP: CEACAM5+/CST1+ Double Positive Cells (>0.5)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "umap_ceacam5_cst1_double_positive.png", dpi=300)
    plt.close()

    # Figure 5: Dotplot
    print("  - Generating candidate genes dotplot...")
    sc.pl.dotplot(
        adata, 
        var_names=["CEACAM5", "CST1", "UBE2S", "CCR6"], 
        groupby='cell_type', 
        save='_candidate_genes_independent.png', 
        show=False
    )
    # Move scanpy generated dotplot to our figures dir
    scanpy_dot_dir = Path("figures")
    dot_file = scanpy_dot_dir / "dotplot__candidate_genes_independent.png"
    if dot_file.exists():
        os.rename(dot_file, FIGURES_DIR / "dotplot_candidate_genes_independent_annotation.png")
    else:
        # Check other possible scanpy locations or search for it
        found = False
        for root, dirs, files in os.walk('.'):
            for file in files:
                if 'candidate_genes_independent' in file:
                    os.rename(os.path.join(root, file), FIGURES_DIR / "dotplot_candidate_genes_independent_annotation.png")
                    found = True
                    break
            if found:
                break
    plt.close()

    # Figure 6: Barplot v1 vs v2 co-expression (Threshold > 0)
    print("  - Generating v1 vs v2 coexpression comparison...")
    # Extract coexpression at threshold > 0
    t1_df = df_coexpr[df_coexpr["threshold_definition"] == "threshold_1_gt_0"].copy()
    
    plt.figure(figsize=(10, 5))
    x = np.arange(len(t1_df))
    width = 0.35
    
    plt.bar(x - width/2, t1_df["UBE2S_CCR6_double_positive_fraction"] * 100, width, label='v1 (UBE2S + CCR6)', color='#7F7F7F')
    plt.bar(x + width/2, t1_df["CEACAM5_CST1_double_positive_fraction"] * 100, width, label='v2 (CEACAM5 + CST1)', color='#1F77B4')
    
    plt.ylabel('Co-expression Fraction (%)')
    plt.title('Logic-Gate Candidate Co-expression by Independent Cell Type (Threshold > 0)', fontsize=12, fontweight='bold')
    plt.xticks(x, t1_df["cell_type"], rotation=45, ha='right', fontsize=8)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "v1_vs_v2_coexpression_independent_annotation.png", dpi=300)
    plt.close()

    # Figure 7: Patient-level CEACAM5+CST1 coexpression (Epithelial cells only)
    print("  - Generating patient-level coexpression figure...")
    df_epi_patient = df_epi_patient.sort_values(by="CEACAM5_CST1_double_positive_fraction_gt_0", ascending=False)
    
    plt.figure(figsize=(10, 5))
    x_pat = np.arange(len(df_epi_patient))
    width_pat = 0.35
    
    plt.bar(
        x_pat - width_pat/2, 
        df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0"] * 100, 
        width_pat, 
        label='Double Positive Fraction (Threshold > 0)', 
        color='#1F77B4'
    )
    plt.bar(
        x_pat + width_pat/2, 
        df_epi_patient["CEACAM5_CST1_double_positive_fraction_gt_0_5"] * 100, 
        width_pat, 
        label='Double Positive Fraction (Threshold > 0.5)', 
        color='#FF7F0E'
    )
    
    plt.ylabel('Double Positive Fraction in Epithelial Cells (%)')
    plt.xlabel('Patient ID')
    plt.title('Patient-Level CEACAM5 + CST1 Co-expression in Epithelial/Ductal Tumor-Origin Cells', fontsize=12, fontweight='bold')
    plt.xticks(x_pat, df_epi_patient["patient_id"], rotation=0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "patient_level_ceacam5_cst1_coexpression.png", dpi=300)
    plt.close()

    print("[+] All analysis calculations and figures generated successfully!")

if __name__ == "__main__":
    main()
