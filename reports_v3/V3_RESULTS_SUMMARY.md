# V3 Results Summary: Unbiased Validation Pipeline

This document summarizes the quantitative results of the third-generation (v3) discovery and validation pipeline.

## 1. Data Source Usage and Ingestion Audit
The pipeline uses three distinct patient cohorts. GSE28735 is kept strictly locked and is only evaluated once on the final selected pair:

| dataset | role | locked_final_validation_only |
| --- | --- | --- |
| TCGA + GTEx Discovery | used_for_discovery | no |
| GSE62452 Same-Cohort Validation | used_for_validation_filtering | no |
| GSE28735 External Validation | locked_final_validation_only | yes |

---

## 2. Elastic Net Hyperparameter Logging
Grid search results for the Elastic Net Logistic Regression (SAGA) solver:

| penalty | solver | C | l1_ratio | max_iter | random_state | features_standardized | solver_iterations | convergence_achieved | ROC_AUC_discovery | ROC_AUC_GSE62452_validation | avg_internal_ROC_AUC | best_selected_yes_no |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elasticnet | saga | 0.5 | 0.2 | 10000 | 42 | yes | 3614 | yes | 1.0 | 0.8769303872653839 | 0.938465193632692 | no |
| elasticnet | saga | 0.5 | 0.5 | 10000 | 42 | yes | 4810 | yes | 1.0 | 0.8885721073889286 | 0.9442860536944644 | no |
| elasticnet | saga | 0.5 | 0.8 | 10000 | 42 | yes | 5356 | yes | 1.0 | 0.8899976241387503 | 0.9449988120693752 | yes |

---

## 3. Model-Consensus Feature Prioritization (Top 15 Stable Genes)
Consensus ranking of features across Elastic Net, Random Forest, and XGBoost:

