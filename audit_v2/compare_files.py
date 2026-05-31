#!/usr/bin/env python3
import hashlib
import pandas as pd
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.resolve()
ORIG_DIR = PROJECT_DIR / "results_v2/tables"
RERUN_DIR = PROJECT_DIR / "audit_v2/results_rerun/tables"
OUT_DIR = PROJECT_DIR / "audit_v2/tables"

FILES_TO_COMPARE = [
    "final_candidate_pair_v2.csv",
    "gene_pair_scores_v2.csv",
    "table_final_pair_performance_all_datasets.csv",
    "and_gate_performance_v2.csv",
    "shap_thresholds_consensus_genes.csv",
    "model_consensus_feature_ranking.csv"
]

def get_file_stats(filepath):
    if not filepath.exists():
        return "N/A", 0, "File missing"
    
    # Compute SHA256
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    sha_str = sha256_hash.hexdigest()
    
    # Row count (excluding header)
    try:
        df = pd.read_csv(filepath)
        row_count = len(df)
    except Exception as e:
        row_count = 0
        
    return sha_str, row_count, "Success"

def main():
    records = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for filename in FILES_TO_COMPARE:
        orig_file = ORIG_DIR / filename
        rerun_file = RERUN_DIR / filename
        
        orig_sha, orig_rows, orig_status = get_file_stats(orig_file)
        rerun_sha, rerun_rows, rerun_status = get_file_stats(rerun_file)
        
        identical = "yes" if orig_sha == rerun_sha and orig_sha != "N/A" else "no"
        
        notes = ""
        if orig_status != "Success":
            notes += f"Original: {orig_status}. "
        if rerun_status != "Success":
            notes += f"Rerun: {rerun_status}. "
        if identical == "yes":
            notes += "100% identical match."
        else:
            notes += "SHA256 mismatch."
            
        records.append({
            "file": filename,
            "identical_yes_no": identical,
            "row_count_original": orig_rows,
            "row_count_rerun": rerun_rows,
            "sha256_original": orig_sha,
            "sha256_rerun": rerun_sha,
            "notes": notes.strip()
        })
        
    df_comparison = pd.DataFrame(records)
    df_comparison.to_csv(OUT_DIR / "reproducibility_file_comparison.csv", index=False)
    print("[+] Wrote comparison to reproducibility_file_comparison.csv")
    print(df_comparison[["file", "identical_yes_no", "row_count_original", "row_count_rerun"]])

if __name__ == "__main__":
    main()
