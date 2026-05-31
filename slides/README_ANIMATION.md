# Animation Notes — Computational Derivation Slide Deck

This deck keeps the original warm paper / ink-blue Kami-style, but changes the core results section from “result chart fade-in” to “raw data → computation → visual result → interpretation.” All JavaScript libraries are local under `slides/scripts/`; the deck does not require network access.

## Updated slide sequence

| Slide | Module | What the animation explains |
|---:|---|---|
| 7 | Volcano plot / DE analysis | Expression matrix → PDAC vs normal means → log2FC → FDR → each gene becomes a volcano dot → UBE2S and CCR6 highlighted. |
| 8 | Machine learning as feature prioritization | Gene matrix transposed to samples × genes → labels added → train/test split → classifier outputs probability → AUC interpreted as prioritization, not diagnosis. |
| 9 | SHAP model attribution | One sample expression profile → trained classifier probability → positive/negative feature contributions → SHAP importance logic. |
| 10 | SHAP threshold inference | Expression value → SHAP value → SHAP = 0 crossing → model-inferred activation threshold. |
| 11 | UBE2S + CCR6 scatter / pair selection | Candidate genes → gene pairs → tumor double-high, normal double-high, correlation penalty → selected pair → scatter thresholds and AND ON quadrant. |
| 12 | Hill-equation AND-gate modeling | Raw expression → min-max scaling → H(UBE2S) and H(CCR6) → multiplication → AND-gate output heatmap. |
| 13 | Random-pair control | All filtered genes → random two-gene pair → same AND-gate simulation → AUC → repeat 1,000× → random background distribution compared with UBE2S + CCR6. |
| 14 | Threshold sensitivity analysis | Baseline K_A and K_B → perturb ±10%, ±25%, ±50% → recompute output/AUC/accuracy → AUC heatmap and accuracy caution. |
| 15 | External validation and interpretation | RNA-seq discovery cohort vs microarray external cohort → transfer thresholds → specificity remains high but sensitivity collapses. |

## Required interpretation guardrails included

- **Volcano plot:** x-axis is tumor-vs-normal expression difference; y-axis is statistical confidence; each dot is one gene. The plot prioritizes candidates but does not prove causality.
- **Machine learning:** the classifier is framed as feature prioritization, not clinical diagnosis. The slide explicitly notes that near-perfect AUC may reflect both biology and TCGA-vs-GTEx cohort effects.
- **SHAP:** SHAP explains model decisions and does not prove biological causality.
- **SHAP thresholds / Hill K values:** K_A and K_B are model-inferred expression thresholds, not biochemical dissociation constants or Kd values.
- **Pair selection:** UBE2S + CCR6 is selected by pair scoring, with the caution that correlation = 0.714 means functionally divergent but not statistically orthogonal.
- **Random-pair control:** tests statistical non-randomness against chance, not biological causality.
- **Threshold sensitivity:** tests computational robustness against parameter uncertainty, not biochemical affinity validation.
- **External validation:** tests dataset/platform shift and supports the interpretation “high-specificity computational candidate, not validated sensitive PDAC detector.”

## Animation libraries

All libraries are local and minimal:

- `scripts/d3.min.js` — SVG chart construction and axes.
- `scripts/anime.min.js` — restrained stepwise reveals and derivation timing.
- `scripts/rough-notation.js` — retained locally for sketch-style annotation compatibility, though the revised slides mostly use direct labels and lines.

No framework or dashboard UI was added. MathJax CDN and Google font imports were removed so the deck can run offline.

## Reduced-motion mode

Reduced-motion mode is available in two ways:

1. Click the top-right **Reduced Motion** button.
2. Press the **R** key.

When enabled, the `body.reduced-motion` class disables CSS transitions and the animation functions render final states immediately instead of sequencing the derivations.

## How to open locally

From the repository root:

```bash
cd slides
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

You can also open `slides/index.html` directly in a browser, but the local server path is usually more reliable for local assets.

## Known data / figure limitations

- The explanatory animations use compact schematic data rather than loading the full 58,581-gene matrix in the browser.
- Existing analysis tables under `reports/latex/shared/tables/` provide the reported metrics (AND-gate performance, random-pair control, threshold sensitivity, and external validation), but the browser animation currently renders teaching-scale plots instead of exact full-resolution figures.
- If final publication figures are required, the schematic point clouds can be replaced with JSON exports from the Python analysis pipeline while preserving the same animation sequence.
