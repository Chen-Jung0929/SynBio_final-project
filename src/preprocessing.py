#!/usr/bin/env python3
import os
import sys
import yaml
import gzip
import pandas as pd
import numpy as np
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def preprocess_metadata(raw_dir, tables_dir):
    pheno_path = raw_dir / "TcgaTargetGTEX_phenotype.txt.gz"
    print(f"[*] Reading phenotype file: {pheno_path}")
    
    # Load phenotype with ISO-8859-1 encoding to handle special characters
    df = pd.read_csv(pheno_path, sep="\t", encoding="ISO-8859-1")
    
    # Define filters
    is_pdac = (
        (df["_study"] == "TCGA") & 
        (df["_sample_type"] == "Primary Tumor") & 
        (df["primary disease or tissue"] == "Pancreatic Adenocarcinoma")
    )
    is_normal = (
        (df["_study"] == "GTEX") & 
        (df["_sample_type"] == "Normal Tissue") & 
        (df["primary disease or tissue"] == "Pancreas")
    )
    
    df_pdac = df[is_pdac].copy()
    df_pdac["group"] = "PDAC"
    
    df_normal = df[is_normal].copy()
    df_normal["group"] = "Normal"
    
    metadata = pd.concat([df_pdac, df_normal], ignore_index=True)
    metadata = metadata[[
        "sample", "group", "_study", "_sample_type", 
        "primary disease or tissue", "_gender"
    ]].rename(columns={"sample": "sample_id"})
    
    tables_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = tables_dir / "sample_metadata.csv"
    metadata.to_csv(metadata_path, index=False)
    print(f"[+] Saved metadata to {metadata_path} (PDAC: {len(df_pdac)}, Normal: {len(df_normal)})")
    
    return metadata

def parse_probemap(raw_dir):
    probemap_path = raw_dir / "gencode.v23.annotation.gene.probemap"
    print(f"[*] Parsing probemap: {probemap_path}")
    df_pm = pd.read_csv(probemap_path, sep="\t")
    # Map Ensembl ID -> Gene Symbol
    mapping = dict(zip(df_pm["id"], df_pm["gene"]))
    return mapping

def filter_expression_matrix(raw_dir, processed_dir, sample_ids, mapping):
    expr_path = raw_dir / "TcgaTargetGtex_rsem_gene_tpm.gz"
    out_path = processed_dir / "expression_matrix.csv.gz"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Stream-filtering expression matrix: {expr_path}")
    
    # Read header to find column indices
    with gzip.open(expr_path, "rt") as f:
        header = f.readline().strip().split("\t")
        
    sample_indices = {sample_id: idx for idx, sample_id in enumerate(header) if sample_id in sample_ids}
    sorted_samples = sorted(list(sample_indices.keys()))
    col_idx_to_sample = {sample_indices[s]: s for s in sorted_samples}
    
    print(f"[*] Identified {len(sample_indices)} columns matching our cohort.")
    
    # Process expression matrix line-by-line
    data = []
    genes = []
    
    count = 0
    with gzip.open(expr_path, "rt") as f:
        f.readline() # Skip header
        for line in f:
            fields = line.strip().split("\t")
            ens_id = fields[0]
            gene_symbol = mapping.get(ens_id, ens_id) # Fallback to Ensembl ID if not in probemap
            
            # Extract expression values for our cohort samples
            vals = [float(fields[idx]) for idx in [sample_indices[s] for s in sorted_samples]]
            
            genes.append(gene_symbol)
            data.append(vals)
            
            count += 1
            if count % 10000 == 0:
                print(f"    Processed {count} genes...")
                
    df_expr = pd.DataFrame(data, index=genes, columns=sorted_samples)
    
    # Average duplicate gene symbols
    print("[*] Handling duplicate gene symbols (averaging expression)...")
    df_expr = df_expr.groupby(df_expr.index).mean()
    
    # Filter out low expression genes (optional, e.g. average expression < 0.1 across samples)
    # The user request asks for removing low expression genes: "e.g. in over 80% samples expression below specified threshold"
    # Let's filter out genes where expression is 0 in >80% samples
    zero_ratio = (df_expr == 0).mean(axis=1)
    df_expr = df_expr[zero_ratio <= 0.8]
    print(f"[+] Retained {len(df_expr)} genes after filtering low-expression genes (<=80% zeros).")
    
    print(f"[*] Saving processed matrix to {out_path}...")
    df_expr.to_csv(out_path, compression="gzip")
    print(f"[+] Saved processed expression matrix of shape {df_expr.shape}.")
    
    return df_expr

def main():
    config = load_config()
    raw_dir = Path(__file__).parent.parent / config["data"]["raw_dir"]
    interim_dir = Path(__file__).parent.parent / config["data"]["interim_dir"]
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    
    # Step 1: Preprocess metadata
    metadata = preprocess_metadata(raw_dir, tables_dir)
    sample_ids = set(metadata["sample_id"].tolist())
    
    # Step 2: Load probemap
    mapping = parse_probemap(raw_dir)
    
    # Step 3: Stream and filter expression matrix
    df_expr = filter_expression_matrix(raw_dir, processed_dir, sample_ids, mapping)
    
    # Step 4: Write QC Summary
    qc_path = tables_dir / "expression_qc_summary.csv"
    qc_summary = pd.DataFrame({
        "Metric": ["Total Samples", "PDAC Samples", "Normal Samples", "Total Genes", "Filtered Genes"],
        "Value": [
            len(metadata), 
            len(metadata[metadata["group"] == "PDAC"]), 
            len(metadata[metadata["group"] == "Normal"]),
            len(mapping),
            len(df_expr)
        ]
    })
    qc_summary.to_csv(qc_path, index=False)
    print(f"[+] Saved QC summary to {qc_path}")

if __name__ == "__main__":
    main()
