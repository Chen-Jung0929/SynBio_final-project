# V3 Methods: Unbiased Three-Model Ensemble Pipeline for PDAC Logic-Gated Biosensor Input Discovery

This document details the mathematical, statistical, and machine learning methods implemented in the third-generation (v3) biosensor candidate gene pair discovery pipeline.

## 1. Machine Learning Model Ensemble & Feature Selection

Transcriptomic data contain highly correlated genes due to shared molecular pathways, cell cycle stages, stromal contamination, and tumor purity boundaries. Pure L1 (Lasso) regularization can be unstable in this setting because it arbitrarily selects one feature from a correlated group while suppressing others. 

To resolve this, the v3 pipeline uses **Elastic Net Logistic Regression** as its sparse linear model. Elastic Net combines $L1$ and $L2$ penalties to preserve sparsity and feature selection capability while stabilizing coefficient estimates among correlated predictors:

$$\mathcal{L} = \mathcal{L}_{\text{cross-entropy}} + C \left( \alpha \sum |w_i| + \frac{1-\alpha}{2} \sum w_i^2 \right)$$

where:
* $C$ is the inverse regularization strength ($C = 0.5$).
* $\alpha$ is the `l1_ratio` parameter ($l1\_ratio \in [0.2, 0.5, 0.8]$).

### Model Ingestion & Scaling
Elastic Net coefficient sizes are scale-dependent. Therefore, gene expression features are standardized using `StandardScaler` (mean = 0, standard deviation = 1) before model fitting. The tree-based models (Random Forest, XGBoost) are trained on the raw (unscaled) expression values since they are scale-invariant.

### Consensus Ranking
The consensus feature importance ranking integrates rankings from three model families trained on the cross-dataset stable gene subset (Stage 2 output):
1. **Elastic Net Logistic Regression** (SAGA solver, standardized features, CV-optimized `l1_ratio`).
2. **Random Forest Classifier** (unscaled features, Gini feature importance).
3. **XGBoost Classifier** (unscaled features, Gain feature importance).

The final rankings are computed as follows:
* Rank score for model $m$ and gene $g$ is $\text{RankScore}_{m}(g) = \frac{M - \text{rank}_m(g)}{M}$, where $M$ is the total number of stable genes.
* The model consensus score is:
  $$\text{Model Consensus Score}(g) = \frac{\text{RankScore}_{\text{EN}} + \text{RankScore}_{\text{RF}} + \text{RankScore}_{\text{XGB}}}{3}$$
* The final consensus score combines this with cross-dataset stability:
  $$\text{Consensus Score}(g) = \frac{\text{Model Consensus Score}(g) + \text{Stability Score}(g)}{2}$$

---

## 2. Three-Model Ensemble Threshold Estimation

For each gene in the consensus pool, we estimate model-specific activation thresholds on the discovery dataset:
1. **Elastic Net ($K_{\text{EN}}$)**: The threshold is derived from the linear SHAP coefficient contribution ($w_g \cdot X_g^{\text{scaled}}$). The threshold represents the expression value where the contribution crosses $0$ (which is the mean of the gene expression since the features are standardized).
2. **Random Forest ($K_{\text{RF}}$)**: TreeSHAP values are computed. We fit a 3rd degree polynomial to the SHAP values vs. expression values and identify the root where SHAP crosses from negative to positive.
3. **XGBoost ($K_{\text{XGB}}$)**: TreeSHAP values are computed, and the inflection point is estimated using a 3rd degree polynomial.
4. **Fallback (Youden Index)**: If no zero-crossing root is found within the expression range (e.g. if the Elastic Net coefficient is $0$), the threshold defaults to the expression value that maximizes Youden's Index ($J = \text{sensitivity} + \text{specificity} - 1$) in separating tumor and normal within the discovery cohort.

### Ensemble Threshold & Instability
* The final threshold is the ensemble average:
  $$K_{\text{final}} = K_{\text{mean}} = \frac{K_{\text{EN}} + K_{\text{RF}} + K_{\text{XGB}}}{3}$$
* The standard deviation of the three thresholds represents the threshold instability:
  $$\text{Threshold Instability Score} = K_{\text{std}}$$

---

## 3. Search-Space Sweeps & Pair Scoring

To assess pipeline robustness, we perform the pair search independently across four consensus-cutoff spaces: top 20, 50, 100, and 200 consensus genes. For every pairwise combination of genes (Gene A and Gene B), we scale expressions to $[0, 1]$ and compute the composite Pair Score:

$$\text{Pair Score} = \text{Performance Score} - \text{Redundancy Penalty} - \text{Threshold Instability Penalty}$$

where:
* $\text{Performance Score} = \frac{\text{sens}_{\text{disc}} + \text{spec}_{\text{disc}} + \text{sens}_{\text{val}} + \text{spec}_{\text{val}}}{4}$ (GSE62452 is used for same-cohort validation).
* $\text{Redundancy Penalty} = \alpha \cdot |r_{\text{Spearman}}|$, with $\alpha = 0.2$.
* $\text{Threshold Instability Penalty} = \beta \cdot \frac{K_{\text{std}}(A) + K_{\text{std}}(B)}{2}$, with $\beta = 0.1$.

The final selected biosensor pair is the top-ranked pair in the default **top 100** search space.

---

## 4. Single-Cell Validation Disclaimer

Due to lack of standard unsupervised cell clustering dependencies (such as `leidenalg`) in the target execution environment, the single-cell RNA-seq validation (GSE154778) is implemented as a **preliminary marker-score-based targeted validation, not a full unbiased scRNA-seq annotation workflow**. Cell types are scored based on canonical lineage markers after candidate gene overlap removal, but without de novo Leiden clustering or UMAP projections.