| gene | importance_elastic_net | rank_elastic_net | rank_score_elastic_net | importance_rf | rank_rf | rank_score_rf | importance_xgb | rank_xgb | rank_score_xgb | model_consensus_score | log2fc | auc | log2fc_val | auc_val | stability_score | consensus_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MISP | 0.3389714215496242 | 3 | 0.9966216216216216 | 0.0295916220576349 | 5 | 0.9943693693693694 | 0.453004 | 1 | 0.9988738738738738 | 0.9966216216216216 | 7.767093157505214 | 0.996366816927942 | 0.6659791732002853 | 0.8246614397719174 | 0.9105141170485191 | 0.9535678693350704 |
| OCIAD2 | 0.1327659306222557 | 15 | 0.983108108108108 | 0.0198843327623274 | 12 | 0.9864864864864864 | 0.3147495 | 2 | 0.9977477477477478 | 0.989114114114114 | 3.9669676209379 | 0.996938706855951 | 1.0010752459016403 | 0.8184842005226894 | 0.907711433062664 | 0.9484127735883892 |
| MMP12 | 0.4124299058344953 | 1 | 0.9988738738738738 | 0.018541743326163 | 19 | 0.9786036036036035 | 0.04024303 | 3 | 0.9966216216216216 | 0.9913663663663664 | 11.282721984121643 | 0.997998385251968 | 1.4072152791636978 | 0.8111190306486101 | 0.9045586660587742 | 0.9479625162125702 |
| CCNB1 | 0.0667604781708052 | 43 | 0.9515765765765766 | 0.0206032078798938 | 11 | 0.9876126126126126 | 0.00539526 | 15 | 0.983108108108108 | 0.9740990990990992 | 3.72830410078719 | 0.9945165848079124 | 0.9178550748396308 | 0.831551437396056 | 0.9130340049834812 | 0.94356655204129 |
| AGR2 | 0.1103825364285567 | 23 | 0.9740990990990992 | 0.000911275607523 | 68 | 0.9234234234234234 | 0.019951181 | 4 | 0.9954954954954957 | 0.9643393393393392 | 6.326527390163492 | 0.976317028863621 | 1.859313894036588 | 0.851983844143502 | 0.9141504355990157 | 0.9392448874691774 |
| PLAC8 | 0.0314337961883701 | 58 | 0.9346846846846848 | 0.0096575908955569 | 33 | 0.9628378378378378 | 0.0039186347 | 17 | 0.980855855855856 | 0.9594594594594597 | 6.732672865504945 | 0.99312050057189 | 1.7647905725825588 | 0.83464005702067 | 0.9138802743135876 | 0.9366698668865236 |
| LAMA3 | 0.0165497190430404 | 73 | 0.9177927927927928 | 0.0005240616071335 | 81 | 0.9087837837837838 | 0.0012821412 | 35 | 0.9605855855855856 | 0.929054054054054 | 5.364946686402476 | 0.9883435376438136 | 1.241862988833451 | 0.8990258968876218 | 0.943684717248034 | 0.936369385651044 |
| CEACAM5 | 0.1277590691022387 | 18 | 0.9797297297297296 | 0.0003740572911135 | 99 | 0.8885135135135135 | 0.009501049 | 9 | 0.9898648648648648 | 0.9527027027027026 | 10.462945828567584 | 0.9664771580434636 | 2.794674587788072 | 0.8648134948918983 | 0.9156453262104316 | 0.9341740144565672 |
| MMP9 | 0.260613202742897 | 6 | 0.9932432432432432 | 0.0096415035385465 | 40 | 0.954954954954955 | 0.015149248 | 7 | 0.9921171171171173 | 0.9801051051051052 | 7.755727349794792 | 0.9973255735719572 | 0.7886111712995953 | 0.7697790449037777 | 0.8835505412278342 | 0.9318278231664696 |
| CST1 | 0.3748596649277899 | 2 | 0.9977477477477478 | 0.0002549408478824 | 124 | 0.8603603603603603 | 0.0012592678 | 37 | 0.9583333333333334 | 0.9388138138138138 | 13.968350481060352 | 0.9902274103478436 | 1.651110529817058 | 0.8168210976478973 | 0.9035242299939726 | 0.9211690219038932 |
| GRN | 0.0826775151197643 | 34 | 0.9617117117117115 | 0.0006644507993732 | 75 | 0.9155405405405406 | 0.017589133 | 5 | 0.9943693693693694 | 0.9572072072072072 | 3.5322372199421377 | 0.9967368633519478 | 0.507347327156098 | 0.7574245664053219 | 0.8770756861545227 | 0.917141446680865 |
| RCN1 | 0.0093035969777335 | 77 | 0.9132882882882885 | 0.0100038596524927 | 24 | 0.972972972972973 | 0.0072265593 | 12 | 0.9864864864864864 | 0.9575825825825826 | 3.24744221893292 | 0.992935477359887 | 0.5799790354003314 | 0.7462580185317178 | 0.8695845202056721 | 0.9135835513941272 |
| CTTN | 0.2280730768092249 | 9 | 0.9898648648648648 | 0.000342409104443 | 106 | 0.8806306306306306 | 0.0017601902 | 26 | 0.9707207207207208 | 0.947072072072072 | 1.2410260983650678 | 0.9113234205745812 | 0.7262719695889732 | 0.8412924685198384 | 0.8763079423285811 | 0.9116900072003268 |
| SDC1 | 0.0 | 151 | 0.829954954954955 | 0.0093278784336645 | 52 | 0.9414414414414416 | 0.0 | 61 | 0.9313063063063064 | 0.9009009009009008 | 4.570934521967301 | 0.9802361568996836 | 0.7746903254929913 | 0.862200047517225 | 0.9212181018685718 | 0.9110595013847363 |
| TPX2 | 0.0637173336702434 | 46 | 0.9481981981981982 | 0.0001168342984862 | 178 | 0.7995495495495496 | 0.0011695587 | 38 | 0.9572072072072072 | 0.9016516516516516 | 6.654686059341989 | 0.9954080602839264 | 0.9746665645046342 | 0.8371347113328582 | 0.9162713822267036 | 0.9089615169391776 |

