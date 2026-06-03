#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).parent.parent.resolve()
V5_TABLES_DIR = PROJECT_DIR / "results_v5/tables"
V5_AUDIT_DIR = PROJECT_DIR / "results_v5/audit"


PROFILES = [
    ("strict_0p80_target_0p05_pooled_offtarget", 0.80, 0.05, "pooled_off_target_coexpr"),
    ("strict_0p80_target_0p05_max_compartment_offtarget", 0.80, 0.05, "max_off_target_coexpr"),
    ("intermediate_0p70_target_0p10_pooled_offtarget", 0.70, 0.10, "pooled_off_target_coexpr"),
    ("intermediate_0p70_target_0p10_max_compartment_offtarget", 0.70, 0.10, "max_off_target_coexpr"),
    ("relaxed_0p60_target_0p10_pooled_offtarget", 0.60, 0.10, "pooled_off_target_coexpr"),
    ("relaxed_0p60_target_0p10_max_compartment_offtarget", 0.60, 0.10, "max_off_target_coexpr"),
]


def main():
    V5_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    candidates_file = V5_TABLES_DIR / "v5_scrna_candidates.csv"
    if not candidates_file.exists():
        pd.DataFrame([{
            "profile": "all",
            "audit_status": "MISSING_SCRNA_CANDIDATES",
            "passing_pairs": 0,
            "note": "Run analysis_v5/01_scrna_discovery.py first."
        }]).to_csv(V5_AUDIT_DIR / "v5_threshold_profile_summary.csv", index=False)
        print("[-] Missing V5 scRNA candidates.")
        return

    df = pd.read_csv(candidates_file)
    records = []
    for profile, target_min, off_max, off_col in PROFILES:
        if df.empty:
            passing = df.copy()
        else:
            passing = df[(df["target_coexpr"] >= target_min) & (df[off_col] <= off_max)].copy()

        if passing.empty:
            records.append({
                "profile": profile,
                "target_min": target_min,
                "off_target_max": off_max,
                "off_target_metric": off_col,
                "passing_pairs": 0,
                "top_pair": "",
                "top_target_coexpr": "",
                "top_off_target": "",
                "top_max_off_target_compartment": "",
                "top_patient_positive_rate": "",
                "audit_status": "NO_PASSING_PAIRS",
            })
            continue

        top = passing.sort_values(
            by=["patient_positive_rate", "target_coexpr", off_col],
            ascending=[False, False, True],
        ).iloc[0]
        records.append({
            "profile": profile,
            "target_min": target_min,
            "off_target_max": off_max,
            "off_target_metric": off_col,
            "passing_pairs": len(passing),
            "top_pair": f"{top['gene_A']}+{top['gene_B']}",
            "top_target_coexpr": top["target_coexpr"],
            "top_off_target": top[off_col],
            "top_max_off_target_compartment": top["max_off_target_compartment"],
            "top_patient_positive_rate": top["patient_positive_rate"],
            "audit_status": "PASSING_PAIRS_FOUND",
        })

    out_path = V5_AUDIT_DIR / "v5_threshold_profile_summary.csv"
    pd.DataFrame(records).to_csv(out_path, index=False)
    print(f"[+] Wrote V5 threshold profile audit to {out_path}")


if __name__ == "__main__":
    main()
