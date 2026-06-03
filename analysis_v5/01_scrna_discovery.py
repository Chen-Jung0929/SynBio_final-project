#!/usr/bin/env python3
import pandas as pd
import numpy as np
import scanpy as sc
import anndata as ad
from pathlib import Path


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_DIR = PROJECT_DIR / "analysis_v4"
GSE154778_FILE = V4_DIR / "GSE154778_dgeMtx.csv.gz"
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"

TARGET_PAIR_MIN = 0.60
POOLED_OFF_TARGET_MAX = 0.10
PATIENT_POSITIVE_MIN = 0.05
THRESHOLD_PROFILE = "exploratory_relaxed_v5_0p60_target_0p10_pooled_offtarget"

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


def safe_corr(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    corr = np.corrcoef(a, b)[0, 1]
    return 0.0 if np.isnan(corr) else float(corr)


def main():
    V5_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[*] Loading scRNA expression matrix: {GSE154778_FILE}")
    df = pd.read_csv(GSE154778_FILE, index_col=0)
    print(f"[+] Loaded matrix of shape: {df.shape}")

    adata = ad.AnnData(df.T)
    sc.pp.filter_cells(adata, min_genes=50)
    sc.pp.filter_genes(adata, min_cells=10)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    adata.obs["patient_id"] = [x.split(":")[0] for x in adata.obs_names]
    adata.obs["is_tumor"] = [x.startswith("P") or x.startswith("MET") for x in adata.obs["patient_id"]]
    adata.obs["compartment"] = assign_compartments(adata, score_marker_groups(adata))

    target_mask = (adata.obs["compartment"] == "malignant ductal / epithelial").values
    off_target_mask = ~target_mask
    n_target = int(np.sum(target_mask))
    n_off_target = int(np.sum(off_target_mask))
    print(f"[*] Target cells: {n_target}, off-target cells: {n_off_target}")

    if n_target == 0 or n_off_target == 0:
        pd.DataFrame().to_csv(V5_TABLES_DIR / "v5_scrna_candidates.csv", index=False)
        pd.DataFrame([{
            "audit_status": "NO_TARGET_OR_OFFTARGET_CELLS",
            "n_target_cells": n_target,
            "n_off_target_cells": n_off_target,
            "annotation_version": "v5_heuristic_marker_metadata"
        }]).to_csv(V5_AUDIT_DIR / "v5_scrna_discovery_audit.csv", index=False)
        print("[-] Cannot run V5 discovery without both target and off-target cells.")
        return

    expr_matrix = adata.X if isinstance(adata.X, np.ndarray) else adata.X.toarray()
    expr_bool = expr_matrix > 0
    target_bool = expr_bool[target_mask]
    off_target_bool = expr_bool[off_target_mask]

    target_gene_pct = np.mean(target_bool, axis=0)
    marker_set = {g for genes in MARKER_GENES.values() for g in genes}
    essential_prefixes = ("RPL", "RPS", "MRPL", "MRPS", "MT-")
    essential_exact = {"ACTB", "GAPDH", "TUBB", "TUBA1A", "B2M", "PPIA"}

    candidate_indices = []
    for idx, gene in enumerate(adata.var_names):
        if target_gene_pct[idx] <= 0.15:
            continue
        if gene in marker_set or gene in essential_exact or gene.startswith(essential_prefixes):
            continue
        candidate_indices.append(idx)

    print(f"[+] Candidate genes after single-gene filters: {len(candidate_indices)}")
    filtered_bool = expr_bool[:, candidate_indices]
    target_filtered = filtered_bool[target_mask]
    off_filtered = filtered_bool[off_target_mask]

    target_compartments = adata.obs.loc[target_mask, ["patient_id"]]
    off_compartments = adata.obs.loc[off_target_mask, "compartment"]
    off_compartment_names = sorted(off_compartments.unique())

    records = []
    for i in range(len(candidate_indices)):
        a_target = target_filtered[:, i:i + 1]
        b_target = target_filtered[:, i + 1:]
        if b_target.shape[1] == 0:
            continue

        target_pcts = np.sum(a_target & b_target, axis=0) / n_target
        target_pass = np.where(target_pcts >= TARGET_PAIR_MIN)[0]
        if len(target_pass) == 0:
            continue

        global_j = target_pass + i + 1
        a_off = off_filtered[:, i:i + 1]
        b_off = off_filtered[:, global_j]
        pooled_off_pcts = np.sum(a_off & b_off, axis=0) / n_off_target

        for local_idx, off_pct in enumerate(pooled_off_pcts):
            if off_pct > POOLED_OFF_TARGET_MAX:
                continue
            j = global_j[local_idx]
            pair_expr = filtered_bool[:, i] & filtered_bool[:, j]
            target_pair_expr = pair_expr[target_mask]

            patient_rates = []
            for patient_id in sorted(target_compartments["patient_id"].unique()):
                patient_mask = (target_compartments["patient_id"].values == patient_id)
                if np.sum(patient_mask) == 0:
                    continue
                patient_rates.append(np.mean(target_pair_expr[patient_mask] > 0))
            patient_positive_rate = float(np.mean(np.array(patient_rates) >= PATIENT_POSITIVE_MIN)) if patient_rates else 0.0

            max_off_pct = 0.0
            max_off_ct = "None"
            for ct in off_compartment_names:
                ct_mask = (off_compartments.values == ct)
                if np.sum(ct_mask) == 0:
                    continue
                ct_pct = float(np.mean(pair_expr[off_target_mask][ct_mask]))
                if ct_pct > max_off_pct:
                    max_off_pct = ct_pct
                    max_off_ct = ct

            gene_a = adata.var_names[candidate_indices[i]]
            gene_b = adata.var_names[candidate_indices[j]]
            records.append({
                "gene_A": gene_a,
                "gene_B": gene_b,
                "target_coexpr": float(target_pcts[target_pass[local_idx]]),
                "pooled_off_target_coexpr": float(off_pct),
                "max_off_target_coexpr": max_off_pct,
                "max_off_target_compartment": max_off_ct,
                "patient_positive_rate": patient_positive_rate,
                "correlation": safe_corr(filtered_bool[:, i].astype(float), filtered_bool[:, j].astype(float)),
                "annotation_version": "v5_heuristic_marker_metadata",
                "threshold_profile": THRESHOLD_PROFILE,
            })

    df_results = pd.DataFrame(records)
    if not df_results.empty:
        df_results = df_results.sort_values(
            by=["patient_positive_rate", "target_coexpr", "max_off_target_coexpr"],
            ascending=[False, False, True],
        )

    out_path = V5_TABLES_DIR / "v5_scrna_candidates.csv"
    df_results.to_csv(out_path, index=False)
    pd.DataFrame([{
        "audit_status": "PASS",
        "n_target_cells": n_target,
        "n_off_target_cells": n_off_target,
        "candidate_genes": len(candidate_indices),
        "candidate_pairs": len(df_results),
        "annotation_version": "v5_heuristic_marker_metadata",
        "threshold_profile": THRESHOLD_PROFILE,
        "target_pair_min": TARGET_PAIR_MIN,
        "pooled_off_target_max": POOLED_OFF_TARGET_MAX,
        "patient_positive_min": PATIENT_POSITIVE_MIN,
        "note": "scRNA-first discovery uses heuristic marker and metadata labels; downstream validation is still required."
    }]).to_csv(V5_AUDIT_DIR / "v5_scrna_discovery_audit.csv", index=False)
    print(f"[+] Saved {len(df_results)} scRNA-first candidates to {out_path}")


if __name__ == "__main__":
    main()
