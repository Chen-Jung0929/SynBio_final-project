#!/usr/bin/env python3
import gzip
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.resolve()
RAW_DIR = PROJECT_DIR / "data/raw"
PROCESSED_DIR = PROJECT_DIR / "data/processed"
OUT_DIR = PROJECT_DIR / "audit_v2/tables"

GENE_A = "CEACAM5"
GENE_B = "CST1"

# Thresholds from original pipeline run
K_A = 0.40677820318024827
K_B = 0.3606846833167901

# Load probe mapping helper
def load_probe_map():
    annot_path = RAW_DIR / "GPL6244.annot.gz"
    probe_to_gene = {}
    with gzip.open(annot_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                probe_id = parts[0]
                gene_symbol = parts[2]
                if gene_symbol and not gene_symbol.startswith("---"):
                    # Extract first gene symbol if multiple are separated by ///
                    symbol = gene_symbol.split("///")[0].strip()
                    probe_to_gene[probe_id] = symbol
    return probe_to_gene

def load_discovery():
    expr_path = PROCESSED_DIR / "expression_matrix.csv.gz"
    meta_path = PROJECT_DIR / "results_v1_archive/tables/sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0)
    df_meta = pd.read_csv(meta_path)
    
    # Align samples
    common_samples = list(set(df_expr.columns).intersection(set(df_meta["sample_id"])))
    df_expr = df_expr[common_samples]
    df_meta = df_meta.set_index("sample_id").loc[common_samples].reset_index()
    
    return df_expr, df_meta

def load_geo_matrix(matrix_path, probe_to_gene):
    samples = []
    groups = []
    expr_rows = []
    probe_ids = []
    
    in_table = False
    with gzip.open(matrix_path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("!Sample_characteristics_ch1"):
                fields = line.split("\t")[1:]
                for field in fields:
                    field = field.strip().replace('"', '')
                    if "adjacent pancreatic non-tumor" in field or "non-tumor" in field.lower():
                        groups.append(0)  # Normal
                    else:
                        groups.append(1)  # Tumor
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
    return df_geo, df_meta

def load_geo_matrix_gse28735(matrix_path, probe_to_gene):
    samples = []
    groups = []
    expr_rows = []
    probe_ids = []
    
    in_table = False
    with gzip.open(matrix_path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("!Sample_characteristics_ch1") and "tissue:" in line:
                groups = []
                fields = line.split("\t")[1:]
                for field in fields:
                    field = field.strip().replace('"', '')
                    if "tissue: n" in field.lower() or "normal" in field.lower() or "non-tumor" in field.lower():
                        groups.append(0)  # Normal
                    else:
                        groups.append(1)  # Tumor
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
    return df_geo, df_meta

def evaluate_metrics(df_expr, df_meta, label_name):
    # Verify genes are in index
    if GENE_A not in df_expr.index or GENE_B not in df_expr.index:
        raise ValueError(f"Required genes not found in {label_name} index!")
        
    y_true = (df_meta["group"] == "PDAC").astype(int).values
    is_pdac = (df_meta["group"] == "PDAC").values
    
    exp_a = df_expr.loc[GENE_A].values
    exp_b = df_expr.loc[GENE_B].values
    
    # Min-max scaling
    norm_a = (exp_a - np.min(exp_a)) / (np.max(exp_a) - np.min(exp_a))
    norm_b = (exp_b - np.min(exp_b)) / (np.max(exp_b) - np.min(exp_b))
    
    # Raw stats
    min_a, max_a, mean_a = np.min(exp_a), np.max(exp_a), np.mean(exp_a)
    min_b, max_b, mean_b = np.min(exp_b), np.max(exp_b), np.mean(exp_b)
    
    # Boolean logic activation (both inputs > threshold)
    act_a = norm_a > K_A
    act_b = norm_b > K_B
    and_activated = act_a & act_b
    
    # Confusion Matrix
    tp = np.sum((and_activated == 1) & (y_true == 1))
    tn = np.sum((and_activated == 0) & (y_true == 0))
    fp = np.sum((and_activated == 1) & (y_true == 0))
    fn = np.sum((and_activated == 0) & (y_true == 1))
    
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    acc = (tp + tn) / len(y_true)
    
    # Hill Equation Output logic (n=2, P_basal=0.01)
    def hill(x, K, n=2):
        return (x ** n) / (K ** n + x ** n)
    gate_out = 0.01 + 0.99 * hill(norm_a, K_A) * hill(norm_b, K_B)
    roc_auc = roc_auc_score(y_true, gate_out)
    
    # Spearman correlation in tumor-only
    tumor_corr, _ = spearmanr(exp_a[is_pdac], exp_b[is_pdac])
    
    conf_rec = {
        "dataset": label_name,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn
    }
    
    perf_rec = {
        "dataset": label_name,
        "sensitivity": sens,
        "specificity": spec,
        "accuracy": acc,
        "ROC_AUC": roc_auc,
        "tumor_spearman_correlation": tumor_corr
    }
    
    thresh_rec = {
        "dataset": label_name,
        "gene_A": GENE_A,
        "gene_B": GENE_B,
        "min_A": min_a,
        "max_A": max_a,
        "mean_A": mean_a,
        "norm_threshold_A": K_A,
        "raw_threshold_A": min_a + K_A * (max_a - min_a),
        "min_B": min_b,
        "max_B": max_b,
        "mean_B": mean_b,
        "norm_threshold_B": K_B,
        "raw_threshold_B": min_b + K_B * (max_b - min_b)
    }
    
    return conf_rec, perf_rec, thresh_rec

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    probe_to_gene = load_probe_map()
    
    print("[*] Loading datasets for audit...")
    df_expr_disc, df_meta_disc = load_discovery()
    
    matrix_path_val = RAW_DIR / "GSE62452_series_matrix.txt.gz"
    df_expr_val, df_meta_val = load_geo_matrix(matrix_path_val, probe_to_gene)
    
    matrix_path_ext = RAW_DIR / "GSE28735_series_matrix.txt.gz"
    df_expr_ext, df_meta_ext = load_geo_matrix_gse28735(matrix_path_ext, probe_to_gene)
    
    print("[*] Evaluating discovery cohort...")
    c_disc, p_disc, t_disc = evaluate_metrics(df_expr_disc, df_meta_disc, "TCGA+GTEx Discovery")
    
    print("[*] Evaluating validation cohort...")
    c_val, p_val, t_val = evaluate_metrics(df_expr_val, df_meta_val, "GSE62452 Validation")
    
    print("[*] Evaluating external cohort...")
    c_ext, p_ext, t_ext = evaluate_metrics(df_expr_ext, df_meta_ext, "GSE28735 External")
    
    # Save output tables
    df_conf = pd.DataFrame([c_disc, c_val, c_ext])
    df_perf = pd.DataFrame([p_disc, p_val, p_ext])
    df_thresh = pd.DataFrame([t_disc, t_val, t_ext])
    
    df_conf.to_csv(OUT_DIR / "audit_ceacam5_cst1_confusion_matrices.csv", index=False)
    df_perf.to_csv(OUT_DIR / "audit_ceacam5_cst1_performance.csv", index=False)
    df_thresh.to_csv(OUT_DIR / "audit_ceacam5_cst1_thresholds.csv", index=False)
    
    print("[+] Audited metrics written successfully!")
    print(df_perf)

if __name__ == "__main__":
    main()
