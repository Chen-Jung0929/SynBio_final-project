# scRNA-seq and Spatial Transcriptomics Dataset Search Log

This document records the evaluation of public pancreatic ductal adenocarcinoma (PDAC) datasets for validation of the biosensor candidate genes.

## Evaluated Datasets

| Dataset ID | Source Database | Publication | Platform | Cells / Spots | Tumor / Normal | Accepted? | Reason |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **CRA001160 / Peng et al.** | GSA | Peng et al. 2019 | 10x Chromium | 57,530 cells | 24T / 11N | **No** | Raw sequencing files are too large to process in this run; processed h5ad objects are not hosted directly. |
| **GSE154778 / Lin et al.** | GEO | Lin et al. 2020 | 10x Chromium | 42,093 cells | 10T / 6N | **Yes** | Processed digital gene expression matrix is available as a compressed CSV (~28.7 MB) for direct download. |
| **GSE165399 / Werba et al.** | GEO | Werba et al. 2021 | 10x Chromium | 89,000 cells | 22T / 0N | **No** | Large raw tarball of text files; difficult to integrate without metadata. |
| **GSE205013 / PDAC Atlas** | GEO | Steele et al. 2021 | 10x Chromium | 120,000 cells | 48T / 0N | **No** | Large tarball with separate cell/barcode matrices per sample; lacks integrated metadata. |

## Conclusion
We have accepted **GSE154778** as the primary single-cell validation dataset due to its balanced sample design (10 tumors, 6 normal samples) and the availability of a clean, unified count matrix.
