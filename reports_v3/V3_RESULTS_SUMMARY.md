# V3 Results Summary: Unbiased Validation Pipeline

This document summarizes the quantitative results of the third-generation (v3) discovery and validation pipeline.

## 1. Data Source Usage and Ingestion Audit
The pipeline uses three distinct patient cohorts. GSE28735 is kept strictly locked and is only evaluated once on the final selected pair:

| dataset                         | role                          | locked_final_validation_only   |
|:--------------------------------|:------------------------------|:-------------------------------|
| TCGA + GTEx Discovery           | used_for_discovery            | no                             |
| GSE62452 Same-Cohort Validation | used_for_validation_filtering | no                             |
| GSE28735 External Validation    | locked_final_validation_only  | yes                            |

---

## 2. Elastic Net Hyperparameter Logging
Grid search results for the Elastic Net Logistic Regression (SAGA) solver:

| penalty    | solver   |   C |   l1_ratio |   max_iter |   random_state | features_standardized   |   solver_iterations | convergence_achieved   |   ROC_AUC_discovery |   ROC_AUC_GSE62452_validation |   avg_internal_ROC_AUC | best_selected_yes_no   |
|:-----------|:---------|----:|-----------:|-----------:|---------------:|:------------------------|--------------------:|:-----------------------|--------------------:|------------------------------:|-----------------------:|:-----------------------|
| elasticnet | saga     | 0.5 |        0.2 |      10000 |             42 | yes                     |                3614 | yes                    |                   1 |                      0.87693  |               0.938465 | no                     |
| elasticnet | saga     | 0.5 |        0.5 |      10000 |             42 | yes                     |                4810 | yes                    |                   1 |                      0.888572 |               0.944286 | no                     |
| elasticnet | saga     | 0.5 |        0.8 |      10000 |             42 | yes                     |                5356 | yes                    |                   1 |                      0.889998 |               0.944999 | yes                    |

---

## 3. Model-Consensus Feature Prioritization (Top 15 Stable Genes)
Consensus ranking of features across Elastic Net, Random Forest, and XGBoost:

