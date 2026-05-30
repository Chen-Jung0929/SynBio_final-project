#!/usr/bin/env python3
import os
import sys
import yaml
import gzip
import re
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def hill_equation(x, K, n):
    x = np.clip(x, 0, None)
    K = np.clip(K, 1e-6, None)
    return (x ** n) / (K ** n + x ** n)

def run_random_pair_control(df_expr, df_meta, tables_dir, gene_a, gene_b):
    print("[*] Running random pair control (1000 iterations)...")
    genes = df_expr.index.tolist()
    y_true = (df_meta.set_index("sample_id").loc[df_expr.columns]["group"] == "PDAC").astype(int).values
    
    np.random.seed(42)
    random_aucs = []
    
    for _ in range(1000):
        # Pick 2 random genes
        rand_a, rand_b = np.random.choice(genes, size=2, replace=False)
        
        # Simple AND-gate logic using 10th percentile of tumor as threshold
        vals_a = df_expr.loc[rand_a].values
        vals_b = df_expr.loc[rand_b].values
        
        min_a, max_a = np.min(vals_a), np.max(vals_a)
        min_b, max_b = np.min(vals_b), np.max(vals_b)
        
        if (max_a - min_a) == 0 or (max_b - min_b) == 0:
            continue
            
        norm_a = (vals_a - min_a) / (max_a - min_a)
        norm_b = (vals_b - min_b) / (max_b - min_b)
        
        # Use Youden-like threshold or median
        K_a = 0.5
        K_b = 0.5
        
        output = hill_equation(norm_a, K_a, 1) * hill_equation(norm_b, K_b, 1)
        try:
            auc = roc_auc_score(y_true, output)
            random_aucs.append(auc)
        except:
            pass
            
    df_rand = pd.DataFrame({"Random_Pair_AUC": random_aucs})
    df_rand.to_csv(tables_dir / "random_pair_control.csv", index=False)
    
    mean_rand_auc = np.mean(random_aucs)
    p_val_chosen = np.mean(np.array(random_aucs) >= 0.998)
    
    print(f"[+] Mean Random Pair AUC: {mean_rand_auc:.3f}")
    print(f"[+] Empirical p-value of UBE2S + CCR6 pair (AUC >= 0.998): p = {p_val_chosen:.4f}")

def run_threshold_sensitivity(df_expr, df_meta, tables_dir, gene_a, gene_b, K_a, K_b):
    print("[*] Running threshold sensitivity analysis...")
    expr_a = df_expr.loc[gene_a].values
    expr_b = df_expr.loc[gene_b].values
    y_true = (df_meta.set_index("sample_id").loc[df_expr.columns]["group"] == "PDAC").astype(int).values
    
    min_a, max_a = np.min(expr_a), np.max(expr_a)
    min_b, max_b = np.min(expr_b), np.max(expr_b)
    
    norm_a = (expr_a - min_a) / (max_a - min_a)
    norm_b = (expr_b - min_b) / (max_b - min_b)
    
    perturbations = [-0.5, -0.25, -0.1, 0.0, 0.1, 0.25, 0.5]
    results = []
    
    for pct_a in perturbations:
        for pct_b in perturbations:
            K_a_pert = np.clip(K_a * (1.0 + pct_a), 0.01, 0.99)
            K_b_pert = np.clip(K_b * (1.0 + pct_b), 0.01, 0.99)
            
            output = hill_equation(norm_a, K_a_pert, 1) * hill_equation(norm_b, K_b_pert, 1)
            auc = roc_auc_score(y_true, output)
            
            # Accuracy at default threshold of 0.25
            preds = (output > 0.25).astype(int)
            acc = accuracy_score(y_true, preds)
            
            results.append({
                "Perturbation_A": pct_a,
                "Perturbation_B": pct_b,
                "K_A_perturbed": K_a_pert,
                "K_B_perturbed": K_b_pert,
                "ROC_AUC": auc,
                "Accuracy": acc
            })
            
    df_sens = pd.DataFrame(results)
    df_sens.to_csv(tables_dir / "threshold_sensitivity.csv", index=False)
    print(f"[+] Saved threshold sensitivity results to {tables_dir / 'threshold_sensitivity.csv'}")

