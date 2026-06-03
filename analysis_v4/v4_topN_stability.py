#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_RESULTS_FILE = PROJECT_DIR / "results_v4/tables/v4_pair_search_results.csv"
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"

def main():
    print("[*] Generating Top-N stability summary for V4...")
    df = pd.read_csv(V4_RESULTS_FILE)
    
    top_ns = [20, 50, 100, 200]
    records = []
    
    for n in top_ns:
        # Assuming the CSV is already sorted by pair_score descending
        top_df = df.head(n)
        
        # Stability metrics
        median_pair_score = top_df['pair_score'].median()
        median_perf_score = top_df['performance_score'].median()
        median_scrna_score = top_df['scrna_score'].median()
        median_target_coexpr = top_df['target_coexpr_est'].median()
        median_off_target = top_df['max_off_target_coexpr_est'].median()
        
        most_common_off_target = top_df['max_off_target_compartment'].mode()[0] if not top_df.empty else "N/A"
        
        # Output the N subset
        top_df.to_csv(V4_TABLES_DIR / f"v4_pair_search_top{n}.csv", index=False)
        
        records.append({
            "top_N": n,
            "median_pair_score": median_pair_score,
            "median_performance_score": median_perf_score,
            "median_scrna_score": median_scrna_score,
            "median_target_coexpr": median_target_coexpr,
            "median_off_target_coexpr": median_off_target,
            "most_common_off_target_compartment": most_common_off_target
        })
        
    df_summary = pd.DataFrame(records)
    out_path = V4_TABLES_DIR / "v4_topN_stability_summary.csv"
    df_summary.to_csv(out_path, index=False)
    print(f"[+] Wrote stability summary to {out_path}")

if __name__ == "__main__":
    main()
