#!/bin/bash
set -e

export PATH="/Users/Janet/Library/TinyTeX/bin/universal-darwin:$PATH"

# Base directories
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
EN_DIR="$BASE_DIR/en"
ZH_DIR="$BASE_DIR/zh"

echo "=== Compiling English Report ==="
cd "$EN_DIR"
xelatex -interaction=nonstopmode pdac_biosensor_report_en
if [ -f pdac_biosensor_report_en.bcf ]; then
    biber pdac_biosensor_report_en || echo "Biber compilation failed, continuing anyway..."
fi
xelatex -interaction=nonstopmode pdac_biosensor_report_en
xelatex -interaction=nonstopmode pdac_biosensor_report_en

echo "=== Compiling English Revised Report ==="
xelatex -interaction=nonstopmode pdac_biosensor_report_en_revised
if [ -f pdac_biosensor_report_en_revised.bcf ]; then
    biber pdac_biosensor_report_en_revised || echo "Biber compilation failed, continuing anyway..."
fi
xelatex -interaction=nonstopmode pdac_biosensor_report_en_revised
xelatex -interaction=nonstopmode pdac_biosensor_report_en_revised

echo "=== Compiling Chinese Report ==="
cd "$ZH_DIR"
xelatex -interaction=nonstopmode pdac_biosensor_report_zh
if [ -f pdac_biosensor_report_zh.bcf ]; then
    biber pdac_biosensor_report_zh || echo "Biber compilation failed, continuing anyway..."
fi
xelatex -interaction=nonstopmode pdac_biosensor_report_zh
xelatex -interaction=nonstopmode pdac_biosensor_report_zh

echo "=== Compiling Chinese Revised Report ==="
xelatex -interaction=nonstopmode pdac_biosensor_report_zh_revised
if [ -f pdac_biosensor_report_zh_revised.bcf ]; then
    biber pdac_biosensor_report_zh_revised || echo "Biber compilation failed, continuing anyway..."
fi
xelatex -interaction=nonstopmode pdac_biosensor_report_zh_revised
xelatex -interaction=nonstopmode pdac_biosensor_report_zh_revised

echo "=== LaTeX compilation finished! ==="
