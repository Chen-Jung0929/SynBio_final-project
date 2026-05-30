# Technical Limitations and Excluded Datasets

## Excluded Cohorts and Rationale

1. **GSE71729**:
   * Reason: Agilent microarray format GPL11154 has poor probe alignment to standard ENSEMBL gene IDs. Excluded from final validation to avoid dynamic mapping noise.
2. **TCGA Normal Samples**:
   * Reason: TCGA-PAAD contains only 4 normal pancreas adjacent samples, which is statistically insufficient for a transcriptome-wide discovery cohort.
3. **Spatial Transcriptomics (Raw count matrices)**:
   * Reason: Download size exceeds 25 GB. We instead extracted and represented cell-localization statistics using curated literature data (Peng et al. 2019).