---

## 4. Threshold Instability Audit (Top 15 Genes)
Ensemble threshold standard deviations and IQRs:

| gene | threshold_std_instability | threshold_iqr |
| --- | --- | --- |
| MISP | 0.2939899091235 | 0.3148972533575113 |
| OCIAD2 | 0.0095736059580269 | 0.0107225783240405 |
| MMP12 | 0.0220799345862613 | 0.0263315366984431 |
| CCNB1 | 0.0417661586595062 | 0.0449482187628647 |
| AGR2 | 0.2900457034734938 | 0.3084794816233119 |
| PLAC8 | 0.0234246257285141 | 0.0281972362323263 |
| LAMA3 | 0.4023131021354224 | 0.4794756435667157 |
| CEACAM5 | 0.0984764933069095 | 0.1177144045189396 |
| MMP9 | 0.0779806405713783 | 0.086201290736759 |
| CST1 | 0.2613835538362081 | 0.303714808607933 |
| GRN | 0.0227026820801638 | 0.0274923935108576 |
| RCN1 | 0.0414750648719722 | 0.0456525981618171 |
| CTTN | 0.1315102479082387 | 0.1403224424213937 |
| SDC1 | 0.0845303428349702 | 0.0941014393209985 |
| TPX2 | 0.1722119354068063 | 0.1856316087335003 |

---

## 5. Top-N Search-Space Stability Sweeps
The optimal pair selection metrics across different search spaces (top 20, 50, 100, 200 consensus genes):

| search_space_top_N | evaluated_genes | evaluated_pairs | top_ranked_pair | pair_score | discovery_sensitivity | discovery_specificity | GSE62452_validation_sensitivity | GSE62452_validation_specificity | tumor_spearman_r | mean_threshold_instability | redundancy_category |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 20 | 190 | OCIAD2 + EDIL3 | 0.8538227235560543 | 0.9831460674157304 | 1.0 | 0.8115942028985508 | 0.639344262295082 | 0.0120732716087298 | 0.022837552745406 | weak correlation / high independence |
| 50 | 50 | 1225 | OCIAD2 + EDIL3 | 0.8538227235560543 | 0.9831460674157304 | 1.0 | 0.8115942028985508 | 0.639344262295082 | 0.0120732716087298 | 0.022837552745406 | weak correlation / high independence |
| 100 | 100 | 4950 | PKM + ADAM22 | 0.8784213842101507 | 0.9662921348314608 | 0.994011976047904 | 0.7101449275362319 | 0.9016393442622952 | 0.0634428696647769 | 0.0191213752636675 | weak correlation / high independence |
| 200 | 200 | 19900 | PKM + ADAM22 | 0.8784213842101507 | 0.9662921348314608 | 0.994011976047904 | 0.7101449275362319 | 0.9016393442622952 | 0.0634428696647769 | 0.0191213752636675 | weak correlation / high independence |

---

## 6. Overlap of Top 20 Pairs Across Cutoffs
Jaccard similarity and shared top-ranked pairs between search spaces:

| space_1 | space_2 | top20_pairs_shared | jaccard_similarity |
| --- | --- | --- | --- |
| top_20 | top_20 | 20 | 1.0 |
| top_20 | top_50 | 3 | 0.081081081081081 |
| top_20 | top_100 | 1 | 0.0256410256410256 |
| top_20 | top_200 | 0 | 0.0 |
| top_50 | top_50 | 20 | 1.0 |
| top_50 | top_100 | 4 | 0.1111111111111111 |
| top_50 | top_200 | 0 | 0.0 |
| top_100 | top_100 | 20 | 1.0 |
| top_100 | top_200 | 3 | 0.081081081081081 |
| top_200 | top_200 | 20 | 1.0 |

---

