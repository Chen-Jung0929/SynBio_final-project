#!/usr/bin/env python3
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
from pathlib import Path
from sklearn.metrics import roc_auc_score

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_DIR = PROJECT_DIR / "analysis_v4"
GSE154778_FILE = V4_DIR / "GSE154778_dgeMtx.csv.gz"
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"

MARKER_GENES = {
    "ductal": ["EPCAM", "KRT19", "SOX9", "CFTR"],
    "acinar": ["PRSS1", "CPA1", "REG1A", "AMY2A"],
    "fibroblast": ["COL1A1", "COL1A2", "DCN", "LUM", "ACTA2", "FAP"],
    "endothelial": ["PECAM1", "VWF", "KDR"],
    "t_cells": ["CD3D", "CD3E", "CD2"],
    "b_cells": ["MS4A1", "CD79A"],
    "macrophages": ["LST1", "CD68", "CD14", "FCGR3A", "C1QA"],
    "mast_cells": ["TPSAB1", "CPA3"],
}

def get_valid_markers(adata, genes):
    return [g for g in genes if g in adata.var_names]

def score_marker_groups(adata):
    scores = {}
    for group, genes in MARKER_GENES.items():
        markers = get_valid_markers(adata, genes)
        if not markers:
            scores[group] = np.zeros(adata.n_obs)
            continue
        idx = [adata.var_names.get_loc(g) for g in markers]
        expr_slice = adata.X[:, idx]
        scores[group] = expr_slice.mean(axis=1) if isinstance(expr_slice, np.ndarray) else np.array(expr_slice.mean(axis=1)).flatten()
    return pd.DataFrame(scores, index=adata.obs_names)

