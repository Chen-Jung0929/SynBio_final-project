# V5 Next-Gen Pipeline Proposal: Single-Cell First Discovery

## 1. Background & Rationale
Throughout V1 to V4, our logic for discovering synthetic biology biosensor inputs (AND gates) has been:
1. **Discover** candidates using Bulk RNA-seq (TCGA, GTEx).
2. **Filter** based on clinical Bulk datasets (GSE62452, GSE28735).
3. **Validate** post-hoc on Single-Cell RNA-seq (GSE154778).

The V4 circularity audit decisively proved that this pipeline is fundamentally limited. Bulk RNA-seq inherently "averages" gene expression across the tumor microenvironment (TME). When we strictly enforce single-cell compartmentalization (0% in CAFs/Immune cells, >90% in malignant epithelial cells), **zero pairs from the top 200 bulk candidates successfully pass.**

## 2. The V5 Reversal Strategy
To find a clinically viable and biologically safe logic-gated biosensor, we must **reverse the pipeline**.

### Phase 1: Single-Cell Discovery (The "Perfect Biosensor" Filter)
We begin with scRNA-seq matrices (e.g., GSE154778 and others).
1. Isolate the true `malignant ductal / epithelial` compartment.
2. Isolate all off-target compartments (`CAF`, `T-cells`, `B-cells`, `Macrophages`, `Endothelial`, `Normal Ductal/Acinar`).
3. Compute the theoretical **AND-gate activation rate** for all possible gene pairs `(Gene A AND Gene B)` across single cells.
4. **Strict Constraint:** Keep only pairs that achieve > 80% co-expression in the target compartment AND < 5% co-expression in all off-target compartments.

### Phase 2: Bulk Generalization (The "Clinical Robustness" Filter)
Once we have a shortlist of pairs that are perfectly compartmentalized at the cellular level, we validate them on Bulk RNA-seq.
1. Run the surviving pairs through the TCGA-PAAD vs. GTEx pipeline.
2. Run them through the GSE62452 and GSE28735 validation datasets.
3. Why? Because a biosensor must also be consistently expressed across a wide population of patients, not just the single-cell cohorts.

## 3. Request for Codex Review
Codex, please review this V5 paradigm shift. 
* Do you agree with the sequence inversion?
* Are there other single-cell datasets (e.g., from `cCREs` or spatial transcriptomics) we should integrate into Phase 1 to ensure even tighter localization?
* I am ready to begin scaffolding `analysis_v5/` once we align on the methodology.
