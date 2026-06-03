#!/usr/bin/env python3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"
BULK_EXPR_FILE = PROJECT_DIR / "data/processed/expression_matrix.csv.gz"
BULK_META_CANDIDATES = [
    PROJECT_DIR / "data/processed/metadata.csv",
    PROJECT_DIR / "results_v1_archive/tables/sample_metadata.csv",
]


def write_unavailable(status, note):
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{
        "audit_status": status,
        "note": note,
    }]).to_csv(V5_AUDIT_DIR / "v5_bulk_backward_validation_audit.csv", index=False)
    print(f"[-] {status}: {note}")


def load_bulk_inputs():
    if not BULK_EXPR_FILE.exists():
        return None, None, "Missing bulk expression matrix: data/processed/expression_matrix.csv.gz"

    meta_path = next((p for p in BULK_META_CANDIDATES if p.exists()), None)
    if meta_path is None:
        return None, None, "Missing bulk metadata file."

    df_expr = pd.read_csv(BULK_EXPR_FILE, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    return df_expr, df_meta, None


def get_labels(df_meta, sample_ids):
    meta = df_meta.copy()
    if "sample_id" in meta.columns:
        meta = meta.set_index("sample_id")
        meta = meta.loc[[s for s in sample_ids if s in meta.index]]
    elif meta.index.name is None:
        meta.index = meta.index.astype(str)

    label_col = next((c for c in ["group", "condition", "phenotype", "label"] if c in meta.columns), None)
    if label_col is None:
        raise ValueError("No usable label column found in metadata.")

    labels = meta[label_col].astype(str).str.lower()
    y = labels.apply(lambda x: 1 if "pdac" in x or "tumor" in x or "cancer" in x else 0)
    return meta.index.tolist(), y.values


def gene_values(df_expr, gene, sample_ids):
    if gene in df_expr.index:
        return df_expr.loc[gene, sample_ids].values.astype(float)
    if gene in df_expr.columns:
        return df_expr.loc[sample_ids, gene].values.astype(float)
    return None


def evaluate_bulk(gene_a, gene_b, df_expr, sample_ids, y_true):
    a_expr = gene_values(df_expr, gene_a, sample_ids)
    b_expr = gene_values(df_expr, gene_b, sample_ids)
    if a_expr is None or b_expr is None:
        return None

    a_scaled = (a_expr - np.min(a_expr)) / (np.max(a_expr) - np.min(a_expr) + 1e-9)
    b_scaled = (b_expr - np.min(b_expr)) / (np.max(b_expr) - np.min(b_expr) + 1e-9)
    and_score = a_scaled * b_scaled

    auc = roc_auc_score(y_true, and_score)
    thresholds = np.linspace(0.1, 0.9, 9)
    accuracies = [np.mean((and_score > t).astype(int) == y_true) for t in thresholds]

    return {
        "bulk_auc": auc,
        "threshold_instability": float(np.std(accuracies)),
    }


def main():
    V5_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    candidates_file = V5_TABLES_DIR / "v5_scrna_candidates.csv"
    if not candidates_file.exists():
        write_unavailable("MISSING_SCRNA_CANDIDATES", "Run analysis_v5/01_scrna_discovery.py first.")
        return

    df_cands = pd.read_csv(candidates_file)
    if df_cands.empty:
        write_unavailable("NO_SCRNA_CANDIDATES", "No candidate pairs survived the scRNA-first filters.")
        return

    df_expr, df_meta, load_error = load_bulk_inputs()
    if load_error:
        write_unavailable("UNAVAILABLE_BULK_INPUTS", load_error)
        return

    try:
        sample_ids, y_true = get_labels(df_meta, list(df_expr.columns))
    except Exception as exc:
        write_unavailable("UNAVAILABLE_BULK_LABELS", str(exc))
        return

    results = []
    missing_pairs = 0
    for _, row in df_cands.iterrows():
        gene_a = row["gene_A"]
        gene_b = row["gene_B"]
        bulk_metrics = evaluate_bulk(gene_a, gene_b, df_expr, sample_ids, y_true)
        if bulk_metrics is None:
            missing_pairs += 1
            continue
        res = row.to_dict()
        res.update(bulk_metrics)
        results.append(res)

    if not results:
        write_unavailable("NO_MAPPABLE_BULK_CANDIDATES", f"No scRNA-first candidates mapped to the bulk matrix; missing pairs: {missing_pairs}.")
        return

    df_res = pd.DataFrame(results)
    df_res = df_res[df_res["bulk_auc"] > 0.70].copy()
    if df_res.empty:
        write_unavailable("NO_BULK_AUC_PASS", "No scRNA-first candidates achieved bulk AUC > 0.70.")
        return

    df_res["final_score"] = (
        df_res["bulk_auc"]
        - (df_res["threshold_instability"] * 2.0)
        - (np.abs(df_res["correlation"]) * 0.5)
        + df_res["patient_positive_rate"]
        - df_res["max_off_target_coexpr"]
    )
    df_res = df_res.sort_values(by="final_score", ascending=False)

    out_path = V5_TABLES_DIR / "v5_bulk_validated_candidates.csv"
    df_res.to_csv(out_path, index=False)
    pd.DataFrame([{
        "audit_status": "PASS",
        "evaluated_pairs": len(results),
        "missing_pairs": missing_pairs,
        "bulk_auc_pass_pairs": len(df_res),
        "default_pair": f"{df_res.iloc[0]['gene_A']}+{df_res.iloc[0]['gene_B']}",
    }]).to_csv(V5_AUDIT_DIR / "v5_bulk_backward_validation_audit.csv", index=False)

    best = df_res.iloc[0]
    pd.DataFrame([best]).to_csv(V5_TABLES_DIR / "v5_default_final_pair.csv", index=False)
    print(f"[+] Saved {len(df_res)} V5 bulk-validated candidates to {out_path}")
    print(f"[!] V5 current best pair: {best['gene_A']} + {best['gene_B']}")


if __name__ == "__main__":
    main()
