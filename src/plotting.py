#!/usr/bin/env python3
import os
import sys
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def plot_volcano(tables_dir, figures_dir, gene_a, gene_b):
    print("[*] Generating Volcano Plot...")
    df_de = pd.read_csv(tables_dir / "differential_expression_discovery.csv")
    
    # Calculate -log10(FDR)
    df_de["minus_log10_fdr"] = -np.log10(df_de["fdr"] + 1e-100)
    
    plt.figure(figsize=(8, 6))
    
    # Background points
    sns.scatterplot(
        data=df_de, x="log2fc", y="minus_log10_fdr",
        hue=df_de["fdr"] < 0.05, palette={True: "skyblue", False: "lightgray"},
        alpha=0.6, legend=False, edgecolor=None
    )
    
    # Highlight candidates (FDR < 0.05 & Log2FC >= 1)
    df_cand = df_de[(df_de["fdr"] < 0.05) & (df_de["log2fc"] >= 1.0)]
    sns.scatterplot(
        data=df_cand, x="log2fc", y="minus_log10_fdr",
        color="steelblue", alpha=0.8, legend=False, edgecolor=None
    )
    
    # Highlight final pair
    final_pair = df_de[df_de["gene"].isin([gene_a, gene_b])]
    sns.scatterplot(
        data=final_pair, x="log2fc", y="minus_log10_fdr",
        color="crimson", s=120, zorder=5, edgecolor="black", linewidth=1.5
    )
    
    # Add text labels for final pair
    for _, row in final_pair.iterrows():
        plt.text(
            row["log2fc"] + 0.15, row["minus_log10_fdr"] + 2, 
            row["gene"], fontsize=12, fontweight="bold", color="black"
        )
        
    plt.axvline(1.0, color="gray", linestyle="--", linewidth=1)
    plt.axhline(-np.log10(0.05), color="gray", linestyle="--", linewidth=1)
    
    plt.title("Volcano Plot: PDAC vs Normal Pancreas", fontsize=14, fontweight="bold")
    plt.xlabel("Log2 Fold Change (PDAC - Normal)", fontsize=12)
    plt.ylabel("-Log10 (FDR-adjusted p-value)", fontsize=12)
    plt.tight_layout()
    plt.savefig(figures_dir / "volcano_discovery.png", dpi=150)
    plt.close()

def plot_shap_importance(tables_dir, figures_dir):
    print("[*] Generating SHAP Feature Importance Plot...")
    df_shap = pd.read_csv(tables_dir / "shap_feature_importance.csv").head(15)
    
    # Exclude lncRNAs/pseudogenes for the display to focus on clean targets
    df_shap["is_coding"] = df_shap["gene"].apply(lambda g: not (g.startswith(("RP", "AC", "AL", "AP", "LINC", "MIR", "SNO")) and "-" in g) and not re.search(r'[A-Z0-9]+P[0-9]+$', g))
    
    plt.figure(figsize=(8, 5))
    colors = ["darkcyan" if c else "coral" for c in df_shap["is_coding"]]
    sns.barplot(
        data=df_shap, x="mean_abs_shap", y="gene",
        palette=colors, hue="gene", legend=False
    )
    
    plt.title("Top 15 Most Important Features (SHAP)", fontsize=14, fontweight="bold")
    plt.xlabel("Mean Absolute SHAP Value (Impact on Model Decision)", fontsize=12)
    plt.ylabel("Gene Name", fontsize=12)
    
    # Legend for coding/non-coding
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='darkcyan', label='Protein-coding'),
        Patch(facecolor='coral', label='Pseudogene/Non-coding')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(figures_dir / "shap_summary.png", dpi=150)
    plt.close()