| gene    |   importance_elastic_net |   rank_elastic_net |   rank_score_elastic_net |   importance_rf |   rank_rf |   rank_score_rf |   importance_xgb |   rank_xgb |   rank_score_xgb |   model_consensus_score |   log2fc |      auc |   log2fc_val |   auc_val |   stability_score |   consensus_score |
|:--------|-------------------------:|-------------------:|-------------------------:|----------------:|----------:|----------------:|-----------------:|-----------:|-----------------:|------------------------:|---------:|---------:|-------------:|----------:|------------------:|------------------:|
| MISP    |                0.338971  |                  3 |                 0.996622 |     0.0295916   |         5 |        0.994369 |       0.453004   |          1 |         0.998874 |                0.996622 |  7.76709 | 0.996367 |     0.665979 |  0.824661 |          0.910514 |          0.953568 |
| OCIAD2  |                0.132766  |                 15 |                 0.983108 |     0.0198843   |        12 |        0.986486 |       0.31475    |          2 |         0.997748 |                0.989114 |  3.96697 | 0.996939 |     1.00108  |  0.818484 |          0.907711 |          0.948413 |
| MMP12   |                0.41243   |                  1 |                 0.998874 |     0.0185417   |        19 |        0.978604 |       0.040243   |          3 |         0.996622 |                0.991366 | 11.2827  | 0.997998 |     1.40722  |  0.811119 |          0.904559 |          0.947963 |
| CCNB1   |                0.0667605 |                 43 |                 0.951577 |     0.0206032   |        11 |        0.987613 |       0.00539526 |         15 |         0.983108 |                0.974099 |  3.7283  | 0.994517 |     0.917855 |  0.831551 |          0.913034 |          0.943567 |
| AGR2    |                0.110383  |                 23 |                 0.974099 |     0.000911276 |        68 |        0.923423 |       0.0199512  |          4 |         0.995495 |                0.964339 |  6.32653 | 0.976317 |     1.85931  |  0.851984 |          0.91415  |          0.939245 |
| PLAC8   |                0.0314338 |                 58 |                 0.934685 |     0.00965759  |        33 |        0.962838 |       0.00391863 |         17 |         0.980856 |                0.959459 |  6.73267 | 0.993121 |     1.76479  |  0.83464  |          0.91388  |          0.93667  |
| LAMA3   |                0.0165497 |                 73 |                 0.917793 |     0.000524062 |        81 |        0.908784 |       0.00128214 |         35 |         0.960586 |                0.929054 |  5.36495 | 0.988344 |     1.24186  |  0.899026 |          0.943685 |          0.936369 |
| CEACAM5 |                0.127759  |                 18 |                 0.97973  |     0.000374057 |        99 |        0.888514 |       0.00950105 |          9 |         0.989865 |                0.952703 | 10.4629  | 0.966477 |     2.79467  |  0.864813 |          0.915645 |          0.934174 |
| MMP9    |                0.260613  |                  6 |                 0.993243 |     0.0096415   |        40 |        0.954955 |       0.0151492  |          7 |         0.992117 |                0.980105 |  7.75573 | 0.997326 |     0.788611 |  0.769779 |          0.883551 |          0.931828 |
| CST1    |                0.37486   |                  2 |                 0.997748 |     0.000254941 |       124 |        0.86036  |       0.00125927 |         37 |         0.958333 |                0.938814 | 13.9684  | 0.990227 |     1.65111  |  0.816821 |          0.903524 |          0.921169 |
| GRN     |                0.0826775 |                 34 |                 0.961712 |     0.000664451 |        75 |        0.915541 |       0.0175891  |          5 |         0.994369 |                0.957207 |  3.53224 | 0.996737 |     0.507347 |  0.757425 |          0.877076 |          0.917141 |
| RCN1    |                0.0093036 |                 77 |                 0.913288 |     0.0100039   |        24 |        0.972973 |       0.00722656 |         12 |         0.986486 |                0.957583 |  3.24744 | 0.992935 |     0.579979 |  0.746258 |          0.869585 |          0.913584 |
| CTTN    |                0.228073  |                  9 |                 0.989865 |     0.000342409 |       106 |        0.880631 |       0.00176019 |         26 |         0.970721 |                0.947072 |  1.24103 | 0.911323 |     0.726272 |  0.841292 |          0.876308 |          0.91169  |
| SDC1    |                0         |                151 |                 0.829955 |     0.00932788  |        52 |        0.941441 |       0          |         61 |         0.931306 |                0.900901 |  4.57093 | 0.980236 |     0.77469  |  0.8622   |          0.921218 |          0.91106  |
| TPX2    |                0.0637173 |                 46 |                 0.948198 |     0.000116834 |       178 |        0.79955  |       0.00116956 |         38 |         0.957207 |                0.901652 |  6.65469 | 0.995408 |     0.974667 |  0.837135 |          0.916271 |          0.908962 |

---

## 4. Threshold Instability Audit (Top 15 Genes)
Ensemble threshold standard deviations and IQRs:

| gene    |   threshold_std_instability |   threshold_iqr |
|:--------|----------------------------:|----------------:|
| MISP    |                  0.29399    |       0.314897  |
| OCIAD2  |                  0.00957361 |       0.0107226 |
| MMP12   |                  0.0220799  |       0.0263315 |
| CCNB1   |                  0.0417662  |       0.0449482 |
| AGR2    |                  0.290046   |       0.308479  |
| PLAC8   |                  0.0234246  |       0.0281972 |
| LAMA3   |                  0.402313   |       0.479476  |
| CEACAM5 |                  0.0984765  |       0.117714  |
| MMP9    |                  0.0779806  |       0.0862013 |
| CST1    |                  0.261384   |       0.303715  |
| GRN     |                  0.0227027  |       0.0274924 |
| RCN1    |                  0.0414751  |       0.0456526 |
| CTTN    |                  0.13151    |       0.140322  |
| SDC1    |                  0.0845303  |       0.0941014 |
| TPX2    |                  0.172212   |       0.185632  |

---

## 5. Top-N Search-Space Stability Sweeps
The optimal pair selection metrics across different search spaces (top 20, 50, 100, 200 consensus genes):

