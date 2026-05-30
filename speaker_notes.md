# Speaker Notes — PDAC AND-Gate Biosensor Project Presentation

Use these notes to guide your narrative during the slide presentation. Each slide's notes describe the key scientific concepts and explain how to walk the audience through the on-screen animations.

---

## Slide 1: Title Slide
- **Visuals**: Clean, spacious layout with the NTU authors list and affiliations.
- **Talking Points**:
  - Welcome everyone. Today, I am presenting our project on the data-driven design of a logic-gated synthetic biology biosensor.
  - Our goal is to leverage unbiased public transcriptomic datasets to program a genetic circuit that can safely distinguish pancreatic tumors from normal tissues.
  - This work has been co-authored by Shih, Chen-Jung and Su, Te-Fang from NTU Life Science, and Liao, Xuan-You and Lin, Chia-I from NTU Biochemical Science and Technology.

---

## Slide 2: The PDAC Tumor Microenvironment
- **Visuals**: Layered schematic of stroma, immune stroma, and tumor cells.
- **Talking Points**:
  - Pancreatic Ductal Adenocarcinoma (PDAC) has one of the poorest prognoses of any solid tumor, with a 5-year survival rate of less than 12%.
  - This lethality is heavily driven by its unique tumor microenvironment: a dense fibrotic stroma populated by cancer-associated fibroblasts (CAFs) and extracellular matrix components.
  - This stroma creates both a physical barrier to drugs and an immunological shield.
  - Traditional targeted therapies fail because we lack high-specificity cell-surface markers that are uniquely present on cancer cells, presenting a major safety concern.

---

## Slide 3: Why a Single Marker is Insufficient
- **Visuals**: A single-input CAR-T cell binding to low-expressing healthy cells.
- **Talking Points**:
  - Let's look at why single-antigen therapies fall short. Highly overexpressed tumor antigens like Mesothelin or CEA are also expressed at lower levels on healthy tissues (like the lung lining or the GI tract).
  - A standard single-input therapeutic (like a basic CAR-T cell) activates as soon as it binds its target, regardless of the expression level.
  - This results in "on-target, off-tumor" toxicity, where the therapeutic attacks healthy organs.
  - To solve this, we must build a logic gate that requires more than one input to activate.

---

## Slide 4: The AND-Gate Biosensor Paradigm (Scene 1)
- **Visuals**: Dynamic 1D overlap plots of Gene A & B shifting into a 2D scatter plot, drawing threshold borders and highlighting the ON region.
- **Talking Points**:
  - This is where the synthetic biology AND-gate logic circuit comes in.
  - *[Explain the animation]*: If we look at Gene A alone, we see a massive overlap in expression between normal and tumor samples. The same is true for Gene B. Single-marker classification is highly ambiguous.
  - *[Watch the animation transition]*: However, by plotting these two markers together in two dimensions, we can isolate a specific "Double-High" quadrant.
  - An AND-gate biosensor will only activate (turn "ON") when *both* markers exceed their thresholds. Since healthy tissues only express at most one of the markers, they remain in the "OFF" regions, preventing off-tumor toxicity.

---

## Slide 5: Data Sources: TCGA-PAAD + GTEx
- **Visuals**: Table of discovery and validation cohorts.
- **Talking Points**:
  - To discover suitable gene pairs, we constructed an unbiased discovery cohort of 345 samples.
  - We integrated 178 primary tumors from TCGA-PAAD and 167 normal pancreas tissues from GTEx.
  - Crucially, these datasets were harmonized via the TOIL pipeline to eliminate batch effects and align their dynamic ranges.
  - We also reserved GSE62452, an independent microarray dataset of 130 samples, to test the transferability of our design to a different platform.

---

## Slide 6: Unbiased Selection Pipeline (Scene 2)
- **Visuals**: A step-by-step sequential flowchart revealing each stage of the pipeline.
- **Talking Points**:
  - *[Explain the animation]*: Our computational workflow operates in 9 stages.
  - First, we fetch and preprocess the combined TOIL matrix.
  - We perform a first-pass screen using Welch's t-test to identify significantly upregulated tumor-high genes.
  - Next, we train machine learning classifiers—not for clinical diagnosis, but to prioritize predictive features.
  - We apply SHAP to understand model attribution and extract local activation thresholds.
  - Candidate pairs are then scored based on activation rates and orthogonality.
  - We simulate logic gate kinetics using the Hill equation, perform robustness testing via parameter sweeps, and finally run external validation.

---