def plot_pair_scatter_with_boundary(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b):
    print("[*] Generating Gene Pair Scatter & Decision Boundary...")
    
    expr_a = df_expr.loc[gene_a].values
    expr_b = df_expr.loc[gene_b].values
    groups = df_meta.set_index("sample_id").loc[df_expr.columns]["group"].values
    
    # Retrieve raw thresholds
    df_thresh = pd.read_csv(tables_dir / "shap_threshold_candidates.csv").set_index("gene")
    thresh_a = df_thresh.loc[gene_a, "inferred_threshold"]
    thresh_b = df_thresh.loc[gene_b, "inferred_threshold"]
    
    df_plot = pd.DataFrame({
        "expr_A": expr_a,
        "expr_B": expr_b,
        "Group": groups
    })
    
    plt.figure(figsize=(7, 6))
    sns.scatterplot(
        data=df_plot, x="expr_A", y="expr_B", hue="Group",
        palette={"PDAC": "crimson", "Normal": "dodgerblue"},
        alpha=0.8, s=60, edgecolor="w"
    )
    
    # Draw decision boundary lines
    plt.axvline(thresh_a, color="black", linestyle="--", linewidth=1.5, label=f"{gene_a} Thresh: {thresh_a:.2f}")
    plt.axhline(thresh_b, color="black", linestyle="--", linewidth=1.5, label=f"{gene_b} Thresh: {thresh_b:.2f}")
    
    # Label the quadrants
    plt.text(thresh_a + 0.5, thresh_b + 0.5, "AND Gate ON\n(Tumor Specific)", fontsize=11, fontweight="bold", color="darkgreen")
    
    plt.title(f"Two-Gene Specificity Scatter: {gene_a} vs {gene_b}", fontsize=14, fontweight="bold")
    plt.xlabel(f"{gene_a} Expression [Log2(TPM + 0.001)]", fontsize=12)
    plt.ylabel(f"{gene_b} Expression [Log2(TPM + 0.001)]", fontsize=12)
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(figures_dir / "gene_pair_scatter_final.png", dpi=150)
    plt.close()

def plot_and_gate_heatmap(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b, Hill_n, P_basal):
    print("[*] Generating 2D AND Gate Activation Heatmap...")
    
    expr_a = df_expr.loc[gene_a].values
    expr_b = df_expr.loc[gene_b].values
    groups = df_meta.set_index("sample_id").loc[df_expr.columns]["group"].values
    
    # Rescale inputs
    min_a, max_a = np.min(expr_a), np.max(expr_a)
    min_b, max_b = np.min(expr_b), np.max(expr_b)
    
    norm_a = (expr_a - min_a) / (max_a - min_a)
    norm_b = (expr_b - min_b) / (max_b - min_b)
    
    # Generate 2D grid for surface heatmap
    u = np.linspace(0.0, 1.0, 100)
    v = np.linspace(0.0, 1.0, 100)
    U, V = np.meshgrid(u, v)
    
    # Calculate AND gate reporter output
    Z = P_basal + 1.0 * hill_equation(U, K_a, Hill_n) * hill_equation(V, K_b, Hill_n)
    Z = np.clip(Z, 0.0, 1.0)
    
    plt.figure(figsize=(8, 6.5))
    
    # Plot heatmap
    cp = plt.contourf(U, V, Z, levels=50, cmap="YlGnBu")
    cbar = plt.colorbar(cp)
    cbar.set_label("Simulated AND-Gate Reporter Output [0-1]", fontsize=12)
    
    # Overlay patient data coordinates
    tumor_mask = (groups == "PDAC")
    normal_mask = (groups == "Normal")
    
    plt.scatter(norm_a[tumor_mask], norm_b[tumor_mask], color="red", label="PDAC Patient Tumor", alpha=0.8, edgecolor="black", s=30)
    plt.scatter(norm_a[normal_mask], norm_b[normal_mask], color="cyan", label="GTEx Normal Pancreas", alpha=0.8, edgecolor="black", s=30)
    
    # Mark threshold points
    plt.axvline(K_a, color="black", linestyle=":", linewidth=2, label="K_A parameter")
    plt.axhline(K_b, color="black", linestyle=":", linewidth=2, label="K_B parameter")
    
    plt.title(f"In Silico AND-Gate Simulation: {gene_a} AND {gene_b}", fontsize=14, fontweight="bold")
    plt.xlabel(f"Rescaled {gene_a} Abundance (0-1)", fontsize=12)
    plt.ylabel(f"Rescaled {gene_b} Abundance (0-1)", fontsize=12)
    plt.legend(loc="upper left", framealpha=0.9)
    plt.tight_layout()
    plt.savefig(figures_dir / "and_gate_heatmap_final.png", dpi=150)
    plt.close()