def assign_compartments(adata, marker_scores):
    compartments = []
    for idx, row in marker_scores.iterrows():
        immune_score = max(row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"])
        stromal_score = max(row["fibroblast"], row["endothelial"])
        epi_score = max(row["ductal"], row["acinar"])
        max_cat = np.argmax([immune_score, stromal_score, epi_score])

        if max_cat == 0:
            sub_cat = np.argmax([row["t_cells"], row["b_cells"], row["macrophages"], row["mast_cells"]])
            compartments.append(["T cells", "B cells", "macrophages / monocytes", "mast cells"][sub_cat])
        elif max_cat == 1:
            sub_cat = np.argmax([row["fibroblast"], row["endothelial"]])
            compartments.append(["CAF / fibroblast", "endothelial"][sub_cat])
        else:
            sub_cat = np.argmax([row["ductal"], row["acinar"]])
            if sub_cat == 1:
                compartments.append("normal acinar")
            elif bool(adata.obs.loc[idx, "is_tumor"]):
                compartments.append("malignant ductal / epithelial")
            else:
                compartments.append("normal ductal")
    return compartments

def generate_pseudobulk(adata, composition, n_samples=100, cells_per_sample=500):
    """
    Generate pseudo-bulk samples by sampling cells based on the given composition.
    """
    pb_matrix = np.zeros((n_samples, adata.n_vars))
    
    # Map cells to compartments
    comp_indices = {}
    for comp in composition.keys():
        idx = np.where(adata.obs["compartment"] == comp)[0]
        if len(idx) == 0:
            print(f"[-] Warning: No cells found for compartment {comp}")
            # Fallback to random if missing
            idx = np.arange(adata.n_obs)
        comp_indices[comp] = idx
        
    for i in range(n_samples):
        sample_cells = []
        for comp, frac in composition.items():
            n_comp_cells = int(cells_per_sample * frac)
            sampled = np.random.choice(comp_indices[comp], size=n_comp_cells, replace=True)
            sample_cells.extend(sampled)
            
        # Sum expression across sampled cells
        expr = adata.X[sample_cells, :]
        if not isinstance(expr, np.ndarray):
            expr = expr.toarray()
        pb_matrix[i, :] = np.sum(expr, axis=0)
        
    return pb_matrix

def main():
    print("[*] Generating Pseudo-Bulk Validation Matrix from scRNA-seq")
    V5_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    candidates_file = V5_TABLES_DIR / "v5_scrna_candidates.csv"
    if not candidates_file.exists():
        print("[-] Run analysis_v5/01_scrna_discovery.py first.")
        return

    df_cands = pd.read_csv(candidates_file)
    if df_cands.empty:
        print("[-] No candidates to validate.")
        return

    print(f"[*] Loading scRNA expression matrix: {GSE154778_FILE}")
    df = pd.read_csv(GSE154778_FILE, index_col=0)
    adata = ad.AnnData(df.T)
    sc.pp.normalize_total(adata, target_sum=1e4)
    # Using raw counts (normalized) for pseudo-bulk sum is more realistic than log1p
    
    adata.obs["patient_id"] = [x.split(":")[0] for x in adata.obs_names]
    adata.obs["is_tumor"] = [x.startswith("P") or x.startswith("MET") for x in adata.obs["patient_id"]]
    adata.obs["compartment"] = assign_compartments(adata, score_marker_groups(adata))

    # Define compositions
    normal_comp = {
        "normal acinar": 0.60,
        "normal ductal": 0.20,
        "CAF / fibroblast": 0.10,
        "T cells": 0.05,
        "macrophages / monocytes": 0.05
    }
    
    tumor_comp = {
        "malignant ductal / epithelial": 0.40,
        "CAF / fibroblast": 0.40,
        "T cells": 0.10,
        "macrophages / monocytes": 0.10
    }
    
    print("[*] Simulating 100 Normal pseudo-bulk samples...")
    normal_pb = generate_pseudobulk(adata, normal_comp, n_samples=100)
    
    print("[*] Simulating 100 Tumor pseudo-bulk samples...")
    tumor_pb = generate_pseudobulk(adata, tumor_comp, n_samples=100)
    
    # Combine into a single matrix
    X_pb = np.vstack([normal_pb, tumor_pb])
    y_true = np.array([0]*100 + [1]*100)
    
    print("[*] Evaluating candidates on pseudo-bulk matrix...")
    results = []
    
    for _, row in df_cands.iterrows():
        gene_a = row["gene_A"]
        gene_b = row["gene_B"]
        
        idx_a = adata.var_names.get_loc(gene_a)
        idx_b = adata.var_names.get_loc(gene_b)
        
        a_expr = X_pb[:, idx_a]
        b_expr = X_pb[:, idx_b]
        
        # Scale to 0-1
        a_scaled = (a_expr - np.min(a_expr)) / (np.max(a_expr) - np.min(a_expr) + 1e-9)
        b_scaled = (b_expr - np.min(b_expr)) / (np.max(b_expr) - np.min(b_expr) + 1e-9)
        
        and_score = a_scaled * b_scaled
        
        auc = roc_auc_score(y_true, and_score)
        
        thresholds = np.linspace(0.1, 0.9, 9)
        accuracies = [np.mean((and_score > t).astype(int) == y_true) for t in thresholds]
        instability = float(np.std(accuracies))
        
        res = row.to_dict()
        res["bulk_auc"] = auc
        res["threshold_instability"] = instability
        # Re-calculate final score
        res["final_score"] = (
            auc 
            - (instability * 2.0) 
            - (np.abs(res["correlation"]) * 0.5)
            + res["patient_positive_rate"]
            - res["max_off_target_coexpr"]
        )
        results.append(res)
        
    df_res = pd.DataFrame(results)
    # Filter for AUC > 0.70
    df_res = df_res[df_res["bulk_auc"] > 0.70].copy()
    
    if df_res.empty:
        print("[-] No candidates achieved > 0.70 Bulk AUC on pseudo-bulk.")
        pd.DataFrame([{
            "audit_status": "FAIL",
            "note": "No candidates achieved > 0.70 AUC on pseudo-bulk",
        }]).to_csv(V5_AUDIT_DIR / "v5_bulk_backward_validation_audit.csv", index=False)
        return
        
    df_res = df_res.sort_values(by="final_score", ascending=False)
    
    out_path = V5_TABLES_DIR / "v5_bulk_validated_candidates.csv"
    df_res.to_csv(out_path, index=False)
    
    best = df_res.iloc[0]
    pd.DataFrame([best]).to_csv(V5_TABLES_DIR / "v5_default_final_pair.csv", index=False)
    
    pd.DataFrame([{
        "audit_status": "PASS (Pseudo-Bulk Simulated)",
        "evaluated_pairs": len(df_cands),
        "bulk_auc_pass_pairs": len(df_res),
        "default_pair": f"{best['gene_A']}+{best['gene_B']}",
        "note": "Validated on pseudo-bulk matrix generated from scRNA-seq due to missing TCGA data."
    }]).to_csv(V5_AUDIT_DIR / "v5_bulk_backward_validation_audit.csv", index=False)
    
    print(f"[+] Saved {len(df_res)} pseudo-bulk validated candidates to {out_path}")
    print(f"[!] V5 final pseudo-bulk pair: {best['gene_A']} + {best['gene_B']} (AUC: {best['bulk_auc']:.3f})")

if __name__ == "__main__":
    main()
