# Word Reports Build Status

This document summarizes the generation and styling verification of the editable Word reports.

## Generation Summary

- **English Report**: `reports/word/en/pdac_biosensor_report_en.docx` (Generated successfully, ~920 KB)
- **Traditional Chinese Report**: `reports/word/zh/pdac_biosensor_report_zh.docx` (Generated successfully, ~923 KB)

## Font Properties and Verification

1. **English Body Font**: Times New Roman (Successfully applied, 12pt, 1.5 line spacing).
2. **English Headings**: Arial (Successfully applied, Bold, 18pt/14pt/12pt).
3. **Chinese Body Font**: 標楷體 / DFKai-SB (Successfully applied using `w:eastAsia` CJK XML tags).
4. **Chinese Headings**: Arial / DFKai-SB (Successfully applied).
5. **Monospaced / Symbols**: Courier New (Successfully applied).

## Quality Control Checks

- **Editability**: Both files are fully editable Microsoft Word `.docx` documents.
- **Layout & Margins**: 2.5cm margins applied on all sides (left, right, top, bottom).
- **Line Spacing**: 1.5 line spacing applied.
- **Tables**: All 10 tables (8 main tables + 2 supplementary tables) are fully populated and formatted using standard Word table grids.
- **Figures**: All 7 figures (5 main figures + 2 supplementary sub-figures) are embedded directly within the documents and centered.
- **Limitations**: The 7 critical study caveats are fully present in Section 14 (English) and Section 14 (Chinese).

## Rebuild Command

To rebuild the Word reports, run:
```bash
python3 src/generate_reports.py
```