## 7. Locked Final External Validation (GSE28735)
Performance of the final default selected v3 candidate pair (PKM + ADAM22) on the locked external validation cohort:

| gene_A | gene_B | K_final_A | K_final_B | tumor_sample_count | normal_sample_count | sensitivity | specificity | ROC_AUC | TP | FP | TN | FN | GSE28735_Spearman_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PKM | ADAM22 | 0.8047205189285296 | 0.6238650586831749 | 45 | 45 | 0.8 | 0.8222222222222222 | 0.8587654320987654 | 36 | 8 | 37 | 9 | 0.1108036890645586 |

---

## 8. Locked Validation Uncertainty Intervals
Approximate 95% confidence intervals for the locked GSE28735 point estimates:

> [!NOTE]
> Sensitivity, specificity, and accuracy use Wilson score intervals from the locked aggregate confusion matrix. ROC-AUC uses the Hanley-McNeil approximation because sample-level gate scores are not stored in the repository. Prefer bootstrap or DeLong intervals after exporting sample-level scores.

| dataset | gene_A | gene_B | metric | estimate | ci_method | ci_low | ci_high | n_positive | n_negative | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GSE28735 | PKM | ADAM22 | sensitivity | 0.8 | Wilson score 95% CI | 0.6617703088385799 | 0.8910387319216871 | 45 | 45 | Computed from locked aggregate confusion matrix. |
| GSE28735 | PKM | ADAM22 | specificity | 0.8222222222222222 | Wilson score 95% CI | 0.6867017537354023 | 0.9070561048589584 | 45 | 45 | Computed from locked aggregate confusion matrix. |
| GSE28735 | PKM | ADAM22 | accuracy | 0.8111111111111111 | Wilson score 95% CI | 0.7181637647568584 | 0.8785874015586717 | 45 | 45 | Computed from locked aggregate confusion matrix. |
| GSE28735 | PKM | ADAM22 | ROC_AUC | 0.8587654320987654 | Hanley-McNeil approximate 95% CI | 0.7802785578717782 | 0.9372523063257526 | 45 | 45 | Approximate SE=0.0400. Prefer bootstrap or DeLong CI after sample-level gate scores are exported. |

---

## 9. scRNA-seq validation (GSE154778)
Expression and co-expression rates of the final v3 selected pair across independently annotated cell types:

> [!NOTE]
> Single-cell validation is a preliminary marker-score-based targeted validation, not a full unbiased scRNA-seq annotation workflow.

