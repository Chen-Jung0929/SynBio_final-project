# scRNA-seq and Spatial Transcriptomics Metadata Search Log

This document records the search for author-provided cell barcode metadata and annotations for GSE154778.

## Evaluated Sources

| Source | Accession / URL | File Name | Contains Barcodes? | Contains Cell Type? | Accepted? | Reason |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **NCBI GEO Supplementary** | [GSE154778](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154778) | RAW.tar, dgeMtx.csv.gz | Yes | No | **No** | Only raw/processed counts matrices are hosted. No cell type annotations. |
| **Genome Medicine Paper** | [DOI: 10.1186/s13073-020-00776-9](https://doi.org/10.1186/s13073-020-00776-9) | Additional Files 1-3 | No | Yes (marker list only) | **No** | Provides tables of differentially expressed signature marker genes but no barcode-to-cell-type mapping table. |

## Conclusion
No author-provided barcode-to-cell-type metadata mapping file is available for direct download. Therefore, we must perform an **independent marker-based annotation** of the single-cell expression matrix, ensuring that the candidate genes (`CEACAM5`, `CST1`, `UBE2S`, `CCR6`) are completely excluded from the classification marker definitions.
