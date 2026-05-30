# Dataset Search Log for Independent Final Validation

We systematically searched the Gene Expression Omnibus (GEO) for Pancreatic Cancer datasets containing both tumor and healthy/adjacent-normal controls.

## Candidate Datasets Evaluated

1. **GSE62452**:
   * Size: 130 samples (69 PDAC tumor, 61 adjacent normal).
   * Status: **ACCEPTED** as same-cohort tumor/normal validation dataset (Stage 2).
2. **GSE28735**:
   * Size: 90 samples (45 matching PDAC tumor and adjacent normal pairs from 45 patients).
   * Platform: Affymetrix GPL6244 (same as GSE62452, facilitating high-quality annotation).
   * Status: **ACCEPTED** as independent final validation dataset (Stage 3).
3. **GSE71729**:
   * Size: 191 samples (145 tumor, 46 normal).
   * Platform: Agilent microarray GPL11154.
   * Status: **REJECTED** because GPL11154 lacks comprehensive annotations for critical immunogenetic and cell-cycle probes compared to GPL6244, and matching cross-platform probes have lower correlation.
