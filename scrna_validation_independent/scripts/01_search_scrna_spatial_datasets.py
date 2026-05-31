#!/usr/bin/env python3
import os
import pandas as pd
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
VALIDATION_DIR = PROJECT_DIR / "scrna_validation_independent"
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
    print("[+] Created independent validation folder structure.")

    # Define metadata search entries
    search_entries = [
        {
            "source": "NCBI GEO Supplementary Files (GSE154778)",
            "url_or_accession": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154778",
            "file_name": "GSE154778_RAW.tar, GSE154778_dgeMtx.csv.gz",
            "contains_cell_barcodes": "yes",
            "contains_cell_type": "no",
            "contains_patient_id": "yes (encoded in barcode prefixes P01-P10, MET01-MET06)",
            "contains_malignant_status": "no",
            "accepted_yes_no": "no",
            "reason": "Only raw and processed count matrices are hosted on the GEO page. No separate cell metadata CSV or Seurat/AnnData annotations are provided by the authors directly in the repository."
        },
        {
            "source": "Genome Medicine Publication Additional Files",
            "url_or_accession": "https://doi.org/10.1186/s13073-020-00776-9",
            "file_name": "Additional file 1, 2, 3",
            "contains_cell_barcodes": "no",
            "contains_cell_type": "yes (gene marker signatures list only, not mapping)",
            "contains_patient_id": "no",
            "contains_malignant_status": "no",
            "accepted_yes_no": "no",
            "reason": "Supplementary materials list top differentially expressed genes and patient summary statistics, but do not provide a cell-level barcode to cell-type classification metadata table."
        }
    ]

    # Save CSV
    df = pd.DataFrame(search_entries)
    df.to_csv(TABLES_DIR / "author_metadata_search_log.csv", index=False)
    print(f"[+] Wrote CSV to tables/author_metadata_search_log.csv")

    # Generate Markdown Search Log
    md_content = """# scRNA-seq and Spatial Transcriptomics Metadata Search Log

This document records the search for author-provided cell barcode metadata and annotations for GSE154778.

## Evaluated Sources

| Source | Accession / URL | File Name | Contains Barcodes? | Contains Cell Type? | Accepted? | Reason |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **NCBI GEO Supplementary** | [GSE154778](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE154778) | RAW.tar, dgeMtx.csv.gz | Yes | No | **No** | Only raw/processed counts matrices are hosted. No cell type annotations. |
| **Genome Medicine Paper** | [DOI: 10.1186/s13073-020-00776-9](https://doi.org/10.1186/s13073-020-00776-9) | Additional Files 1-3 | No | Yes (marker list only) | **No** | Provides tables of differentially expressed signature marker genes but no barcode-to-cell-type mapping table. |

## Conclusion
No author-provided barcode-to-cell-type metadata mapping file is available for direct download. Therefore, we must perform an **independent marker-based annotation** of the single-cell expression matrix, ensuring that the candidate genes (`CEACAM5`, `CST1`, `UBE2S`, `CCR6`) are completely excluded from the classification marker definitions.
"""

    with open(VALIDATION_DIR / "SCRNA_SPATIAL_DATASET_SEARCH_LOG.md", "w") as f:
        f.write(md_content)
    print("[+] Wrote Markdown log to SCRNA_SPATIAL_DATASET_SEARCH_LOG.md")

if __name__ == "__main__":
    main()