|   search_space_top_N |   evaluated_genes |   evaluated_pairs | top_ranked_pair   |   pair_score |   discovery_sensitivity |   discovery_specificity |   GSE62452_validation_sensitivity |   GSE62452_validation_specificity |   tumor_spearman_r |   mean_threshold_instability | redundancy_category                  |
|---------------------:|------------------:|------------------:|:------------------|-------------:|------------------------:|------------------------:|----------------------------------:|----------------------------------:|-------------------:|-----------------------------:|:-------------------------------------|
|                   20 |                20 |               190 | OCIAD2 + EDIL3    |     0.853823 |                0.983146 |                1        |                          0.811594 |                          0.639344 |          0.0120733 |                    0.0228376 | weak correlation / high independence |
|                   50 |                50 |              1225 | OCIAD2 + EDIL3    |     0.853823 |                0.983146 |                1        |                          0.811594 |                          0.639344 |          0.0120733 |                    0.0228376 | weak correlation / high independence |
|                  100 |               100 |              4950 | PKM + ADAM22      |     0.878421 |                0.966292 |                0.994012 |                          0.710145 |                          0.901639 |          0.0634429 |                    0.0191214 | weak correlation / high independence |
|                  200 |               200 |             19900 | PKM + ADAM22      |     0.878421 |                0.966292 |                0.994012 |                          0.710145 |                          0.901639 |          0.0634429 |                    0.0191214 | weak correlation / high independence |

---

## 6. Overlap of Top 20 Pairs Across Cutoffs
Jaccard similarity and shared top-ranked pairs between search spaces:

| space_1   | space_2   |   top20_pairs_shared |   jaccard_similarity |
|:----------|:----------|---------------------:|---------------------:|
| top_20    | top_20    |                   20 |            1         |
| top_20    | top_50    |                    3 |            0.0810811 |
| top_20    | top_100   |                    1 |            0.025641  |
| top_20    | top_200   |                    0 |            0         |
| top_50    | top_50    |                   20 |            1         |
| top_50    | top_100   |                    4 |            0.111111  |
| top_50    | top_200   |                    0 |            0         |
| top_100   | top_100   |                   20 |            1         |
| top_100   | top_200   |                    3 |            0.0810811 |
| top_200   | top_200   |                   20 |            1         |

---

## 7. Locked Final External Validation (GSE28735)
Performance of the final default selected v3 candidate pair (PKM + ADAM22) on the locked external validation cohort:

| gene_A   | gene_B   |   K_final_A |   K_final_B |   GSE28735_sensitivity |   GSE28735_specificity |   GSE28735_ROC_AUC |   GSE28735_Spearman_r |
|:---------|:---------|------------:|------------:|-----------------------:|-----------------------:|-------------------:|----------------------:|
| PKM      | ADAM22   |    0.804721 |    0.623865 |               0.488889 |                    nan |                nan |               0.60833 |

---

## 8. scRNA-seq Validation (GSE154778)
Expression and co-expression rates of the final v3 selected pair across independently annotated cell types:

| rank               | gene_A   | gene_B   | cell_type                                                          |   n_cells |   mean_expression_A |   mean_expression_B |   coexpression_fraction_gt_0 |   coexpression_fraction_gt_0_5 |
|:-------------------|:---------|:---------|:-------------------------------------------------------------------|----------:|--------------------:|--------------------:|-----------------------------:|-------------------------------:|
| final_pair         | PKM      | ADAM22   | B cells                                                            |       191 |          1.38965    |          0          |                  0           |                    0           |
| final_pair         | PKM      | ADAM22   | CAF / fibroblast                                                   |      1942 |          1.65332    |          0.140254   |                  0.0777549   |                    0.0777549   |
| final_pair         | PKM      | ADAM22   | CD8 T cells                                                        |        79 |          1.51958    |          0.0160875  |                  0.0126582   |                    0.0126582   |
| final_pair         | PKM      | ADAM22   | NK cells                                                           |         9 |          1.46984    |          0          |                  0           |                    0           |
| final_pair         | PKM      | ADAM22   | T cells                                                            |       180 |          1.37528    |          0.0162095  |                  0.00555556  |                    0.00555556  |
| final_pair         | PKM      | ADAM22   | Tregs                                                              |        20 |          2.21032    |          0          |                  0           |                    0           |
| final_pair         | PKM      | ADAM22   | acinar-like cells                                                  |      2256 |          1.2178     |          0.00212868 |                  0.000886525 |                    0.000886525 |
| final_pair         | PKM      | ADAM22   | dendritic cells                                                    |        24 |          1.82973    |          0          |                  0           |                    0           |
| final_pair         | PKM      | ADAM22   | endocrine cells                                                    |         8 |          1.42412    |          0.345485   |                  0.25        |                    0.25        |
| final_pair         | PKM      | ADAM22   | endothelial                                                        |       113 |          1.30733    |          0.0389493  |                  0.00884956  |                    0.00884956  |
| final_pair         | PKM      | ADAM22   | macrophages / monocytes                                            |      1557 |          1.76239    |          0.00558095 |                  0.00385356  |                    0.00385356  |
| final_pair         | PKM      | ADAM22   | mast cells                                                         |        24 |          2.20904    |          0          |                  0           |                    0           |
| final_pair         | PKM      | ADAM22   | pericytes / VSMC                                                   |       120 |          1.42482    |          0.0419182  |                  0.025       |                    0.025       |
| final_pair         | PKM      | ADAM22   | plasma cells                                                       |       752 |          1.14818    |          0.0146317  |                  0.00664894  |                    0.00664894  |
| final_pair         | PKM      | ADAM22   | tumor-associated epithelial / putative malignant ductal epithelial |      7649 |          1.65787    |          0.00460184 |                  0.00261472  |                    0.00261472  |
| alternative_pair_1 | MMP9     | NQO1     | B cells                                                            |       191 |          0.0420728  |          0.283341   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | CAF / fibroblast                                                   |      1942 |          0.0418394  |          0.271841   |                  0.0046344   |                    0.0046344   |
| alternative_pair_1 | MMP9     | NQO1     | CD8 T cells                                                        |        79 |          0.0212958  |          0.25885    |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | NK cells                                                           |         9 |          0          |          0          |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | T cells                                                            |       180 |          0.0534013  |          0.107945   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | Tregs                                                              |        20 |          0          |          0.186308   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | acinar-like cells                                                  |      2256 |          0.00546388 |          1.11519    |                  0.00221631  |                    0.00221631  |
| alternative_pair_1 | MMP9     | NQO1     | dendritic cells                                                    |        24 |          0.17671    |          0.194729   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | endocrine cells                                                    |         8 |          0          |          0.383789   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | endothelial                                                        |       113 |          0.0976228  |          0.542735   |                  0.0176991   |                    0.0176991   |
| alternative_pair_1 | MMP9     | NQO1     | macrophages / monocytes                                            |      1557 |          0.367707   |          0.142526   |                  0.0250482   |                    0.0250482   |
| alternative_pair_1 | MMP9     | NQO1     | mast cells                                                         |        24 |          0          |          0.300881   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | pericytes / VSMC                                                   |       120 |          0.0449496  |          0.309659   |                  0           |                    0           |
| alternative_pair_1 | MMP9     | NQO1     | plasma cells                                                       |       752 |          0.0367594  |          0.858163   |                  0.0159574   |                    0.0159574   |
| alternative_pair_1 | MMP9     | NQO1     | tumor-associated epithelial / putative malignant ductal epithelial |      7649 |          0.0183628  |          1.1299     |                  0.00954373  |                    0.00954373  |
| alternative_pair_2 | LOXL1    | NQO1     | B cells                                                            |       191 |          0.110438   |          0.283341   |                  0.0471204   |                    0.0471204   |
| alternative_pair_2 | LOXL1    | NQO1     | CAF / fibroblast                                                   |      1942 |          0.845901   |          0.271841   |                  0.0911432   |                    0.0911432   |
| alternative_pair_2 | LOXL1    | NQO1     | CD8 T cells                                                        |        79 |          0.0162912  |          0.25885    |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | NK cells                                                           |         9 |          0.108704   |          0          |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | T cells                                                            |       180 |          0.0445781  |          0.107945   |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | Tregs                                                              |        20 |          0.0736002  |          0.186308   |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | acinar-like cells                                                  |      2256 |          0.101817   |          1.11519    |                  0.0505319   |                    0.0505319   |
| alternative_pair_2 | LOXL1    | NQO1     | dendritic cells                                                    |        24 |          0.0403119  |          0.194729   |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | endocrine cells                                                    |         8 |          0          |          0.383789   |                  0           |                    0           |
| alternative_pair_2 | LOXL1    | NQO1     | endothelial                                                        |       113 |          0.0327778  |          0.542735   |                  0.00884956  |                    0.00884956  |
| alternative_pair_2 | LOXL1    | NQO1     | macrophages / monocytes                                            |      1557 |          0.0250532  |          0.142526   |                  0.00513809  |                    0.00513809  |
| alternative_pair_2 | LOXL1    | NQO1     | mast cells                                                         |        24 |          0.11243    |          0.300881   |                  0.0833333   |                    0.0833333   |
| alternative_pair_2 | LOXL1    | NQO1     | pericytes / VSMC                                                   |       120 |          0.348487   |          0.309659   |                  0.0916667   |                    0.0916667   |
| alternative_pair_2 | LOXL1    | NQO1     | plasma cells                                                       |       752 |          0.343898   |          0.858163   |                  0.199468    |                    0.199468    |
| alternative_pair_2 | LOXL1    | NQO1     | tumor-associated epithelial / putative malignant ductal epithelial |      7649 |          0.083286   |          1.1299     |                  0.0444503   |                    0.0444503   |
| alternative_pair_3 | PXDN     | NQO1     | B cells                                                            |       191 |          0.00887413 |          0.283341   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | CAF / fibroblast                                                   |      1942 |          0.350126   |          0.271841   |                  0.0314109   |                    0.0314109   |
| alternative_pair_3 | PXDN     | NQO1     | CD8 T cells                                                        |        79 |          0.0314754  |          0.25885    |                  0.0126582   |                    0.0126582   |
| alternative_pair_3 | PXDN     | NQO1     | NK cells                                                           |         9 |          0          |          0          |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | T cells                                                            |       180 |          0          |          0.107945   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | Tregs                                                              |        20 |          0          |          0.186308   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | acinar-like cells                                                  |      2256 |          0.301046   |          1.11519    |                  0.167996    |                    0.167996    |
| alternative_pair_3 | PXDN     | NQO1     | dendritic cells                                                    |        24 |          0          |          0.194729   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | endocrine cells                                                    |         8 |          0          |          0.383789   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | endothelial                                                        |       113 |          0.658227   |          0.542735   |                  0.176991    |                    0.176991    |
| alternative_pair_3 | PXDN     | NQO1     | macrophages / monocytes                                            |      1557 |          0.0144392  |          0.142526   |                  0.00192678  |                    0.00192678  |
| alternative_pair_3 | PXDN     | NQO1     | mast cells                                                         |        24 |          0.069569   |          0.300881   |                  0           |                    0           |
| alternative_pair_3 | PXDN     | NQO1     | pericytes / VSMC                                                   |       120 |          0.442436   |          0.309659   |                  0.075       |                    0.075       |
| alternative_pair_3 | PXDN     | NQO1     | plasma cells                                                       |       752 |          0.0659348  |          0.858163   |                  0.0305851   |                    0.0305851   |
| alternative_pair_3 | PXDN     | NQO1     | tumor-associated epithelial / putative malignant ductal epithelial |      7649 |          0.0163997  |          1.1299     |                  0.00732122  |                    0.00732122  |