## Slide 7: First-Pass Screening (Differential Expression)
- **Visuals**: Volcano plot showing significantly upregulated genes with UBE2S and CCR6 highlighted.
- **Talking Points**:
  - The Welch's t-test screen identified 19,399 candidate genes that were significantly upregulated in tumors (log2FC &ge; 1.0, FDR &lt; 0.05).
  - To narrow this list down, we calculated a specificity score (the product of single-gene AUC and log2FC).
  - The volcano plot displays our candidates. Among the highly significant upregulated candidates, UBE2S and CCR6 stand out as prime inputs for our circuit.

---

## Slide 8: ML Prioritization & SHAP Attribution (Scene 3)
- **Visuals**: Horizontal bars growing left/right representing positive and negative SHAP attribution values.
- **Talking Points**:
  - To find a sparse signature, we trained three classifiers. An L1-regularized Logistic Regression model achieved a perfect CV AUC of 1.000, isolating the most predictive features.
  - *[Explain the animation]*: We applied SHAP (Shapley Additive exPlanations) to capture how the model makes decisions.
  - Look at the push and pull forces: features in blue pull the prediction toward a "PDAC Tumor" label, while features in gray pull it toward "Normal".
  - *[Emphasize the box highlight]*: Remember, SHAP values explain *the model's* mathematical logic. They do not represent direct biological causality, but rather feature importance.

---

## Slide 9: Selected Input Candidate: UBE2S + CCR6 (Scene 4)
- **Visuals**: Scatter plot showing normal and tumor clusters, threshold lines, and the highlighted Double-High quadrant.
- **Talking Points**:
  - *[Explain the animation]*: By scanning all combinations, our pipeline selected the UBE2S and CCR6 pair as the optimal input candidate.
  - Normal samples cluster in the double-low quadrant, while tumor samples cluster in the top-right double-high quadrant.
  - UBE2S is a cell-cycle regulator associated with mitotic progression, whereas CCR6 is a chemokine receptor expressed on tumor-infiltrating cells.
  - *[Highlight the warning]*: Note that their Pearson correlation is 0.714. While they operate on independent biological pathways (mitotic vs. chemokine), they are statistically correlated in bulk stroma, which is a key design consideration.

---

## Slide 10: Mathematical Hill-Equation Modeling (Scene 5)
- **Visuals**: Progressive reveal of the Hill equation terms, followed by an activating contour heatmap.
- **Talking Points**:
  - *[Explain the animation]*: To model the continuous kinetics of our logic gate, we implemented a dual-input Hill equation.
  - The output is the product of two independent Hill activation terms, with a Hill coefficient $n=1$ and basal leakiness set to 0.
  - *[Watch the heatmap sweep]*: The contour heatmap illustrates the activation profile. Notice the sharp, non-linear activation boundary in the top-right.
  - *[Emphasize the underline]*: A crucial caveat: the activation thresholds K_A and K_B are model-inferred transcriptomic thresholds (0.760 and 0.464), not physical biochemical dissociation constants.

---

## Slide 11: Validation and Transferability (Scene 6)
- **Visuals**: Side-by-side bar plots showing high discovery metrics and the validation sensitivity collapse, followed by a takeaway warning card.
- **Talking Points**:
  - *[Explain the animation]*: When we test our optimized AND gate on the discovery cohort, the performance is stellar: 0.9986 AUC, 98.6% Accuracy, and high sensitivity.
  - *[Watch the validation bars]*: But when we validate on the external GSE62452 microarray dataset, specificity remains high at 98.4%, but sensitivity collapses to just 4.3%.
  - This drop represents a transferability barrier: microarrays have a much lower dynamic range and higher background noise than RNA-seq, causing tumor samples to fall below the strict RNA-seq thresholds.
  - *[Highlight the box]*: The key takeaway is that a computationally prioritized candidate is *not* a pre-validated biosensor. Threshold calibration is mandatory for wet-lab translation.

---

## Slide 12: Summary & Wet-Lab Translation
- **Visuals**: Summary cards of the project outcomes.
- **Talking Points**:
  - In conclusion, we have built an unbiased transcriptomic pipeline that identifies and mathematically models logic-gated synthetic biosensors.
  - Moving forward, wet-lab validation must address threshold alignment.
  - We propose three engineering strategies: utilizing synthetic promoters in split-transactivator configurations, implementing RNA-based toehold switches for direct intracellular sensing, and conducting validation in PANC-1 tumor cells vs. HPDE healthy cells.
  - Thank you, and I am happy to take any questions.