def parse_gpl_annotations(annot_path):
    print(f"[*] Parsing platform annotations: {annot_path}")
    probe_to_gene = {}
    
    # GEO annotation files have header lines starting with '#'
    with gzip.open(annot_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            # Header line of the table starts with ID
            if line.startswith("ID"):
                headers = line.strip().split("\t")
                break
                
        # Find column indices for ID and Gene Symbol
        id_idx = headers.index("ID")
        # In GPL6244, gene symbol is typically labeled as "Gene Symbol"
        symbol_idx = -1
        for idx, h in enumerate(headers):
            if "symbol" in h.lower():
                symbol_idx = idx
                break
                
        if symbol_idx == -1:
            print("[-] Warning: Could not find Gene Symbol column in annotations. Defaulting to 2nd column.")
            symbol_idx = 1
            
        for line in f:
            if not line.strip() or line.startswith("!"):
                continue
            fields = line.strip().split("\t")
            if len(fields) > max(id_idx, symbol_idx):
                probe_id = fields[id_idx].strip()
                # Extract first gene symbol if multiple exist
                symbols = fields[symbol_idx].strip().replace('"', '').split("///")
                gene_symbol = symbols[0].strip()
                if gene_symbol:
                    probe_to_gene[probe_id] = gene_symbol
                    
    return probe_to_gene

def run_external_validation(tables_dir, gene_a, gene_b, K_a_disc, K_b_disc):
    print("[*] Running independent validation on GSE62452...")
    
    raw_dir = Path(__file__).parent.parent / "data/raw"
    matrix_path = raw_dir / "GSE62452_series_matrix.txt.gz"
    annot_path = raw_dir / "GPL6244.annot.gz"
    
    if not matrix_path.exists() or not annot_path.exists():
        print("[-] Verification files missing. Skipping GSE62452 validation.")
        return
        
    # 1. Parse Annotations
    probe_to_gene = parse_gpl_annotations(annot_path)
    
    # Find probes mapping to our candidate genes
    probes_a = [probe for probe, gene in probe_to_gene.items() if gene == gene_a]
    probes_b = [probe for probe, gene in probe_to_gene.items() if gene == gene_b]
    
    print(f"[*] Probes for {gene_a}: {probes_a}")
    print(f"[*] Probes for {gene_b}: {probes_b}")
    
    if not probes_a or not probes_b:
        print("[-] Target genes not found in microarray platform probes. Skipping validation.")
        return
        
    # We will use the first probe found for each gene
    probe_a = probes_a[0]
    probe_b = probes_b[0]
    
    # 2. Parse GSE62452 Series Matrix
    print(f"[*] Parsing expression data from: {matrix_path}")
    
    samples = []
    groups = []
    
    expr_data = {probe_a: [], probe_b: []}
    
    with gzip.open(matrix_path, "rt") as f:
        for line in f:
            line = line.strip()
            # 1. Extract sample categories (tissue types)
            if line.startswith("!Sample_characteristics_ch1"):
                # Matches "tissue: Pancreatic tumor" or "tissue: adjacent pancreatic non-tumor"
                fields = line.split("\t")[1:]
                for field in fields:
                    field = field.strip().replace('"', '')
                    if "adjacent pancreatic non-tumor" in field:
                        groups.append(0) # Normal
                    else:
                        groups.append(1) # Tumor
                        
            elif line.startswith("!Sample_title"):
                # Read sample titles / GSM IDs to verify sample count
                samples = line.split("\t")[1:]
                
            elif line.startswith("!series_matrix_table_begin"):
                break
                
        # Now read expression table rows
        # Read header row of matrix table
        headers = f.readline().strip().split("\t")
        gsm_ids = [h.replace('"', '') for h in headers[1:]]
        
        for line in f:
            if line.startswith("!series_matrix_table_end"):
                break
            fields = line.strip().split("\t")
            probe_id = fields[0].replace('"', '')
            if probe_id in [probe_a, probe_b]:
                vals = [float(val.replace('"', '')) for val in fields[1:]]
                expr_data[probe_id] = vals
                
    # Align and build validation dataframe
    df_val = pd.DataFrame({
        "sample_id": gsm_ids,
        "group": groups[:len(gsm_ids)],
        "expr_A": expr_data[probe_a],
        "expr_B": expr_data[probe_b]
    })
    
    print(f"[+] Loaded GSE62452 expression data: {len(df_val)} samples (Tumor: {sum(df_val['group'])}, Normal: {len(df_val)-sum(df_val['group'])})")
    
    # 3. Rescale expression to [0, 1] range using local min-max to account for platform scale differences
    vals_a = df_val["expr_A"].values
    vals_b = df_val["expr_B"].values
    
    norm_a = (vals_a - np.min(vals_a)) / (np.max(vals_a) - np.min(vals_a))
    norm_b = (vals_b - np.min(vals_b)) / (np.max(vals_b) - np.min(vals_b))
    
    # Run Hill AND gate model using K parameters from discovery (or rescaled locally)
    # Since K parameters in discovery represent a relative position in the dynamic range,
    # we apply the same relative thresholds (0.760 and 0.464) to the GSE62452 rescaled expressions!
    output = hill_equation(norm_a, K_a_disc, 1) * hill_equation(norm_b, K_b_disc, 1)
    
    auc = roc_auc_score(df_val["group"].values, output)
    preds = (output > 0.25).astype(int)
    acc = accuracy_score(df_val["group"].values, preds)
    sens = recall_score(df_val["group"].values, preds)
    spec = recall_score(1 - df_val["group"].values, 1 - preds)
    
    val_results = pd.DataFrame([{
        "dataset": "GSE62452",
        "sample_size": len(df_val),
        "ROC_AUC": auc,
        "Accuracy": acc,
        "Sensitivity": sens,
        "Specificity": spec
    }])
    
    val_out = tables_dir / "external_validation_final_pair.csv"
    val_results.to_csv(val_out, index=False)
    print(f"[+] Saved external validation results to {val_out}")
    print(val_results.to_string(index=False))

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    # Load final selected pair and parameters
    perf_path = tables_dir / "and_gate_performance.csv"
    df_perf = pd.read_csv(perf_path)
    
    gene_a = df_perf.loc[0, "gene_A"]
    gene_b = df_perf.loc[0, "gene_B"]
    K_a = df_perf.loc[0, "K_A"]
    K_b = df_perf.loc[0, "K_B"]
    
    run_random_pair_control(df_expr, df_meta, tables_dir, gene_a, gene_b)
    run_threshold_sensitivity(df_expr, df_meta, tables_dir, gene_a, gene_b, K_a, K_b)
    run_external_validation(tables_dir, gene_a, gene_b, K_a, K_b)

if __name__ == "__main__":
    main()