---

## 9. Patient Prevalence and Co-expression Heterogeneity
Double-positive prevalence in ductal epithelial and CAF compartments across individual patients:

| patient_id   | cell_type                                                          |   n_cells |   mean_expression_A |   mean_expression_B |   coexpression_fraction_gt_0 |   coexpression_fraction_gt_0_5 |
|:-------------|:-------------------------------------------------------------------|----------:|--------------------:|--------------------:|-----------------------------:|-------------------------------:|
| MET01        | tumor-associated epithelial / putative malignant ductal epithelial |       366 |             1.62739 |          0          |                   0          |                     0          |
| MET02        | tumor-associated epithelial / putative malignant ductal epithelial |       701 |             2.18222 |          0.00159553 |                   0.00142653 |                     0.00142653 |
| MET03        | tumor-associated epithelial / putative malignant ductal epithelial |        36 |             1.39918 |          0          |                   0          |                     0          |
| MET03        | CAF / fibroblast                                                   |         1 |             1.31124 |          0          |                   0          |                     0          |
| MET04        | tumor-associated epithelial / putative malignant ductal epithelial |       113 |             1.14632 |          0          |                   0          |                     0          |
| MET05        | tumor-associated epithelial / putative malignant ductal epithelial |       512 |             1.61478 |          0          |                   0          |                     0          |
| MET06        | tumor-associated epithelial / putative malignant ductal epithelial |      2254 |             1.51391 |          0.00398186 |                   0.00266193 |                     0.00266193 |
| MET06        | CAF / fibroblast                                                   |         1 |             1.41423 |          0          |                   0          |                     0          |
| P01          | tumor-associated epithelial / putative malignant ductal epithelial |        75 |             2.06805 |          0.019794   |                   0.0133333  |                     0.0133333  |
| P01          | CAF / fibroblast                                                   |       157 |             1.82918 |          0.0105313  |                   0.00636943 |                     0.00636943 |
| P02          | tumor-associated epithelial / putative malignant ductal epithelial |        70 |             1.92293 |          0          |                   0          |                     0          |
| P02          | CAF / fibroblast                                                   |         1 |             1.69641 |          0          |                   0          |                     0          |
| P03          | tumor-associated epithelial / putative malignant ductal epithelial |       367 |             1.84842 |          0          |                   0          |                     0          |
| P03          | CAF / fibroblast                                                   |       148 |             1.43561 |          0.0198018  |                   0.0135135  |                     0.0135135  |
| P04          | tumor-associated epithelial / putative malignant ductal epithelial |       185 |             2.15877 |          0          |                   0          |                     0          |
| P04          | CAF / fibroblast                                                   |        72 |             2.01333 |          0.0245555  |                   0.0138889  |                     0.0138889  |
| P05          | tumor-associated epithelial / putative malignant ductal epithelial |       138 |             1.96569 |          0.0249954  |                   0.0144928  |                     0.0144928  |
| P05          | CAF / fibroblast                                                   |       610 |             1.85221 |          0.198107   |                   0.109836   |                     0.109836   |
| P06          | tumor-associated epithelial / putative malignant ductal epithelial |       321 |             1.55674 |          0          |                   0          |                     0          |
| P06          | CAF / fibroblast                                                   |       278 |             1.28784 |          0.17383    |                   0.0935252  |                     0.0935252  |
| P07          | tumor-associated epithelial / putative malignant ductal epithelial |       134 |             1.5424  |          0.0218535  |                   0.0149254  |                     0.0149254  |
| P07          | CAF / fibroblast                                                   |       151 |             1.33643 |          0.193231   |                   0.0927152  |                     0.0927152  |
| P08          | tumor-associated epithelial / putative malignant ductal epithelial |       774 |             1.55612 |          0.00895395 |                   0.00258398 |                     0.00258398 |
| P08          | CAF / fibroblast                                                   |       139 |             1.57349 |          0.150157   |                   0.0935252  |                     0.0935252  |
| P09          | tumor-associated epithelial / putative malignant ductal epithelial |       304 |             1.85039 |          0.0161818  |                   0.00986842 |                     0.00986842 |
| P09          | CAF / fibroblast                                                   |       255 |             1.68798 |          0.137918   |                   0.0901961  |                     0.0901961  |
| P10          | tumor-associated epithelial / putative malignant ductal epithelial |      1299 |             1.55859 |          0.00415246 |                   0.00230947 |                     0.00230947 |
| P10          | CAF / fibroblast                                                   |       129 |             1.72785 |          0.0901674  |                   0.0310078  |                     0.0310078  |
