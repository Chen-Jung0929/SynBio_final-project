#!/usr/bin/env python3
import gzip
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.resolve()
RAW_EXPR = PROJECT_DIR / "data/raw/TcgaTargetGtex_rsem_gene_tpm.gz"
OUT_EXPR = PROJECT_DIR / "data/processed/expression_matrix_v5.csv.gz"

MAPPING = {"ENSG00000084234": "APLP2", "ENSG00000167644": "C19orf33", "ENSG00000111775": "COX6A1", "ENSG00000160213": "CSTB", "ENSG00000051523": "CYBA", "ENSG00000092820": "EZR", "ENSG00000089356": "FXYD3", "ENSG00000013588": "GPRC5A", "ENSG00000233276": "GPX1", "ENSG00000084207": "GSTP1", "ENSG00000227715": "HLA-A", "ENSG00000228964": "HLA-B", "ENSG00000275214": "IFI27", "ENSG00000132470": "ITGB4", "ENSG00000111057": "KRT18", "ENSG00000170421": "KRT8", "ENSG00000282992": "LGALS4", "ENSG00000090382": "LYZ", "ENSG00000145247": "OCIAD2", "ENSG00000112378": "PERP", "ENSG00000189334": "S100A14", "ENSG00000188643": "S100A16", "ENSG00000197956": "S100A6", "ENSG00000130066": "SAT1", "ENSG00000142669": "SH3BGRL3", "ENSG00000267795": "SMIM22", "ENSG00000167642": "SPINT2", "ENSG00000103534": "TMC5", "ENSG00000127324": "TSPAN8", "ENSG00000164405": "UQCRQ", "ENSG00000164924": "YWHAZ"}

def main():
    metadata_path = PROJECT_DIR / "results/tables/sample_metadata.csv"
    if not metadata_path.exists():
        metadata_path = PROJECT_DIR / "results_v1_archive/tables/sample_metadata.csv"
    
    meta = pd.read_csv(metadata_path)
    cohort_samples = set(meta["sample_id"].tolist())
    
    print("[*] Filtering expression matrix for 31 candidate genes...")
    OUT_EXPR.parent.mkdir(parents=True, exist_ok=True)
    
    with gzip.open(RAW_EXPR, "rt") as f:
        header = f.readline().strip().split("\t")
    
    sample_indices = {s: i for i, s in enumerate(header) if s in cohort_samples}
    sorted_samples = sorted(list(sample_indices.keys()))
    
    data = []
    genes = []
    
    with gzip.open(RAW_EXPR, "rt") as f:
        f.readline()
        for line in f:
            fields = line.strip().split("\t")
            ens_id_full = fields[0]
            ens_id = ens_id_full.split('.')[0]
            if ens_id in MAPPING:
                gene_symbol = MAPPING[ens_id]
                vals = [float(fields[sample_indices[s]]) for s in sorted_samples]
                genes.append(gene_symbol)
                data.append(vals)
                
    df_expr = pd.DataFrame(data, index=genes, columns=sorted_samples)
    
    # 2^x - 0.001 adjustment since Xena RSEM is log2(TPM+0.001)
    df_expr = (2 ** df_expr) - 0.001
    # Replace small negative values with 0
    df_expr[df_expr < 0] = 0
    
    df_expr = df_expr.groupby(df_expr.index).mean()
    print(f"[*] Saving filtered matrix of shape {df_expr.shape} to {OUT_EXPR}")
    df_expr.to_csv(OUT_EXPR, compression="gzip")
    
if __name__ == "__main__":
    main()
