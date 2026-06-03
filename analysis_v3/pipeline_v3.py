#!/usr/bin/env python3
import os
import sys
import gzip
import re
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr, ranksums
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score, precision_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from statsmodels.stats.multitest import multipletests
import argparse

# Set seed
np.random.seed(42)

# Paths
PROJECT_DIR = Path(__file__).parent.parent.resolve()
RAW_DIR = PROJECT_DIR / "data/raw"
PROCESSED_DIR = PROJECT_DIR / "data/processed"

parser = argparse.ArgumentParser()
parser.add_argument("--outdir", type=str, default=None, help="Output directory overrides results_v3")
args, unknown = parser.parse_known_args()

if args.outdir:
    RESULTS_V3_DIR = Path(args.outdir).resolve()
else:
    RESULTS_V3_DIR = PROJECT_DIR / "results_v3"

TABLES_V3_DIR = RESULTS_V3_DIR / "tables"
FIGURES_V3_DIR = RESULTS_V3_DIR / "figures"
MODELS_V3_DIR = RESULTS_V3_DIR / "models"
AUDIT_V3_DIR = RESULTS_V3_DIR / "audit"
REPORTS_V3_DIR = PROJECT_DIR / "reports_v3"

# Import threshold estimation and validation modules
sys.path.append(str(PROJECT_DIR / "analysis_v3"))
import threshold_estimation_v3 as te
import pair_search_v3 as ps
import validation_v3 as val

def print_section(title):
    print("\n" + "="*80)
    print(f" V3 STAGE: {title}")
    print("="*80)

# GPL6244 Parser
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
    
    # Metadata dataframe
    df_meta = pd.DataFrame({
        "sample_id": gsm_ids,
        "group": ["PDAC" if g == 1 else "Normal" for g in groups[:len(gsm_ids)]]
    })
    print(f"[+] Loaded matrix of shape {df_geo.shape}. Sample size: {len(df_meta)} (PDAC: {sum(df_meta['group']=='PDAC')}, Normal: {sum(df_meta['group']=='Normal')})")
    return df_geo, df_meta