| rank | gene_A | gene_B | cell_type | n_cells | mean_expression_A | mean_expression_B | coexpression_fraction_gt_0 | coexpression_fraction_gt_0_5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| final_pair | PKM | ADAM22 | B cells | 191 | 1.3896469 | 0.0 | 0.0 | 0.0 |
| final_pair | PKM | ADAM22 | CAF / fibroblast | 1942 | 1.6533201 | 0.14025353 | 0.0777548918640576 | 0.0777548918640576 |
| final_pair | PKM | ADAM22 | CD8 T cells | 79 | 1.5195802 | 0.016087497 | 0.0126582278481012 | 0.0126582278481012 |
| final_pair | PKM | ADAM22 | NK cells | 9 | 1.469836 | 0.0 | 0.0 | 0.0 |
| final_pair | PKM | ADAM22 | T cells | 180 | 1.37528 | 0.016209546 | 0.0055555555555555 | 0.0055555555555555 |
| final_pair | PKM | ADAM22 | Tregs | 20 | 2.2103174 | 0.0 | 0.0 | 0.0 |
| final_pair | PKM | ADAM22 | acinar-like cells | 2256 | 1.2177994 | 0.0021286847 | 0.000886524822695 | 0.000886524822695 |
| final_pair | PKM | ADAM22 | dendritic cells | 24 | 1.8297272 | 0.0 | 0.0 | 0.0 |
| final_pair | PKM | ADAM22 | endocrine cells | 8 | 1.4241223 | 0.34548524 | 0.25 | 0.25 |
| final_pair | PKM | ADAM22 | endothelial | 113 | 1.3073344 | 0.038949292 | 0.0088495575221238 | 0.0088495575221238 |
| final_pair | PKM | ADAM22 | macrophages / monocytes | 1557 | 1.7623861 | 0.005580951 | 0.0038535645472061 | 0.0038535645472061 |
| final_pair | PKM | ADAM22 | mast cells | 24 | 2.2090404 | 0.0 | 0.0 | 0.0 |
| final_pair | PKM | ADAM22 | pericytes / VSMC | 120 | 1.4248195 | 0.041918207 | 0.025 | 0.025 |
| final_pair | PKM | ADAM22 | plasma cells | 752 | 1.1481764 | 0.014631667 | 0.0066489361702127 | 0.0066489361702127 |
| final_pair | PKM | ADAM22 | tumor-associated epithelial / putative malignant ductal epithelial | 7649 | 1.6578722 | 0.0046018437 | 0.0026147208785462 | 0.0026147208785462 |
| alternative_pair_1 | MMP9 | NQO1 | B cells | 191 | 0.042072844 | 0.28334096 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | CAF / fibroblast | 1942 | 0.041839372 | 0.27184063 | 0.0046343975283213 | 0.0046343975283213 |
| alternative_pair_1 | MMP9 | NQO1 | CD8 T cells | 79 | 0.021295814 | 0.25884956 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | NK cells | 9 | 0.0 | 0.0 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | T cells | 180 | 0.0534013 | 0.10794489 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | Tregs | 20 | 0.0 | 0.18630828 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | acinar-like cells | 2256 | 0.0054638777 | 1.1151856 | 0.0022163120567375 | 0.0022163120567375 |
| alternative_pair_1 | MMP9 | NQO1 | dendritic cells | 24 | 0.17670971 | 0.19472907 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | endocrine cells | 8 | 0.0 | 0.3837889 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | endothelial | 113 | 0.097622804 | 0.542735 | 0.0176991150442477 | 0.0176991150442477 |
| alternative_pair_1 | MMP9 | NQO1 | macrophages / monocytes | 1557 | 0.36770687 | 0.14252624 | 0.02504816955684 | 0.02504816955684 |
| alternative_pair_1 | MMP9 | NQO1 | mast cells | 24 | 0.0 | 0.30088133 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | pericytes / VSMC | 120 | 0.044949587 | 0.30965927 | 0.0 | 0.0 |
| alternative_pair_1 | MMP9 | NQO1 | plasma cells | 752 | 0.036759403 | 0.85816276 | 0.0159574468085106 | 0.0159574468085106 |
| alternative_pair_1 | MMP9 | NQO1 | tumor-associated epithelial / putative malignant ductal epithelial | 7649 | 0.018362759 | 1.1299046 | 0.0095437312066936 | 0.0095437312066936 |
| alternative_pair_2 | LOXL1 | NQO1 | B cells | 191 | 0.11043781 | 0.28334096 | 0.0471204188481675 | 0.0471204188481675 |
| alternative_pair_2 | LOXL1 | NQO1 | CAF / fibroblast | 1942 | 0.84590137 | 0.27184063 | 0.0911431513903192 | 0.0911431513903192 |
| alternative_pair_2 | LOXL1 | NQO1 | CD8 T cells | 79 | 0.016291192 | 0.25884956 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | NK cells | 9 | 0.10870401 | 0.0 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | T cells | 180 | 0.04457811 | 0.10794489 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | Tregs | 20 | 0.07360019 | 0.18630828 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | acinar-like cells | 2256 | 0.10181729 | 1.1151856 | 0.050531914893617 | 0.050531914893617 |
| alternative_pair_2 | LOXL1 | NQO1 | dendritic cells | 24 | 0.04031192 | 0.19472907 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | endocrine cells | 8 | 0.0 | 0.3837889 | 0.0 | 0.0 |
| alternative_pair_2 | LOXL1 | NQO1 | endothelial | 113 | 0.032777753 | 0.542735 | 0.0088495575221238 | 0.0088495575221238 |
| alternative_pair_2 | LOXL1 | NQO1 | macrophages / monocytes | 1557 | 0.025053158 | 0.14252624 | 0.0051380860629415 | 0.0051380860629415 |
| alternative_pair_2 | LOXL1 | NQO1 | mast cells | 24 | 0.11243045 | 0.30088133 | 0.0833333333333333 | 0.0833333333333333 |
| alternative_pair_2 | LOXL1 | NQO1 | pericytes / VSMC | 120 | 0.34848708 | 0.30965927 | 0.0916666666666666 | 0.0916666666666666 |
| alternative_pair_2 | LOXL1 | NQO1 | plasma cells | 752 | 0.34389803 | 0.85816276 | 0.1994680851063829 | 0.1994680851063829 |
| alternative_pair_2 | LOXL1 | NQO1 | tumor-associated epithelial / putative malignant ductal epithelial | 7649 | 0.083285965 | 1.1299046 | 0.0444502549352856 | 0.0444502549352856 |
| alternative_pair_3 | PXDN | NQO1 | B cells | 191 | 0.0088741295 | 0.28334096 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | CAF / fibroblast | 1942 | 0.3501258 | 0.27184063 | 0.0314109165808444 | 0.0314109165808444 |
| alternative_pair_3 | PXDN | NQO1 | CD8 T cells | 79 | 0.031475447 | 0.25884956 | 0.0126582278481012 | 0.0126582278481012 |
| alternative_pair_3 | PXDN | NQO1 | NK cells | 9 | 0.0 | 0.0 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | T cells | 180 | 0.0 | 0.10794489 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | Tregs | 20 | 0.0 | 0.18630828 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | acinar-like cells | 2256 | 0.30104643 | 1.1151856 | 0.1679964539007092 | 0.1679964539007092 |
| alternative_pair_3 | PXDN | NQO1 | dendritic cells | 24 | 0.0 | 0.19472907 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | endocrine cells | 8 | 0.0 | 0.3837889 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | endothelial | 113 | 0.6582272 | 0.542735 | 0.1769911504424778 | 0.1769911504424778 |
| alternative_pair_3 | PXDN | NQO1 | macrophages / monocytes | 1557 | 0.014439208 | 0.14252624 | 0.001926782273603 | 0.001926782273603 |
| alternative_pair_3 | PXDN | NQO1 | mast cells | 24 | 0.06956904 | 0.30088133 | 0.0 | 0.0 |
| alternative_pair_3 | PXDN | NQO1 | pericytes / VSMC | 120 | 0.4424364 | 0.30965927 | 0.075 | 0.075 |
| alternative_pair_3 | PXDN | NQO1 | plasma cells | 752 | 0.06593483 | 0.85816276 | 0.0305851063829787 | 0.0305851063829787 |
| alternative_pair_3 | PXDN | NQO1 | tumor-associated epithelial / putative malignant ductal epithelial | 7649 | 0.01639973 | 1.1299046 | 0.0073212184599294 | 0.0073212184599294 |

