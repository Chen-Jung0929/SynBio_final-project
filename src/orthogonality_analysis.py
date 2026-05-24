#!/usr/bin/env python3
import os
import sys
import yaml
import re
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def is_protein_coding(gene):
    # Heuristics to screen out pseudogenes, lncRNAs, and uncharacterized transcripts
    if gene.startswith(("RP", "AC", "AL", "AP", "LINC", "MIR", "SNO", "LOC")) and "-" in gene:
        return False
    # Matches pseudogenes ending in P followed by a number (e.g. UBE2SP2, FTH1P7)
    if re.search(r'[A-Z0-9]+P[0-9]+$', gene):
        return False
    return True

def run_orthogonality_analysis(df_expr, df_meta, tables_dir):
    print("[*] Starting orthogonality and pair selection analysis...")
    
    # Load DE statistics and SHAP thresholds
    df_de = pd.read_csv(tables_dir / "differential_expression_discovery.csv").set_index("gene")
    df_thresh = pd.read_csv(tables_dir / "shap_threshold_candidates.csv").set_index("gene")
    
    # Filter candidates: must be in both tables
    common_genes = list(set(df_de.index) & set(df_thresh.index))
    
    # Separate protein-coding and non-coding genes
    coding_genes = [g for g in common_genes if is_protein_coding(g)]
    print(f"[*] Total genes: {len(common_genes)}, Protein-coding genes: {len(coding_genes)}")
    
    if len(coding_genes) < 2:
        print("[!] Too few protein-coding genes. Falling back to all common genes.")
        coding_genes = common_genes
        
    # Get expression data for candidate genes
    X = df_expr.loc[coding_genes].T # Samples as rows, genes as columns
    y = (df_meta.set_index("sample_id").loc[X.index]["group"] == "PDAC").astype(int).values
    
    is_pdac = (y == 1)
    is_normal = (y == 0)
    
    X_tumor = X[is_pdac]
    X_normal = X[is_normal]
    
    # Generate all pairs of genes
    pairs = []
    n_genes = len(coding_genes)
    
    # First pass: try strict correlation limit (abs_corr <= 0.4)
    print("[*] Computing scores for all possible gene pairs (strict correlation threshold)...")
    for i in range(n_genes):
        gene_a = coding_genes[i]
        thresh_a = df_thresh.loc[gene_a, "inferred_threshold"]
        auc_a = df_de.loc[gene_a, "auc"]
        lfc_a = df_de.loc[gene_a, "log2fc"]
        
        for j in range(i + 1, n_genes):
            gene_b = coding_genes[j]
            thresh_b = df_thresh.loc[gene_b, "inferred_threshold"]
            auc_b = df_de.loc[gene_b, "auc"]
            lfc_b = df_de.loc[gene_b, "log2fc"]
            
            corr, _ = spearmanr(X[gene_a].values, X[gene_b].values)
            abs_corr = abs(corr)
            
            if abs_corr > 0.4:
                continue
                
            a_high_tumor = (X_tumor[gene_a] > thresh_a).values
            b_high_tumor = (X_tumor[gene_b] > thresh_b).values
            tumor_and = a_high_tumor & b_high_tumor
            tumor_activation = np.mean(tumor_and)
            
            a_high_normal = (X_normal[gene_a] > thresh_a).values
            b_high_normal = (X_normal[gene_b] > thresh_b).values
            normal_and = a_high_normal & b_high_normal
            normal_activation = np.mean(normal_and)
            
            and_spec = 1.0 - normal_activation
            and_sens = tumor_activation
            
            mean_ind_auc = (auc_a + auc_b) / 2.0
            pair_score = and_sens * and_spec * (1.0 - abs_corr) * mean_ind_auc
            
            pairs.append({
                "gene_A": gene_a,
                "gene_B": gene_b,
                "gene_A_auc": auc_a,
                "gene_B_auc": auc_b,
                "gene_A_log2fc": lfc_a,
                "gene_B_log2fc": lfc_b,
                "correlation": corr,
                "abs_correlation": abs_corr,
                "tumor_AND_activation": tumor_activation,
                "normal_AND_activation": normal_activation,
                "AND_sensitivity": and_sens,
                "AND_specificity": and_spec,
                "pair_score": pair_score
            })
            
    if len(pairs) == 0:
        print("[!] No pairs found with correlation <= 0.4. Re-evaluating with relaxed correlation threshold...")
        for i in range(n_genes):
            gene_a = coding_genes[i]
            thresh_a = df_thresh.loc[gene_a, "inferred_threshold"]
            auc_a = df_de.loc[gene_a, "auc"]
            lfc_a = df_de.loc[gene_a, "log2fc"]
            
            for j in range(i + 1, n_genes):
                gene_b = coding_genes[j]
                thresh_b = df_thresh.loc[gene_b, "inferred_threshold"]
                auc_b = df_de.loc[gene_b, "auc"]
                lfc_b = df_de.loc[gene_b, "log2fc"]
                
                corr, _ = spearmanr(X[gene_a].values, X[gene_b].values)
                abs_corr = abs(corr)
                
                # Check for AND-Gate Performance
                a_high_tumor = (X_tumor[gene_a] > thresh_a).values
                b_high_tumor = (X_tumor[gene_b] > thresh_b).values
                tumor_and = a_high_tumor & b_high_tumor
                tumor_activation = np.mean(tumor_and)
                
                a_high_normal = (X_normal[gene_a] > thresh_a).values
                b_high_normal = (X_normal[gene_b] > thresh_b).values
                normal_and = a_high_normal & b_high_normal
                normal_activation = np.mean(normal_and)
                
                and_spec = 1.0 - normal_activation
                and_sens = tumor_activation
                
                mean_ind_auc = (auc_a + auc_b) / 2.0
                pair_score = and_sens * and_spec * (1.0 - abs_corr) * mean_ind_auc
                
                pairs.append({
                    "gene_A": gene_a,
                    "gene_B": gene_b,
                    "gene_A_auc": auc_a,
                    "gene_B_auc": auc_b,
                    "gene_A_log2fc": lfc_a,
                    "gene_B_log2fc": lfc_b,
                    "correlation": corr,
                    "abs_correlation": abs_corr,
                    "tumor_AND_activation": tumor_activation,
                    "normal_AND_activation": normal_activation,
                    "AND_sensitivity": and_sens,
                    "AND_specificity": and_spec,
                    "pair_score": pair_score
                })
                
    df_pairs = pd.DataFrame(pairs).sort_values(by="pair_score", ascending=False)
    
    pairs_out = tables_dir / "gene_pair_scores.csv"
    df_pairs.to_csv(pairs_out, index=False)
    print(f"[+] Evaluated {len(pairs)} candidate orthogonal pairs.")
    print(f"[+] Saved pair scores to {pairs_out}")
    
    # Select the final best candidate pair
    final_pair = df_pairs.iloc[0:1]
    final_out = tables_dir / "final_candidate_pair.csv"
    final_pair.to_csv(final_out, index=False)
    print("\n--- Final Selected AND Gate Biosensor Input Pair ---")
    print(final_pair.to_string(index=False))

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    run_orthogonality_analysis(df_expr, df_meta, tables_dir)

if __name__ == "__main__":
    main()