def hill_equation(x, K, n):
    x = np.clip(x, 0, None)
    K = np.clip(K, 1e-6, None)
    return (x ** n) / (K ** n + x ** n)

def plot_roc_curves(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b, Hill_n, P_basal):
    print("[*] Generating ROC Curves Comparison...")
    
    expr_a = df_expr.loc[gene_a].values
    expr_b = df_expr.loc[gene_b].values
    y_true = (df_meta.set_index("sample_id").loc[df_expr.columns]["group"] == "PDAC").astype(int).values
    
    min_a, max_a = np.min(expr_a), np.max(expr_a)
    min_b, max_b = np.min(expr_b), np.max(expr_b)
    
    norm_a = (expr_a - min_a) / (max_a - min_a)
    norm_b = (expr_b - min_b) / (max_b - min_b)
    
    # Calculate AND gate reporter output
    and_output = P_basal + 1.0 * hill_equation(norm_a, K_a, Hill_n) * hill_equation(norm_b, K_b, Hill_n)
    
    plt.figure(figsize=(7, 6))
    
    # 1. AND Gate ROC
    fpr_and, tpr_and, _ = roc_curve(y_true, and_output)
    auc_and = auc(fpr_and, tpr_and)
    plt.plot(fpr_and, tpr_and, color="crimson", linewidth=2.5, label=f"Combined AND Gate (AUC = {auc_and:.4f})")
    
    # 2. Gene A ROC
    fpr_a, tpr_a, _ = roc_curve(y_true, norm_a)
    auc_a = auc(fpr_a, tpr_a)
    plt.plot(fpr_a, tpr_a, color="forestgreen", linestyle="--", label=f"Single Input {gene_a} (AUC = {auc_a:.4f})")
    
    # 3. Gene B ROC
    fpr_b, tpr_b, _ = roc_curve(y_true, norm_b)
    auc_b = auc(fpr_b, tpr_b)
    plt.plot(fpr_b, tpr_b, color="darkorange", linestyle="--", label=f"Single Input {gene_b} (AUC = {auc_b:.4f})")
    
    plt.plot([0, 1], [0, 1], color="gray", linestyle=":", label="Random Classifier (AUC = 0.500)")
    
    plt.title("ROC Curves Comparison: Single vs Logic-Gated Input", fontsize=14, fontweight="bold")
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
    plt.ylabel("True Positive Rate (Sensitivity)", fontsize=12)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(figures_dir / "roc_curves.png", dpi=150)
    plt.close()

import re

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    figures_dir = Path(__file__).parent.parent / config["results"]["figures_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    perf_path = tables_dir / "and_gate_performance.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    df_perf = pd.read_csv(perf_path)
    
    gene_a = df_perf.loc[0, "gene_A"]
    gene_b = df_perf.loc[0, "gene_B"]
    K_a = df_perf.loc[0, "K_A"]
    K_b = df_perf.loc[0, "K_B"]
    Hill_n = int(df_perf.loc[0, "Hill_n"])
    P_basal = df_perf.loc[0, "P_basal"]
    
    plot_volcano(tables_dir, figures_dir, gene_a, gene_b)
    plot_shap_importance(tables_dir, figures_dir)
    plot_pair_scatter_with_boundary(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b)
    plot_and_gate_heatmap(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b, Hill_n, P_basal)
    plot_roc_curves(df_expr, df_meta, tables_dir, figures_dir, gene_a, gene_b, K_a, K_b, Hill_n, P_basal)

if __name__ == "__main__":
    main()
