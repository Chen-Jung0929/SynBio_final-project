# Methods Summary — PDAC AND-Gate Biosensor Pipeline

## Data Acquisition

- **Discovery cohort:** TCGA-PAAD (n=178 tumors) + GTEx (n=167 normal pancreas), harmonized via UCSC Xena TOIL pipeline (RSEM TPM)
- **External validation:** GSE62452 (GPL6244 microarray, n=130: 69 tumor + 61 adjacent normal)

## Preprocessing

- Expression values: log2(TPM + 0.001)
- Low-variance gene filter: removed genes with near-zero variance (retained 58,581 / 60,498)
- Quality control: verified sample counts, group balance, and expression distributions

## Differential Expression

- Welch's t-test (unequal variance) for each gene
- Multiple testing correction: Benjamini-Hochberg FDR
- Effect size: log2 fold change (PDAC mean − Normal mean)
- Per-gene ROC-AUC for discriminatory power assessment
- Selection criteria: log2FC ≥ 1.0 AND FDR < 0.05 → 19,399 tumor-high candidates

## Machine Learning Classification

- **Models tested:** L1-regularized Logistic Regression, Random Forest (100 trees), XGBoost
- **Split:** Stratified 80/20 train/test
- **Validation:** 5-fold stratified cross-validation
- **Feature space:** All 58,581 genes
- **Selected model:** Logistic Regression L1 (sparsest solution, AUC = 1.000)

## SHAP Explainable AI

- TreeExplainer (for XGBoost/RF) and LinearExplainer (for LogReg)
- Extracted top 100 genes by mean absolute SHAP value
- Threshold inference: identified expression level where SHAP contribution transitions from negative (Normal-associated) to positive (PDAC-associated) via SHAP dependence analysis
- 95% confidence intervals via 200-iteration bootstrap

## Orthogonality & Pair Selection

- Scored all pairwise combinations of top SHAP features
- **Pair Score** = tumor_AND_activation × AND_specificity × (1 − |Pearson correlation|)
- tumor_AND_activation: fraction of PDAC samples with both genes above SHAP threshold
- AND_specificity: fraction of Normal samples with ≥1 gene below threshold
- Selected pair with highest composite score: **UBE2S + CCR6**

## AND Gate Mathematical Model

- Hill equation: Output = P_basal + P_max × H(A, K_A, n) × H(B, K_B, n)
- where H(x, K, n) = x^n / (K^n + x^n)
- Expression values rescaled to [0, 1] via min-max normalization
- Parameter sweep: n ∈ {1, 2, 3, 4}, K_A/K_B ∈ linspace(0.1, 0.9, 50), P_basal ∈ {0.0, 0.01, 0.05}
- Optimal: n=1, P_basal=0.0, K_A=0.760, K_B=0.464, decision threshold=0.25

## Validation Controls

1. **Random pair control:** 1,000 random gene pairs with same AND-gate model; empirical p-value < 0.0001
2. **Threshold sensitivity:** K parameter perturbation ±10/25/50%; AUC remains > 0.994
3. **External validation:** Applied model to GSE62452 with platform-adapted min-max normalization; AUC=0.648, Specificity=98.4%

## Software

- Python 3.9, pandas, numpy, scipy, scikit-learn, xgboost, shap, matplotlib, seaborn, statsmodels
- Compute: NCHC t3-c4.nchc.org.tw biomedical node
- Automation: Antigravity NCHC Bridge (paramiko + Flask)
