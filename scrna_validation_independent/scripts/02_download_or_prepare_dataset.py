#!/usr/bin/env python3
import shutil
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent.parent.resolve()
SRC_FILE = PROJECT_DIR / "scrna_validation/data/raw/GSE154778_dgeMtx.csv.gz"
DEST_DIR = PROJECT_DIR / "scrna_validation_independent/data/raw"
DEST_FILE = DEST_DIR / "GSE154778_dgeMtx.csv.gz"

def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    
    if DEST_FILE.exists():
        print(f"[+] File already exists at {DEST_FILE}. Skipping copy.")
        return

    if SRC_FILE.exists():
        print(f"[*] Copying expression matrix from {SRC_FILE} to {DEST_FILE}...")
        shutil.copy(SRC_FILE, DEST_FILE)
        print("[+] Copy completed successfully.")
    else:
        print(f"[-] Source file not found at {SRC_FILE}. Please check download.")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