---

## 10. Patient Prevalence and Co-expression Heterogeneity
Double-positive prevalence in ductal epithelial and CAF compartments across individual patients:

| patient_id | cell_type | n_cells | mean_expression_A | mean_expression_B | coexpression_fraction_gt_0 | coexpression_fraction_gt_0_5 |
| --- | --- | --- | --- | --- | --- | --- |
| MET01 | tumor-associated epithelial / putative malignant ductal epithelial | 366 | 1.6273937 | 0.0 | 0.0 | 0.0 |
| MET02 | tumor-associated epithelial / putative malignant ductal epithelial | 701 | 2.182223 | 0.0015955295 | 0.0014265335235378 | 0.0014265335235378 |
| MET03 | tumor-associated epithelial / putative malignant ductal epithelial | 36 | 1.3991795 | 0.0 | 0.0 | 0.0 |
| MET03 | CAF / fibroblast | 1 | 1.3112372 | 0.0 | 0.0 | 0.0 |
| MET04 | tumor-associated epithelial / putative malignant ductal epithelial | 113 | 1.1463174 | 0.0 | 0.0 | 0.0 |
| MET05 | tumor-associated epithelial / putative malignant ductal epithelial | 512 | 1.614785 | 0.0 | 0.0 | 0.0 |
| MET06 | tumor-associated epithelial / putative malignant ductal epithelial | 2254 | 1.5139065 | 0.0039818594 | 0.0026619343389529 | 0.0026619343389529 |
| MET06 | CAF / fibroblast | 1 | 1.4142317 | 0.0 | 0.0 | 0.0 |
| P01 | tumor-associated epithelial / putative malignant ductal epithelial | 75 | 2.0680513 | 0.01979397 | 0.0133333333333333 | 0.0133333333333333 |
| P01 | CAF / fibroblast | 157 | 1.8291813 | 0.010531263 | 0.0063694267515923 | 0.0063694267515923 |
| P02 | tumor-associated epithelial / putative malignant ductal epithelial | 70 | 1.9229294 | 0.0 | 0.0 | 0.0 |
| P02 | CAF / fibroblast | 1 | 1.6964121 | 0.0 | 0.0 | 0.0 |
| P03 | tumor-associated epithelial / putative malignant ductal epithelial | 367 | 1.8484219 | 0.0 | 0.0 | 0.0 |
| P03 | CAF / fibroblast | 148 | 1.4356141 | 0.019801784 | 0.0135135135135135 | 0.0135135135135135 |
| P04 | tumor-associated epithelial / putative malignant ductal epithelial | 185 | 2.1587737 | 0.0 | 0.0 | 0.0 |
| P04 | CAF / fibroblast | 72 | 2.0133324 | 0.024555467 | 0.0138888888888888 | 0.0138888888888888 |
| P05 | tumor-associated epithelial / putative malignant ductal epithelial | 138 | 1.9656852 | 0.024995362 | 0.0144927536231884 | 0.0144927536231884 |
| P05 | CAF / fibroblast | 610 | 1.8522109 | 0.19810706 | 0.1098360655737704 | 0.1098360655737704 |
| P06 | tumor-associated epithelial / putative malignant ductal epithelial | 321 | 1.5567445 | 0.0 | 0.0 | 0.0 |
| P06 | CAF / fibroblast | 278 | 1.2878431 | 0.17382999 | 0.0935251798561151 | 0.0935251798561151 |
| P07 | tumor-associated epithelial / putative malignant ductal epithelial | 134 | 1.5424038 | 0.02185349 | 0.0149253731343283 | 0.0149253731343283 |
| P07 | CAF / fibroblast | 151 | 1.3364348 | 0.19323055 | 0.0927152317880794 | 0.0927152317880794 |
| P08 | tumor-associated epithelial / putative malignant ductal epithelial | 774 | 1.5561211 | 0.008953949 | 0.0025839793281653 | 0.0025839793281653 |
| P08 | CAF / fibroblast | 139 | 1.5734864 | 0.15015683 | 0.0935251798561151 | 0.0935251798561151 |
| P09 | tumor-associated epithelial / putative malignant ductal epithelial | 304 | 1.8503928 | 0.01618175 | 0.0098684210526315 | 0.0098684210526315 |
| P09 | CAF / fibroblast | 255 | 1.6879833 | 0.13791779 | 0.0901960784313725 | 0.0901960784313725 |
| P10 | tumor-associated epithelial / putative malignant ductal epithelial | 1299 | 1.5585904 | 0.0041524563 | 0.0023094688221709 | 0.0023094688221709 |
| P10 | CAF / fibroblast | 129 | 1.7278496 | 0.09016738 | 0.0310077519379844 | 0.0310077519379844 |
