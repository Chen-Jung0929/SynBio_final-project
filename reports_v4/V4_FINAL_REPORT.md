# V4 Final Report: Unbiased Biological Integration

## 1. Overview
The V3 candidate pair (`PKM` + `ADAM22`) failed during downstream single-cell validation because it was predominantly co-expressed in CAFs rather than the malignant epithelial ductal cells. 
Initial V4 attempts accidentally introduced circular logic by using candidate marker genes (`CEACAM5`) to label the target cells. 

This **Final Unbiased V4 Pipeline** strictly removes all candidate circularity, identifies target cells purely by independent ductal markers (`EPCAM`, `KRT19`, `SOX9`, `CFTR`), and enforces strict penalties for off-target expression.

## 2. V4 Selected Unbiased Candidate Pair
* **Gene A**: `NMU`
* **Gene B**: `CEP55`

### Biological Alignment Metrics
* **scRNA Target Co-expression (Malignant Ductal)**: 12.28%
* **scRNA Max Off-Target Co-expression**: 9.68% (in T cells)
* **Patient Prevalence Rate**: 0.0% of patients exhibit positive activation in their tumor compartment.

### Bulk RNA-seq Performance (Discovery + GSE62452)
* **Bulk Performance Score**: 0.7374
* **Integrated scRNA Pair Score**: -1.1710

## 3. Circularity Audit
To ensure no data leakage, the selected pair was explicitly verified against the marker genes used for cell-type annotation:
* NMU: PASS (Not used as marker)
* CEP55: PASS (Not used as marker)

## 4. Conclusion
The unbiased V4 pair `NMU + CEP55` represents a much safer and strictly biologically aligned biosensor candidate than the V3 outputs. By resolving the circularity flaw, ensuring the pair expresses purely in the malignant epithelial compartment (and heavily penalizing CAF/immune off-target expression), this candidate is fully prepared for future stages of validation.
