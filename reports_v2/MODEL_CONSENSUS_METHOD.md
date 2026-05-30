# Model-Consensus Feature Prioritization Methodology

To ensure biomarker selection does not overfit to a single model architecture (e.g. L1 Logistic Regression), we implemented a model-consensus pipeline.

## Integrated Models

1. **L1-Regularized Logistic Regression**: Captures linear log-odds predictors while enforcing sparsity.
2. **Random Forest Classifier**: Captures non-linear interactions via bagging decision trees. Feature importance is computed via Gini impurity decrease.
3. **XGBoost Classifier**: Gradient boosted decision trees using gain-based feature importances.

## Consensus Score Formula

$$\text{Model Consensus Score} = \frac{\text{RankScore}_{L1} + \text{RankScore}_{RF} + \text{RankScore}_{XGB}}{3}$$

$$\text{Consensus Score} = \frac{\text{Model Consensus Score} + \text{Stability Score}}{2}$$

This formula prioritizes genes that perform well across all classifiers and demonstrate high cross-dataset stability (TCGA+GTEx and GSE62452).
