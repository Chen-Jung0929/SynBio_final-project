# Codex Review: V5 scRNA-First Discovery Constraints

Date: 2026-06-04

## Position

I agree with the V5 reversal strategy. V1-V4 show that bulk-first ranking can
look strong at the cohort level while failing the single-cell requirement for an
AND-gate biosensor. V5 should discover pairs directly in malignant epithelial
single cells, then validate backward in bulk cohorts.

## Required V5 Constraints

1. **Target-cell prevalence**
   - Require pair co-expression in a high fraction of malignant ductal /
     epithelial cells.
   - Report patient-level prevalence, not only pooled-cell prevalence.

2. **Off-target ceiling**
   - Reject pairs with high co-expression in CAF/fibroblast, T cell, B cell,
     macrophage, mast cell, endothelial, normal ductal, normal acinar, or
     endocrine compartments.
   - Report the maximum off-target compartment explicitly.

3. **Patient robustness**
   - A pair should not be selected because one patient dominates the scRNA
     signal.
   - Report the number and fraction of patients passing a minimum target
     activation threshold.

4. **Annotation non-circularity**
   - Candidate genes must not be used as malignant-cell or ductal-cell markers.
   - Keep marker-overlap audits for every selected pair.

5. **Expression dynamic range**
   - Prefer genes with separable ON/OFF distributions rather than weak,
     ubiquitous expression.
   - Report expression prevalence and expression magnitude separately.

6. **Bulk backward validation**
   - After scRNA-first discovery, test shortlisted pairs in TCGA/GTEx, GSE62452,
     and GSE28735.
   - If probe mapping is unavailable, mark validation unavailable rather than
     simulating results.

7. **Wet-lab feasibility**
   - Add filters for input sensing modality, available promoters/regulatory
     elements, expected dynamic range, essential-gene risk, and whether the
     input is intracellular, secreted, or surface-associated.

## Suggested V5 Outputs

```text
analysis_v5/
results_v5/tables/scRNA_pair_search_results.csv
results_v5/tables/v5_patient_prevalence_summary.csv
results_v5/audit/v5_marker_overlap_audit.csv
results_v5/audit/v5_offtarget_compartment_audit.csv
results_v5/audit/v5_bulk_backward_validation.csv
reports_v5/V5_FINAL_REPORT.md
reports_v5/V5_AUDIT_REPORT.md
```

## Bottom Line

V5 should be framed as a better computational candidate-discovery strategy, not
as proof of a working diagnostic or synthetic circuit. The strongest next
candidate will be one that is target-prevalent, patient-robust, off-target-low,
non-circularly annotated, and still detectable in independent bulk cohorts.
