#!/usr/bin/env python3
import os
import sys
import gzip
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

# Set seed
np.random.seed(42)

# Paths
PROJECT_DIR = Path(__file__).parent.parent.resolve()
RAW_DIR = PROJECT_DIR / "data/raw"
PROCESSED_DIR = PROJECT_DIR / "data/processed"
RESULTS_V3_DIR = PROJECT_DIR / "results_v3"
TABLES_V3_DIR = RESULTS_V3_DIR / "tables"

RESULTS_V4_DIR = PROJECT_DIR / "results_v4"
TABLES_V4_DIR = RESULTS_V4_DIR / "tables"
FIGURES_V4_DIR = RESULTS_V4_DIR / "figures"
AUDIT_V4_DIR = RESULTS_V4_DIR / "audit"

sys.path.append(str(PROJECT_DIR / "analysis_v4"))
import pair_search_v4 as ps

def print_section(title):
    print("\n" + "="*80)
    print(f" V4 STAGE: {title}")
    print("="*80)

def parse_gpl6244(annot_path):
    print(f"[*] Parsing GPL6244 microarray annotations: {annot_path}")
    probe_to_gene = {}
    with gzip.open(annot_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            if line.startswith("ID"):
                headers = line.strip().split("\t")
                break
        id_idx = headers.index("ID")
        symbol_idx = -1
        for idx, h in enumerate(headers):
            if "symbol" in h.lower():
                symbol_idx = idx
                break
        if symbol_idx == -1:
            symbol_idx = 1
        for line in f:
            if not line.strip() or line.startswith("!"):
                continue
            fields = line.strip().split("\t")
            if len(fields) > max(id_idx, symbol_idx):
                probe_id = fields[id_idx].strip()
                symbols = fields[symbol_idx].strip().replace('"', '').split("///")
                gene_symbol = symbols[0].strip()
                if gene_symbol:
                    probe_to_gene[probe_id] = gene_symbol
    return probe_to_gene

def classify_sample(field):
    field = field.strip().replace('"', '').lower()
    if "adjacent" in field or "non-tumor" in field or "normal" in field or field == "tissue: n" or field.endswith(": n") or field == "n":
        return 0  # Normal
    elif "tumor" in field or "adenocarcinoma" in field or "cancer" in field or field == "tissue: t" or field.endswith(": t") or field == "t":
        return 1  # Tumor
    else:
        return 1  # Default fallback

def load_geo_matrix(matrix_path, probe_to_gene):
    print(f"[*] Loading and parsing GEO series matrix: {matrix_path}")
    samples = []
    groups = []
    expr_rows = []
    probe_ids = []
    in_table = False
    with gzip.open(matrix_path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("!Sample_characteristics_ch1") and ("adjacent" in line.lower() or "tissue:" in line.lower()):
                groups = []
                fields = line.split("\t")[1:]
                for field in fields:
                    groups.append(classify_sample(field))
            elif line.startswith("!Sample_title"):
                samples = [s.replace('"', '') for s in line.split("\t")[1:]]
            elif line.startswith("!series_matrix_table_begin"):
                in_table = True
                headers = f.readline().strip().split("\t")
                gsm_ids = [h.replace('"', '') for h in headers[1:]]
                continue
            if in_table:
                if line.startswith("!series_matrix_table_end"):
                    break
                fields = line.split("\t")
                probe_id = fields[0].replace('"', '')
                gene_symbol = probe_to_gene.get(probe_id)
                if gene_symbol:
                    vals = [float(v.replace('"', '')) for v in fields[1:]]
                    expr_rows.append(vals)
                    probe_ids.append(gene_symbol)
                    
    df_geo = pd.DataFrame(expr_rows, index=probe_ids, columns=gsm_ids)
    df_geo = df_geo.groupby(df_geo.index).mean()
    
    df_meta = pd.DataFrame({
        "sample_id": gsm_ids,
        "group": ["PDAC" if g == 1 else "Normal" for g in groups[:len(gsm_ids)]]
    })
    print(f"[+] Loaded matrix of shape {df_geo.shape}. Sample size: {len(df_meta)} (PDAC: {sum(df_meta['group']=='PDAC')}, Normal: {sum(df_meta['group']=='Normal')})")
    return df_geo, df_meta

def main():
    for d in [TABLES_V4_DIR, FIGURES_V4_DIR, AUDIT_V4_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        
    print_section("Load Datasets (Discovery & Validation)")
    expr_path = PROCESSED_DIR / "expression_matrix.csv.gz"
    meta_path = PROJECT_DIR / "results_v1_archive/tables/sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    samples = df_expr.columns.tolist()
    df_meta = df_meta.set_index("sample_id").loc[samples].reset_index()
    
    annot_path = RAW_DIR / "GPL6244.annot.gz"
    probe_to_gene = parse_gpl6244(annot_path)
    df_expr_val, df_meta_val = load_geo_matrix(RAW_DIR / "GSE62452_series_matrix.txt.gz", probe_to_gene)
    
    print_section("Load V3 Ranks and Thresholds")
    df_ranks = pd.read_csv(TABLES_V3_DIR / "model_consensus_feature_ranking_v3.csv")
    df_thresh_all = pd.read_csv(TABLES_V3_DIR / "model_specific_thresholds_top200.csv")
    
    print_section("V4 Pair Search (with scRNA Penalty)")
    scrna_prior_path = PROJECT_DIR / "analysis_v4/v4_scrna_gene_prior.csv"
    if not scrna_prior_path.exists():
        print("[-] scRNA prior not found! Running 01_extract_scrna_prior.py first...")
        os.system(f"python {PROJECT_DIR}/analysis_v4/01_extract_scrna_prior.py")
        
    space_pairs = {}
    spaces = [20, 50, 100, 200]
    
    # Increase gamma to ensure biological prior dominates redundancy penalties
    gamma = 5.0 
    
    for n in spaces:
        genes_n = df_ranks["gene"].head(n).tolist()
        df_thresh_n = df_thresh_all[df_thresh_all["gene"].isin(genes_n)]
        
        out_path_n = TABLES_V4_DIR / f"pair_search_ensemble_threshold_top{n}.csv"
        df_p_n = ps.run_pair_search(df_expr, df_meta, df_expr_val, df_meta_val, genes_n, df_thresh_n, 
                                    alpha=0.2, beta=0.1, gamma=gamma, 
                                    prior_path=scrna_prior_path, out_path=out_path_n)
        space_pairs[n] = df_p_n
        
    # Generate topN summary
    stability_records = []
    for n in spaces:
        best_p = space_pairs[n].iloc[0]
        stability_records.append({
            "search_space_top_N": n,
            "evaluated_genes": n,
            "evaluated_pairs": len(space_pairs[n]),
            "top_ranked_pair": f"{best_p['gene_A']} + {best_p['gene_B']}",
            "pair_score": best_p['pair_score'],
            "target_coexpr_est": best_p['target_coexpr_est'],
            "max_off_target_coexpr_est": best_p['max_off_target_coexpr_est'],
            "scrna_score": best_p['scrna_score'],
            "performance_score": best_p['performance_score'],
            "discovery_sensitivity": best_p['discovery_sensitivity'],
            "discovery_specificity": best_p['discovery_specificity'],
            "GSE62452_sensitivity": best_p['GSE62452_sensitivity'],
            "GSE62452_specificity": best_p['GSE62452_specificity'],
        })
    pd.DataFrame(stability_records).to_csv(TABLES_V4_DIR / "topN_pair_stability_summary.csv", index=False)
    
    default_best_pair = space_pairs[100].iloc[0]
    pd.DataFrame([default_best_pair]).to_csv(TABLES_V4_DIR / "v4_default_final_pair.csv", index=False)
    
    gene_a = default_best_pair["gene_A"]
    gene_b = default_best_pair["gene_B"]
    print(f"\n[!] V4 Final Selected Pair: {gene_a} + {gene_b}")
    print(f"    scRNA Score: {default_best_pair['scrna_score']:.4f}")
    print(f"    Performance Score: {default_best_pair['performance_score']:.4f}")
    print(f"    Target Coexpr: {default_best_pair['target_coexpr_est']:.4f}")
    print(f"    Off-target max Coexpr: {default_best_pair['max_off_target_coexpr_est']:.4f}")

if __name__ == "__main__":
    main()