def main():
    # Setup directories
    for d in [TABLES_V3_DIR, FIGURES_V3_DIR, MODELS_V3_DIR, AUDIT_V3_DIR, REPORTS_V3_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        
    print_section("Stage 1: Discovery Cohort Ingestion & DEG Screen")
    expr_path = PROCESSED_DIR / "expression_matrix.csv.gz"
    meta_path = PROJECT_DIR / "results_v1_archive/tables/sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    # Align sample names
    samples = df_expr.columns.tolist()
    df_meta = df_meta.set_index("sample_id").loc[samples].reset_index()
    
    is_pdac = (df_meta["group"] == "PDAC").values
    is_normal = (df_meta["group"] == "Normal").values
    
    # PCA Plots
    pca = PCA(n_components=2)
    pca_results = pca.fit_transform(df_expr.T)
    df_pca = pd.DataFrame({
        "PC1": pca_results[:, 0],
        "PC2": pca_results[:, 1],
        "Group": df_meta["group"],
        "Source": df_meta["_study"]
    })
    
    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=df_pca, x="PC1", y="PC2", hue="Group", palette={"PDAC": "#1F77B4", "Normal": "#7F7F7F"}, alpha=0.8)
    plt.title("Discovery Cohort PCA (by Disease Status)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "discovery_pca_by_status.png", dpi=300)
    plt.close()
    
    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=df_pca, x="PC1", y="PC2", hue="Source", palette={"TCGA": "#1F77B4", "GTEX": "#7F7F7F"}, alpha=0.8)
    plt.title("Discovery Cohort PCA (by Data Source)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "discovery_pca_by_source.png", dpi=300)
    plt.close()
    
    # DEGs Welch's t-test and AUC
    results_deg = []
    for gene, row in df_expr.iterrows():
        pdac_vals = row[is_pdac].values
        normal_vals = row[is_normal].values
        mean_p = np.mean(pdac_vals)
        mean_n = np.mean(normal_vals)
        log2fc = mean_p - mean_n
        
        stat, pval = ranksums(pdac_vals, normal_vals) # Using Wilcoxon rank-sum for stability
        
        y_true = np.concatenate([np.ones(len(pdac_vals)), np.zeros(len(normal_vals))])
        y_scores = np.concatenate([pdac_vals, normal_vals])
        try:
            auc = roc_auc_score(y_true, y_scores)
        except:
            auc = 0.5
            
        results_deg.append({
            "gene": gene,
            "mean_pdac": mean_p,
            "mean_normal": mean_n,
            "log2fc": log2fc,
            "p_value": pval,
            "auc": auc
        })
    df_de = pd.DataFrame(results_deg).dropna(subset=["p_value"])
    reject, fdr_vals, _, _ = multipletests(df_de["p_value"].values, alpha=0.05, method="fdr_bh")
    df_de["fdr"] = fdr_vals
    df_de = df_de.sort_values(by="auc", ascending=False)
    df_de.to_csv(TABLES_V3_DIR / "discovery_tcga_gtex_deg.csv", index=False)
    
    # Volcano Plot
    plt.figure(figsize=(6, 5))
    df_de["log_fdr"] = -np.log10(df_de["fdr"] + 1e-300)
    sns.scatterplot(data=df_de, x="log2fc", y="log_fdr", hue=(df_de["auc"] >= 0.8) & (df_de["log2fc"] >= 1.0),
                    palette={True: "#1F77B4", False: "#7F7F7F"}, alpha=0.5, edgecolor="none", legend=False)
    plt.title("Discovery Cohort Volcano Plot", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "discovery_volcano.png", dpi=300)
    plt.close()
    
    print_section("Stage 2: Same-Cohort Validation (GSE62452)")
    annot_path = RAW_DIR / "GPL6244.annot.gz"
    probe_to_gene = parse_gpl6244(annot_path)
    
    df_expr_val, df_meta_val = load_geo_matrix(RAW_DIR / "GSE62452_series_matrix.txt.gz", probe_to_gene)
    is_pdac_val = (df_meta_val["group"] == "PDAC").values
    
    val_de_results = []
    for gene, row in df_expr_val.iterrows():
        pdac_vals = row[is_pdac_val].values
        normal_vals = row[~is_pdac_val].values
        mean_p = np.mean(pdac_vals)
        mean_n = np.mean(normal_vals)
        log2fc = mean_p - mean_n
        
        stat, pval = ranksums(pdac_vals, normal_vals)
        y_true = np.concatenate([np.ones(len(pdac_vals)), np.zeros(len(normal_vals))])
        y_scores = np.concatenate([pdac_vals, normal_vals])
        try:
            auc = roc_auc_score(y_true, y_scores)
        except:
            auc = 0.5
            
        val_de_results.append({
            "gene": gene,
            "mean_pdac_val": mean_p,
            "mean_normal_val": mean_n,
            "log2fc_val": log2fc,
            "p_value_val": pval,
            "auc_val": auc
        })
    df_de_val = pd.DataFrame(val_de_results).dropna(subset=["p_value_val"])
    reject, fdr_vals, _, _ = multipletests(df_de_val["p_value_val"].values, alpha=0.05, method="fdr_bh")
    df_de_val["fdr_val"] = fdr_vals
    df_de_val.to_csv(TABLES_V3_DIR / "gse62452_deg.csv", index=False)
    
    # Save validation volcano
    plt.figure(figsize=(6, 5))
    df_de_val["log_fdr"] = -np.log10(df_de_val["fdr_val"] + 1e-300)
    sns.scatterplot(data=df_de_val, x="log2fc_val", y="log_fdr", hue=(df_de_val["auc_val"] >= 0.7) & (df_de_val["log2fc_val"] >= 0.5),
                    palette={True: "#1F77B4", False: "#7F7F7F"}, alpha=0.6, edgecolor="none", legend=False)
    plt.title("GSE62452 Validation Volcano Plot", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "gse62452_volcano.png", dpi=300)
    plt.close()
    
    # Merge and filter stable genes
    df_merge = pd.merge(df_de, df_de_val, on="gene")
    is_stable = (
        (df_merge["log2fc"] >= 1.0) & (df_merge["fdr"] < 0.05) & (df_merge["auc"] >= 0.8) &
        (df_merge["log2fc_val"] >= 0.5) & (df_merge["fdr_val"] < 0.05) & (df_merge["auc_val"] >= 0.7) &
        ((df_merge["log2fc"] * df_merge["log2fc_val"]) > 0)
    )
    df_merge["stability_score"] = (df_merge["auc"] + df_merge["auc_val"]) / 2 * (1.0 - df_merge["fdr"] - df_merge["fdr_val"])
    df_stable = df_merge[is_stable].sort_values(by="stability_score", ascending=False)
    df_stable.to_csv(TABLES_V3_DIR / "stable_cross_dataset_genes.csv", index=False)
    print(f"[+] Identified {len(df_stable)} cross-dataset stable genes.")
    
    print_section("Stage 3: Locked External Validation Cohort (GSE28735) Load")
    print("[*] GSE28735 remains locked and untouched. Loading is deferred strictly to the validation stage.")
    
    print_section("Stage 4: Three-Model Consensus Feature Ranking & Elastic Net grid search")
    # Training features
    y_train = (df_meta["group"] == "PDAC").astype(int).values
    stable_genes = df_stable["gene"].tolist()
    if len(stable_genes) < 200:
        raise ValueError(f"Fewer than 200 stable genes identified ({len(stable_genes)}). Cannot run top200 search.")
    X_train = df_expr.loc[stable_genes].T.values
    
    # Features standardized for linear coefficient interpretation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Grid search for l1_ratio on Discovery + GSE62452 (Internal CV)
    grid_records = []
    l1_ratios = [0.2, 0.5, 0.8]
    best_l1_ratio = 0.5
    best_avg_auc = -1.0
    
    # Validation data alignment
    X_val = df_expr_val.loc[stable_genes].T.values
    X_val_scaled = scaler.transform(X_val) # Project validation onto discovery scale
    y_val = (df_meta_val["group"] == "PDAC").astype(int).values
    
    for l1 in l1_ratios:
        lr_cv = LogisticRegression(
            penalty="elasticnet",
            solver="saga",
            l1_ratio=l1,
            C=0.5,
            max_iter=10000,
            random_state=42,
            n_jobs=-1
        )
        lr_cv.fit(X_train_scaled, y_train)
        
        auc_train = roc_auc_score(y_train, lr_cv.predict_proba(X_train_scaled)[:, 1])
        auc_val = roc_auc_score(y_val, lr_cv.predict_proba(X_val_scaled)[:, 1])
        avg_auc = (auc_train + auc_val) / 2
        
        is_converged = "yes" if lr_cv.n_iter_[0] < lr_cv.max_iter else "no"
        grid_records.append({
            "penalty": "elasticnet",
            "solver": "saga",
            "C": 0.5,
            "l1_ratio": l1,
            "max_iter": 10000,
            "random_state": 42,
            "features_standardized": "yes",
            "solver_iterations": lr_cv.n_iter_[0],
            "convergence_achieved": is_converged,
            "ROC_AUC_discovery": auc_train,
            "ROC_AUC_GSE62452_validation": auc_val,
            "avg_internal_ROC_AUC": avg_auc,
            "best_selected_yes_no": "no"
        })
        
        if avg_auc > best_avg_auc:
            best_avg_auc = avg_auc
            best_l1_ratio = l1
            
    # Mark the best model
    for r in grid_records:
        if r["l1_ratio"] == best_l1_ratio:
            r["best_selected_yes_no"] = "yes"
            
    df_grid = pd.DataFrame(grid_records)
    df_grid.to_csv(TABLES_V3_DIR / "elastic_net_hyperparameter_log.csv", index=False)
    print(f"[+] Selected best l1_ratio: {best_l1_ratio} with avg internal AUC of {best_avg_auc:.4f}")
    
    # Train final models on selected parameters
    lr_final = LogisticRegression(
        penalty="elasticnet",
        solver="saga",
        l1_ratio=best_l1_ratio,
        C=0.5,
        max_iter=10000,
        random_state=42,
        n_jobs=-1
    )
    lr_final.fit(X_train_scaled, y_train)
    importance_en = np.abs(lr_final.coef_[0])
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    importance_rf = rf.feature_importances_
    
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42, n_jobs=-1)
    xgb_model.fit(X_train, y_train)
    importance_xgb = xgb_model.feature_importances_
    
    # Compute rank scores
    M = len(stable_genes)
    df_en_imp = pd.DataFrame({"gene": stable_genes, "imp_en": importance_en}).sort_values(by="imp_en", ascending=False)
    df_en_imp["rank_en"] = range(1, M + 1)
    df_en_imp["rank_score_en"] = (M - df_en_imp["rank_en"]) / M
    
    df_rf_imp = pd.DataFrame({"gene": stable_genes, "imp_rf": importance_rf}).sort_values(by="imp_rf", ascending=False)
    df_rf_imp["rank_rf"] = range(1, M + 1)
    df_rf_imp["rank_score_rf"] = (M - df_rf_imp["rank_rf"]) / M
    
    df_xgb_imp = pd.DataFrame({"gene": stable_genes, "imp_xgb": importance_xgb}).sort_values(by="imp_xgb", ascending=False)
    df_xgb_imp["rank_xgb"] = range(1, M + 1)
    df_xgb_imp["rank_score_xgb"] = (M - df_xgb_imp["rank_xgb"]) / M
    
    # Merge ranks
    df_ranks = pd.merge(df_en_imp, df_rf_imp, on="gene")
    df_ranks = pd.merge(df_ranks, df_xgb_imp, on="gene")
    df_ranks = pd.merge(df_ranks, df_stable, on="gene")
    
    df_ranks["model_consensus_score"] = (df_ranks["rank_score_en"] + df_ranks["rank_score_rf"] + df_ranks["rank_score_xgb"]) / 3
    df_ranks["consensus_score"] = (df_ranks["model_consensus_score"] + df_ranks["stability_score"]) / 2
    df_ranks = df_ranks.sort_values(by="consensus_score", ascending=False)
    
    # Rename columns to match v3 schema
    df_ranks_out = df_ranks[[
        "gene", "imp_en", "rank_en", "rank_score_en",
        "imp_rf", "rank_rf", "rank_score_rf",
        "imp_xgb", "rank_xgb", "rank_score_xgb",
        "model_consensus_score", "log2fc", "auc", "log2fc_val", "auc_val", 
        "stability_score", "consensus_score"
    ]].rename(columns={
        "imp_en": "importance_elastic_net",
        "rank_en": "rank_elastic_net",
        "rank_score_en": "rank_score_elastic_net",
        "imp_rf": "importance_rf",
        "rank_rf": "rank_rf",
        "rank_score_rf": "rank_score_rf",
        "imp_xgb": "importance_xgb",
        "rank_xgb": "rank_xgb",
        "rank_score_xgb": "rank_score_xgb"
    })
    
    df_ranks_out.to_csv(TABLES_V3_DIR / "model_consensus_feature_ranking_v3.csv", index=False)
    print("[+] Wrote model consensus rankings to model_consensus_feature_ranking_v3.csv")
    
    # Generate Heatmap of top 20 consensus genes
    top_20 = df_ranks_out["gene"].head(20).tolist()
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_expr.loc[top_20], cmap="coolwarm", xticklabels=False, cbar_kws={'label': 'log2 TPM'}, rasterized=True)
    plt.title("Expression Heatmap of Top 20 consensus-Prioritized Genes (Discovery Cohort)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "model_consensus_top_genes_heatmap.png", dpi=300)
    plt.close()
    
    # Top Venn overlap simulation
    plt.figure(figsize=(6, 4))
    overlap_all = len(set(df_en_imp["gene"].head(50)) & set(df_rf_imp["gene"].head(50)) & set(df_xgb_imp["gene"].head(50)))
    plt.bar(["Elastic Net", "Random Forest", "XGBoost", "All Overlap"], [50, 50, 50, overlap_all], color="#1F77B4")
    plt.title("Top Feature Consistency Across Models (V3)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "model_importance_overlap_upset_or_venn.png", dpi=300)
    plt.close()
    
    print_section("Stage 5: Three-Model Ensemble Threshold Estimation (Top 20, 50, 100, 200)")
    # We estimate thresholds for top 200 genes first so we can subset for smaller spaces
    top_200 = df_ranks_out["gene"].head(200).tolist()
    df_thresh_all = te.estimate_thresholds(df_expr, df_meta, top_200)
    
    # Assert exact threshold row counts to prevent incomplete table writes
    if len(df_thresh_all) != 200:
        raise ValueError(f"Incomplete threshold table: model_specific_thresholds_top200.csv has {len(df_thresh_all)} rows, expected 200.")
        
    # Write threshold instability audit
    df_thresh_all[["gene", "K_std", "K_IQR"]].rename(columns={"K_std": "threshold_std_instability", "K_IQR": "threshold_iqr"}).to_csv(TABLES_V3_DIR / "threshold_instability_audit.csv", index=False)
    
    # Create subset threshold tables
    df_thresh_all.head(20).to_csv(TABLES_V3_DIR / "model_specific_thresholds_top20.csv", index=False)
    df_thresh_all.head(50).to_csv(TABLES_V3_DIR / "model_specific_thresholds_top50.csv", index=False)
    df_thresh_all.head(100).to_csv(TABLES_V3_DIR / "model_specific_thresholds_top100.csv", index=False)
    df_thresh_all.to_csv(TABLES_V3_DIR / "model_specific_thresholds_top200.csv", index=False)
    
    # Verify file row counts of generated files
    for n in [20, 50, 100, 200]:
        df_chk = pd.read_csv(TABLES_V3_DIR / f"model_specific_thresholds_top{n}.csv")
        if len(df_chk) != n:
            raise ValueError(f"Threshold table for top {n} has incorrect row count: {len(df_chk)}")
            
    print_section("Stage 6: Top-N Search-Space Sweeps & Pair Scoring")
    # Run searches for top 20, 50, 100, 200 genes
    space_pairs = {}
    spaces = [20, 50, 100, 200]
    
    for n in spaces:
        genes_n = df_ranks_out["gene"].head(n).tolist()
        df_thresh_n = df_thresh_all[df_thresh_all["gene"].isin(genes_n)]
        
        out_path_n = TABLES_V3_DIR / f"pair_search_ensemble_threshold_top{n}.csv"
        df_p_n = ps.run_pair_search(df_expr, df_meta, df_expr_val, df_meta_val, genes_n, df_thresh_n, alpha=0.2, beta=0.1, out_path=out_path_n)
        
        # Verify row counts of pair search files
        expected_pairs = n * (n - 1) // 2
        if len(df_p_n) != expected_pairs:
            raise ValueError(f"Pair search for top {n} has incorrect count: expected {expected_pairs}, got {len(df_p_n)}")
            
        space_pairs[n] = df_p_n
        
    # Record pair freeze timestamp for Locked Validation Sequence audit
    from datetime import datetime
    pair_freeze_time = datetime.now().isoformat()
        
    # Generate topN_pair_stability_summary.csv
    stability_records = []
    for n in spaces:
        best_p = space_pairs[n].iloc[0]
        stability_records.append({
            "search_space_top_N": n,
            "evaluated_genes": n,
            "evaluated_pairs": len(space_pairs[n]),
            "top_ranked_pair": f"{best_p['gene_A']} + {best_p['gene_B']}",
            "pair_score": best_p['pair_score'],
            "discovery_sensitivity": best_p['discovery_sensitivity'],
            "discovery_specificity": best_p['discovery_specificity'],
            "GSE62452_validation_sensitivity": best_p['GSE62452_sensitivity'],
            "GSE62452_validation_specificity": best_p['GSE62452_specificity'],
            "tumor_spearman_r": best_p['tumor_spearman_r'],
            "mean_threshold_instability": best_p['mean_threshold_instability'],
            "redundancy_category": best_p['redundancy_category']
        })
    pd.DataFrame(stability_records).to_csv(TABLES_V3_DIR / "topN_pair_stability_summary.csv", index=False)
    
    # Generate top_ranked_pair_overlap_across_topN.csv
    # Calculate Jaccard intersection of top 20 pairs between adjacent sweeps
    overlap_records = []
    for i in range(len(spaces)):
        n1 = spaces[i]
        p1 = set([f"{r['gene_A']}+{r['gene_B']}" for _, r in space_pairs[n1].head(20).iterrows()])
        for j in range(i, len(spaces)):
            n2 = spaces[j]
            p2 = set([f"{r['gene_A']}+{r['gene_B']}" for _, r in space_pairs[n2].head(20).iterrows()])
            overlap = len(p1.intersection(p2))
            overlap_records.append({
                "space_1": f"top_{n1}",
                "space_2": f"top_{n2}",
                "top20_pairs_shared": overlap,
                "jaccard_similarity": overlap / len(p1.union(p2))
            })
    pd.DataFrame(overlap_records).to_csv(TABLES_V3_DIR / "top_ranked_pair_overlap_across_topN.csv", index=False)
    
    # Pick default final pair (using top 100 space as default)
    # v3 default final pair is the top-ranked pair in the top 100 space
    default_best_pair = space_pairs[100].iloc[0]
    pd.DataFrame([default_best_pair]).to_csv(TABLES_V3_DIR / "v3_default_final_pair.csv", index=False)
    
    gene_a = default_best_pair["gene_A"]
    gene_b = default_best_pair["gene_B"]
    K_a = default_best_pair["K_final_A"]
    K_b = default_best_pair["K_final_B"]
    
    # Write orthogonality audit
    df_orth = space_pairs[100].head(20)[["gene_A", "gene_B", "tumor_spearman_r", "redundancy_category"]]
    df_orth.to_csv(TABLES_V3_DIR / "orthogonality_redundancy_audit.csv", index=False)
    
    # Generate 2D Scatter plot for final pair on Discovery
    exp_a_disc = df_expr.loc[gene_a].values
    exp_b_disc = df_expr.loc[gene_b].values
    min_a, max_a = np.min(exp_a_disc), np.max(exp_a_disc)
    min_b, max_b = np.min(exp_b_disc), np.max(exp_b_disc)
    norm_a_disc = (exp_a_disc - min_a) / (max_a - min_a) if (max_a - min_a) > 0 else np.zeros(len(exp_a_disc))
    norm_b_disc = (exp_b_disc - min_b) / (max_b - min_b) if (max_b - min_b) > 0 else np.zeros(len(exp_b_disc))
    
    plt.figure(figsize=(6, 5))
    df_scatter = pd.DataFrame({"Gene A": norm_a_disc, "Gene B": norm_b_disc, "Group": df_meta["group"]})
    sns.scatterplot(data=df_scatter, x="Gene A", y="Gene B", hue="Group", palette={"PDAC": "#1F77B4", "Normal": "#7F7F7F"}, alpha=0.8)
    plt.axvline(x=K_a, color="#D62728", linestyle="--")
    plt.axhline(y=K_b, color="#D62728", linestyle="--")
    plt.title(f"Discovery Scatter Plot: {gene_a} vs {gene_b}", fontsize=11, fontweight="bold")
    plt.xlabel(f"{gene_a} (Normalized)")
    plt.ylabel(f"{gene_b} (Normalized)")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "final_pair_v3_scatter_discovery.png", dpi=300)
    plt.close()
    
    # Generate 2D Scatter plot for final pair on Validation GSE62452
    exp_a_val = df_expr_val.loc[gene_a].values
    exp_b_val = df_expr_val.loc[gene_b].values
    norm_a_val = (exp_a_val - min_a) / (max_a - min_a) if (max_a - min_a) > 0 else np.zeros(len(exp_a_val))
    norm_b_val = (exp_b_val - min_b) / (max_b - min_b) if (max_b - min_b) > 0 else np.zeros(len(exp_b_val))
    
    plt.figure(figsize=(6, 5))
    df_scatter_val = pd.DataFrame({"Gene A": norm_a_val, "Gene B": norm_b_val, "Group": df_meta_val["group"]})
    sns.scatterplot(data=df_scatter_val, x="Gene A", y="Gene B", hue="Group", palette={"PDAC": "#1F77B4", "Normal": "#7F7F7F"}, alpha=0.8)
    plt.axvline(x=K_a, color="#D62728", linestyle="--")
    plt.axhline(y=K_b, color="#D62728", linestyle="--")
    plt.title(f"Validation Scatter Plot: {gene_a} vs {gene_b} (GSE62452)", fontsize=11, fontweight="bold")
    plt.xlabel(f"{gene_a} (Normalized)")
    plt.ylabel(f"{gene_b} (Normalized)")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "final_pair_v3_scatter_gse62452.png", dpi=300)
    plt.close()
    
    print_section("Stage 7: Locked GSE28735 External Validation & Hill Equation sweeping")
    # Load GSE28735 expressions (Moved to validation stage only)
    gse28735_data_loaded_time = datetime.now().isoformat()
    df_expr_ext, df_meta_ext = load_geo_matrix(RAW_DIR / "GSE28735_series_matrix.txt.gz", probe_to_gene)
    
    # Audit GSE28735 metadata counts
    tumor_sample_count = int(np.sum(df_meta_ext["group"] == "PDAC"))
    normal_sample_count = int(np.sum(df_meta_ext["group"] == "Normal"))
    
    # Save gse28735_metadata_parsing_audit.csv
    df_meta_audit = pd.DataFrame([{
        "dataset": "GSE28735",
        "tumor_sample_count": tumor_sample_count,
        "normal_sample_count": normal_sample_count,
        "expected_tumor": 45,
        "expected_normal": 45,
        "status": "PASS" if (tumor_sample_count == 45 and normal_sample_count == 45) else "FAIL"
    }])
    df_meta_audit.to_csv(AUDIT_V3_DIR / "gse28735_metadata_parsing_audit.csv", index=False)
    print(f"[+] Audited GSE28735: tumor={tumor_sample_count}, normal={normal_sample_count}")
    
    # Stop the pipeline with an error if normal count is zero
    if normal_sample_count == 0:
        raise ValueError("GSE28735 metadata parsing failed: 0 normal samples detected. Pipeline execution halted.")
        
    # Save locked_validation_access_audit.csv
    df_lock_audit = pd.DataFrame([
        {"event": "pair_selection_frozen", "timestamp": pair_freeze_time, "status": "freeze_completed"},
        {"event": "gse28735_data_loaded", "timestamp": gse28735_data_loaded_time, "status": "loading_completed"}
    ])
    df_lock_audit.to_csv(AUDIT_V3_DIR / "locked_validation_access_audit.csv", index=False)
    
    exp_a_ext = df_expr_ext.loc[gene_a].values
    exp_b_ext = df_expr_ext.loc[gene_b].values
    norm_a_ext = (exp_a_ext - min_a) / (max_a - min_a) if (max_a - min_a) > 0 else np.zeros(len(exp_a_ext))
    norm_b_ext = (exp_b_ext - min_b) / (max_b - min_b) if (max_b - min_b) > 0 else np.zeros(len(exp_b_ext))
    y_ext = (df_meta_ext["group"] == "PDAC").astype(int).values
    
    and_ext = (norm_a_ext > K_a) & (norm_b_ext > K_b)
    
    # TP, FP, TN, FN calculations
    TP = int(np.sum((and_ext == True) & (y_ext == 1)))
    FP = int(np.sum((and_ext == True) & (y_ext == 0)))
    TN = int(np.sum((and_ext == False) & (y_ext == 0)))
    FN = int(np.sum((and_ext == False) & (y_ext == 1)))
    
    sens_ext = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    spec_ext = TN / (TN + FP) if (TN + FP) > 0 else 0.0
    
    # Calculate ROC-AUC of AND gate using Hill Equation output
    def hill_eq(x, K, n):
        return (x ** n) / (K ** n + x ** n) if K > 0 else np.zeros(len(x))
        
    def gate_output(a, b, K_a, K_b, n_a, n_b, P_basal, v_max):
        h_a = hill_eq(a, K_a, n_a)
        h_b = hill_eq(b, K_b, n_b)
        return P_basal + v_max * h_a * h_b
        
    out_ext = gate_output(norm_a_ext, norm_b_ext, K_a, K_b, 2, 2, 0.01, 1.0)
    try:
        auc_ext = roc_auc_score(y_ext, out_ext)
    except:
        auc_ext = 0.5
        
    out_disc = gate_output(norm_a_disc, norm_b_disc, K_a, K_b, 2, 2, 0.01, 1.0)
    try:
        auc_disc = roc_auc_score(y_train, out_disc)
    except:
        auc_disc = 0.5
        
    out_val = gate_output(norm_a_val, norm_b_val, K_a, K_b, 2, 2, 0.01, 1.0)
    try:
        auc_val = roc_auc_score(y_val, out_val)
    except:
        auc_val = 0.5
        
    df_ext = pd.DataFrame([{
        "gene_A": gene_a,
        "gene_B": gene_b,
        "K_final_A": K_a,
        "K_final_B": K_b,
        "tumor_sample_count": tumor_sample_count,
        "normal_sample_count": normal_sample_count,
        "sensitivity": sens_ext,
        "specificity": spec_ext,
        "ROC_AUC": auc_ext,
        "TP": TP,
        "FP": FP,
        "TN": TN,
        "FN": FN,
        "GSE28735_Spearman_r": spearmanr(exp_a_ext[y_ext == 1], exp_b_ext[y_ext == 1])[0]
    }])
    df_ext.to_csv(TABLES_V3_DIR / "locked_gse28735_final_validation.csv", index=False)
    print(f"[+] Final Locked External Validation: Sens={sens_ext:.4f}, Spec={spec_ext:.4f}, AUC={auc_ext:.4f}")
    
    # Dataset usage audit
    df_usage = pd.DataFrame([
        {"dataset": "TCGA + GTEx Discovery", "role": "used_for_discovery", "locked_final_validation_only": "no"},
        {"dataset": "GSE62452 Same-Cohort Validation", "role": "used_for_validation_filtering", "locked_final_validation_only": "no"},
        {"dataset": "GSE28735 External Validation", "role": "locked_final_validation_only", "locked_final_validation_only": "yes"}
    ])
    df_usage.to_csv(TABLES_V3_DIR / "data_source_usage_audit.csv", index=False)
    
    # Hill kinetics parameter sweep
    cooperativities = [1, 2, 4, 8]
    leakiness_levels = [0.0, 0.01, 0.05, 0.1]
    sweep_results = []
    
    for n in cooperativities:
        for p_basal in leakiness_levels:
            sweep_results.append({
                "cooperativity_n": n,
                "leakiness_P_basal": p_basal,
                "ROC_AUC_discovery": roc_auc_score(y_train, gate_output(norm_a_disc, norm_b_disc, K_a, K_b, n, n, p_basal, 1.0)),
                "ROC_AUC_validation": roc_auc_score(y_val, gate_output(norm_a_val, norm_b_val, K_a, K_b, n, n, p_basal, 1.0)),
                "ROC_AUC_external": roc_auc_score(y_ext, gate_output(norm_a_ext, norm_b_ext, K_a, K_b, n, n, p_basal, 1.0))
            })
    pd.DataFrame(sweep_results).to_csv(TABLES_V3_DIR / "and_gate_parameter_sweep_v3.csv", index=False)
    
    # Plot Hill activation heatmap
    grid_size = 50
    a_grid = np.linspace(0, 1, grid_size)
    b_grid = np.linspace(0, 1, grid_size)
    A, B = np.meshgrid(a_grid, b_grid)
    Z = gate_output(A, B, K_a, K_b, 2, 2, 0.01, 1.0)
    
    plt.figure(figsize=(6, 5))
    plt.contourf(A, B, Z, levels=20, cmap="coolwarm")
    plt.colorbar(label="Output Strength")
    plt.axvline(x=K_a, color="#D62728", linestyle="--")
    plt.axhline(y=K_b, color="#D62728", linestyle="--")
    plt.title(f"Simulated AND-Gate Response Surface ({gene_a} x {gene_b})", fontsize=11, fontweight="bold")
    plt.xlabel(f"Normalized Input A [{gene_a}]")
    plt.ylabel(f"Normalized Input B [{gene_b}]")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "fig_final_and_gate_heatmap_v3.png", dpi=300)
    plt.close()
    
    # Plot barplot of performance across datasets
    plt.figure(figsize=(7, 4))
    plt.bar(["Disc Sens", "Disc Spec", "Val Sens", "Val Spec", "Ext Sens", "Ext Spec"],
            [default_best_pair["discovery_sensitivity"], default_best_pair["discovery_specificity"],
             default_best_pair["GSE62452_sensitivity"], default_best_pair["GSE62452_specificity"],
             sens_ext, spec_ext],
            color=["#1F77B4", "#1F77B4", "#7F7F7F", "#7F7F7F", "#D62728", "#D62728"])
    plt.title(f"Performance of {gene_a} + {gene_b} AND-gate across cohorts", fontsize=11, fontweight="bold")
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "fig_v3_pair_performance.png", dpi=300)
    plt.close()
    
    print_section("Stage 8: Anti-bias scRNA-seq Downstream Validation (GSE154778)")
    # Get top 3 alternative pairs to write logs for in scRNA validation
    top_alts = [(r["gene_A"], r["gene_B"]) for _, r in space_pairs[100].iloc[1:4].iterrows()]
    df_val_sc, df_pat_sc, df_audit_sc = val.run_sc_validation(gene_a, gene_b, top_alternative_pairs=top_alts)
    
    # Plot scRNA cell type expressions
    plt.figure(figsize=(10, 5))
    df_p_sc = df_val_sc[df_val_sc["rank"] == "final_pair"]
    x = np.arange(len(df_p_sc))
    width = 0.35
    plt.bar(x - width/2, df_p_sc["mean_expression_A"], width, label=gene_a, color="#1F77B4")
    plt.bar(x + width/2, df_p_sc["mean_expression_B"], width, label=gene_b, color="#FF7F0E")
    plt.xticks(x, df_p_sc["cell_type"], rotation=45, ha="right", fontsize=8)
    plt.ylabel("Mean Log-Normalized Count")
    plt.title("v3 Selected Pair Cell-Type Expression Profile (GSE154778 scRNA-seq)", fontsize=11, fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "scrna_celltype_expression.png", dpi=300)
    plt.close()
    
    # Save a simpler co-expression prevalence barplot too
    plt.figure(figsize=(10, 5))
    plt.bar(x, df_p_sc["coexpression_fraction_gt_0"] * 100, color="#1F77B4")
    plt.xticks(x, df_p_sc["cell_type"], rotation=45, ha="right", fontsize=8)
    plt.ylabel("Co-expression Prevalence (%)")
    plt.title("v3 Selected Pair Single-Cell Co-expression (Threshold > 0)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "scrna_pair_coexpression_barplot.png", dpi=300)
    plt.close()
    
    # Generate patient-level prevalence barplot for final pair
    plt.figure(figsize=(10, 5))
    df_epi_pat = df_pat_sc[df_pat_sc["cell_type"] == "tumor-associated epithelial / putative malignant ductal epithelial"].sort_values(by="coexpression_fraction_gt_0", ascending=False)
    x_pat = np.arange(len(df_epi_pat))
    plt.bar(x_pat, df_epi_pat["coexpression_fraction_gt_0"] * 100, color="#1F77B4")
    plt.xticks(x_pat, df_epi_pat["patient_id"])
    plt.ylabel("Double Positive Fraction (%)")
    plt.xlabel("Patient ID")
    plt.title("Patient-Level Co-expression in Putative Malignant Ductal Cells", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_V3_DIR / "patient_level_ceacam5_cst1_coexpression.png", dpi=300)
    plt.close()
    
    # Write results_v3/audit/v3_output_row_count_audit.csv
    row_count_records = []
    
    # Pair search files
    for n in [20, 50, 100, 200]:
        path = TABLES_V3_DIR / f"pair_search_ensemble_threshold_top{n}.csv"
        row_count_records.append({
            "file_name": f"pair_search_ensemble_threshold_top{n}.csv",
            "row_count": len(pd.read_csv(path)),
            "expected_row_count": n * (n - 1) // 2,
            "status": "PASS" if len(pd.read_csv(path)) == (n * (n - 1) // 2) else "FAIL"
        })
        
    # Threshold files
    for n in [20, 50, 100, 200]:
        path = TABLES_V3_DIR / f"model_specific_thresholds_top{n}.csv"
        row_count_records.append({
            "file_name": f"model_specific_thresholds_top{n}.csv",
            "row_count": len(pd.read_csv(path)),
            "expected_row_count": n,
            "status": "PASS" if len(pd.read_csv(path)) == n else "FAIL"
        })
        
    pd.DataFrame(row_count_records).to_csv(AUDIT_V3_DIR / "v3_output_row_count_audit.csv", index=False)
    print("[+] Wrote row count audit to results_v3/audit/v3_output_row_count_audit.csv")

    # Run the audit script and verify all outputs
    import subprocess
    print_section("Audit Checks Verification")
    audit_res = subprocess.run([sys.executable, "analysis_v3/audit_v3_outputs.py"], capture_output=False)
    if audit_res.returncode != 0:
        print("[!] Audit checks FAILED. Halting pipeline execution.")
        sys.exit(1)
    else:
        print("[+] Audit checks PASSED.")

    print_section("Stage 9: Compile V3 Reports & Final Audit Summary")
    # Trigger generate_reports_v3.py which reads tables/figures and writes REPORTS_V3
    import generate_reports_v3 as gr
    gr.main()
    print("[+] Final Report compiled successfully.")

if __name__ == "__main__":
    main()
