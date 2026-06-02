#!/usr/bin/env python3
import os
import sys
import yaml
import requests
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def download_file(url, dest_path):
    print(f"[*] Downloading {url} to {dest_path}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Check if download is resumed or from scratch
    if dest_path.exists():
        print(f"[+] File already exists at {dest_path}. Skipping download.")
        return
        
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024 * 1024  # 1MB blocks
        downloaded = 0
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        sys.stdout.write(f"\r    Progress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({percent:.1f}%)")
                    else:
                        sys.stdout.write(f"\r    Progress: {downloaded / (1024*1024):.1f} MB")
                    sys.stdout.flush()
        print("\n[+] Download completed successfully!")
    except Exception as e:
        print(f"\n[-] Failed to download {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()  # Clean up partial download
        sys.exit(1)

def main():
    config = load_config()
    raw_dir = Path(__file__).parent.parent / config["data"]["raw_dir"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    phenotype_url = config["data"]["phenotype_url"]
    expression_url = config["data"]["expression_url"]
    
    phenotype_path = raw_dir / "TcgaTargetGTEX_phenotype.txt.gz"
    expression_path = raw_dir / "TcgaTargetGtex_rsem_gene_tpm.gz"
    
    # Download files
    download_file(phenotype_url, phenotype_path)
    download_file(expression_url, expression_path)

if __name__ == "__main__":
    main()
