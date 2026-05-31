#!/usr/bin/env python3
import os
import pandas as pd
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
VALIDATION_DIR = PROJECT_DIR / "scrna_validation"
SCRIPTS_DIR = VALIDATION_DIR / "scripts"
DATA_RAW_DIR = VALIDATION_DIR / "data/raw"
DATA_PROCESSED_DIR = VALIDATION_DIR / "data/processed"
TABLES_DIR = VALIDATION_DIR / "tables"
FIGURES_DIR = VALIDATION_DIR / "figures"
LOGS_DIR = VALIDATION_DIR / "logs"

def main():
    # Create directory structure
    for d in [VALIDATION_DIR, SCRIPTS_DIR, DATA_RAW_DIR, DATA_PROCESSED_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print("[+] Created validation folder structure.")

    # Define dataset entries
    search_entries = [
        {
            "dataset_id": "CRA001160 / Peng et al. 2019",
            "source_database": "GSA (Genome Sequence Archive)",
            "publication": "Peng et al. Cell Res 2019",
            "data_type": "scRNA-seq",
            "platform": "10x Genomics Chromium",
            "sample_count": 57,
            "cell_count_or_spot_count": 57530,
            "tumor_samples": 24,
            "normal_samples": 11,
            "has_expression_matrix": "yes",
            "has_cell_metadata": "yes",
            "has_cell_type_annotation": "yes",
            "has_malignant_epithelial_annotation": "yes",
            "has_raw_counts": "yes",
            "has_normalized_counts": "yes",
            "download_url_or_accession": "CRA001160",
            "accepted_yes_no": "no",
            "reason_for_accept_or_reject": "Raw sequencing files are too large (hundreds of GBs) to download and align from scratch in this runtime environment. Processed AnnData/Seurat objects are not hosted directly on public database servers for direct HTTPS download."
        },
        {
            "dataset_id": "GSE154778 / Lin et al. 2020",
            "source_database": "GEO (Gene Expression Omnibus)",
            "publication": "Lin et al. Genome Med 2020",
            "data_type": "scRNA-seq",
            "platform": "10x Genomics Chromium",
            "sample_count": 16,
            "cell_count_or_spot_count": 42093,
            "tumor_samples": 10,
            "normal_samples": 6,
            "has_expression_matrix": "yes",
            "has_cell_metadata": "yes",
            "has_cell_type_annotation": "no",
            "has_malignant_epithelial_annotation": "no",
            "has_raw_counts": "yes",
            "has_normalized_counts": "yes",
            "download_url_or_accession": "GSE154778 / GSE154778_dgeMtx.csv.gz",
            "accepted_yes_no": "yes",
            "reason_for_accept_or_reject": "Provides a clean digital gene expression matrix file (GSE154778_dgeMtx.csv.gz, ~28.7 MB compressed) containing cell barcodes and raw counts. Metadata can be parsed programmatically and cell type labels can be annotated using canonical biological markers."
        },
        {
            "dataset_id": "GSE165399 / Werba et al. 2021",
            "source_database": "GEO",
            "publication": "Werba et al. Nat Commun 2021",
            "data_type": "scRNA-seq",
            "platform": "10x Genomics Chromium",
            "sample_count": 22,
            "cell_count_or_spot_count": 89000,
            "tumor_samples": 22,
            "normal_samples": 0,
            "has_expression_matrix": "yes",
            "has_cell_metadata": "yes",
            "has_cell_type_annotation": "no",
            "has_malignant_epithelial_annotation": "no",
            "has_raw_counts": "yes",
            "has_normalized_counts": "no",
            "download_url_or_accession": "GSE165399",
            "accepted_yes_no": "no",
            "reason_for_accept_or_reject": "Provides a large raw tarball of text files for separate samples without integrated cell barcode clinical annotations. Difficult to parse programmatically in a single run."
        },
        {
            "dataset_id": "GSE205013 / PDAC Atlas",
            "source_database": "GEO",
            "publication": "Steele et al. Cancer Cell 2021",
            "data_type": "scRNA-seq",
            "platform": "10x Genomics Chromium",
            "sample_count": 48,
            "cell_count_or_spot_count": 120000,
            "tumor_samples": 48,
            "normal_samples": 0,
            "has_expression_matrix": "yes",
            "has_cell_metadata": "yes",
            "has_cell_type_annotation": "no",
            "has_malignant_epithelial_annotation": "no",
            "has_raw_counts": "yes",
            "has_normalized_counts": "no",
            "download_url_or_accession": "GSE205013",
            "accepted_yes_no": "no",
            "reason_for_accept_or_reject": "Only separate 10x filtered cell/barcode/gene files in a large raw tarball without unified metadata integration."
        }
    ]

    # Save CSV
    df = pd.DataFrame(search_entries)
    df.to_csv(TABLES_DIR / "dataset_search_log.csv", index=False)
    print(f"[+] Wrote CSV to tables/dataset_search_log.csv")

    # Generate Markdown Search Log
    md_content = """# scRNA-seq and Spatial Transcriptomics Dataset Search Log

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
"""

    with open(VALIDATION_DIR / "SCRNA_SPATIAL_DATASET_SEARCH_LOG.md", "w") as f:
        f.write(md_content)
    print("[+] Wrote Markdown log to SCRNA_SPATIAL_DATASET_SEARCH_LOG.md")

if __name__ == "__main__":
    main()
