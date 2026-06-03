#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
V4_TABLES_DIR = PROJECT_DIR / "results_v4/tables"
REPORTS_DIR = PROJECT_DIR / "reports_v4"

def generate_reports():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    df_best = pd.read_csv(V4_TABLES_DIR / "v4_default_final_pair.csv")
    best = df_best.iloc[0]
    
    gene_a = best['gene_A']
    gene_b = best['gene_B']
    sc_score = best['scrna_score']
    bulk_score = best['performance_score']
    target_co = best['target_coexpr_est']
    off_target_co = best['max_off_target_coexpr_est']
    
    report_md = f"""# V4 Final Report: Biologically Integrated Candidate Search

## 1. Overview
The V3 candidate pair (`PKM` + `ADAM22`) had a stronger locked bulk-validation audit than earlier candidates, but it failed the core cell-level biosensor requirement: both inputs were rarely co-expressed in the putative malignant ductal epithelial compartment.

To address this biological misalignment, the V4 pipeline integrates single-cell compartment evidence directly into pair ranking instead of treating scRNA-seq as only a post-hoc validation step.

## 2. V4 Methodology
We extracted scRNA-seq expression summaries for the top 200 model-consensus genes across major cell types, including malignant ductal / epithelial cells, normal ductal cells, acinar cells, CAFs, T cells, Tregs, B cells, macrophages, endothelial cells, and mast cells.

During the pairwise search over 19,900 combinations, V4 integrated a **single-cell compartment score**:
* **Target Co-expression Estimate**: `min(pct_expressing(Gene A), pct_expressing(Gene B))` in malignant ductal cells.
* **Off-Target Co-expression Estimate**: Max `min(pct(A), pct(B))` across all stromal/immune cell types.
* **scRNA Score**: `Target Co-expression - (5.0 * Off-Target Co-expression)`
* **Final Pair Score**: `Bulk Performance - Redundancy Penalty - Instability Penalty + (5.0 * scRNA Score)`

The intent is to reward target-compartment co-expression while penalizing immune, stromal, and normal-compartment leakage. Each component remains visible in the output table so the final score can be audited.

## 3. V4 Selected Candidate Pair
* **Gene A**: `{gene_a}`
* **Gene B**: `{gene_b}`

### Scores
* **Bulk Performance Score**: {bulk_score:.4f}
* **scRNA Target Co-expression (Malignant Ductal)**: {target_co * 100:.2f}%
* **scRNA Max Off-Target Co-expression**: {off_target_co * 100:.2f}%
* **Integrated scRNA Score**: {sc_score:.4f}

## 4. Interpretation
V4 improves the biological alignment of the selected pair by prioritizing strong malignant ductal / epithelial co-expression. This is an important correction to the V3 failure mode.

However, the result is still a computational candidate, not a validated biosensor. The selected pair retains measurable off-target co-expression, moderate tumor-gene correlation, and limited GSE62452 specificity. It should therefore be treated as a stronger hypothesis for follow-up design, not as a completed diagnostic detector or experimentally validated synthetic circuit.

## 5. Next Required Work
* Audit the full single-cell prior and confirm that cell-type labels were not circularly defined by candidate genes.
* Report which off-target compartment produces the maximum co-expression signal.
* Re-evaluate locked GSE28735 performance for the V4 pair.
* Add patient-level target-compartment prevalence.
* Define wet-lab feasibility for sensing `OCIAD2` and `CEACAM5` as implementable circuit inputs.
"""
    
    with open(REPORTS_DIR / "V4_FINAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"[+] Wrote V4 Final Report to {REPORTS_DIR / 'V4_FINAL_REPORT.md'}")

if __name__ == "__main__":
    generate_reports()
