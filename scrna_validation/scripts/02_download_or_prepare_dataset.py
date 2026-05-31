#!/usr/bin/env python3
import os
import urllib.request
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_RAW_DIR = PROJECT_DIR / "scrna_validation/data/raw"
DOWNLOAD_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE154nnn/GSE154778/suppl/GSE154778_dgeMtx.csv.gz"
TARGET_FILE = DATA_RAW_DIR / "GSE154778_dgeMtx.csv.gz"

def main():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    if TARGET_FILE.exists():
        print(f"[+] File already exists at {TARGET_FILE}. Skipping download.")
        return
        
    print(f"[*] Downloading {DOWNLOAD_URL} to {TARGET_FILE}...")
    try:
        # Define progress callback
        def report_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = (downloaded / total_size) * 100 if total_size > 0 else 0
            if block_num % 100 == 0:
                print(f"[*] Downloaded: {downloaded / 1024**2:.2f} MB / {total_size / 1024**2:.2f} MB ({percent:.1f}%)")

        urllib.request.urlretrieve(DOWNLOAD_URL, TARGET_FILE, report_hook)
        print(f"[+] Download completed successfully. Saved to {TARGET_FILE}")
    except Exception as e:
        print(f"[-] Download failed: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
