#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"
V4_AUDIT_DIR = PROJECT_DIR / "results_v4/audit"

def main():
    V4_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("[*] Loading V4 final pair...")
    df_pair = pd.read_csv(V4_TABLES_DIR / "v4_default_final_pair.csv")
    gene_a = df_pair.iloc[0]['gene_A']
    gene_b = df_pair.iloc[0]['gene_B']
    
    # We used these markers to define malignant_ductal / normal_ductal
    # Notice we REMOVED CEACAM5 and MUC1
    ductal_markers = ["EPCAM", "KRT19", "SOX9", "CFTR"]
    
    a_circular = gene_a in ductal_markers
    b_circular = gene_b in ductal_markers
    
    audit_data = [
        {
            "gene": gene_a,
            "used_as_marker": a_circular,
            "marker_list_checked": ", ".join(ductal_markers),
            "status": "FAIL" if a_circular else "PASS"
        },
        {
            "gene": gene_b,
            "used_as_marker": b_circular,
            "marker_list_checked": ", ".join(ductal_markers),
            "status": "FAIL" if b_circular else "PASS"
        }
    ]
    
    df_audit = pd.DataFrame(audit_data)
    out_path = V4_AUDIT_DIR / "v4_circularity_audit.csv"
    df_audit.to_csv(out_path, index=False)
    print(f"[+] Wrote circularity audit to {out_path}")
    print(f"[!] Circularity Audit Result: A={gene_a} ({'FAIL' if a_circular else 'PASS'}), B={gene_b} ({'FAIL' if b_circular else 'PASS'})")

if __name__ == "__main__":
    main()
