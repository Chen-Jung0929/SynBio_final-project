with open("src/generate_reports.py", "r") as f:
    code = f.read()

# Define the new generate_latex_en function body (excluding the def line)
new_body = """
    filename = "pdac_biosensor_report_en_revised.tex" if is_revised else "pdac_biosensor_report_en.tex"
    filepath = os.path.join(LATEX_DIR, "en", filename)
    
    en_sections_esc = {k: (escape_text_for_latex(v) if isinstance(v, str) else v) for k, v in globals()['en_sections'].items()}
    en_secs = en_sections_esc

    def make_latex_table(headers, data, caption, label, spec=None, span_columns=False):
        actual_span = span_columns and is_revised
        if spec is None:
            spec = "l" + "c"*(len(headers)-1)
        env = "table*" if actual_span else "table"
        pos = "[t]" if actual_span else "[H]"
        latex = f"\\\\begin{{{env}}}{pos}\\n\\\\centering\\n"
        latex += f"\\\\caption{{{caption}}}\\\\label{{{label}}}\\n"
        if actual_span:
            latex += f"\\\\resizebox{{\\\\textwidth}}{{!}}{{\\n"
        else:
            latex += f"\\\\resizebox{{\\\\linewidth}}{{!}}{{\\n"
        latex += f"\\\\begin{{tabular}}{{{spec}}}\\n\\\\toprule\\n"
        escaped_headers = [h.replace("%", "\\\\%").replace("_", "\\\\_") for h in headers]
        latex += " & ".join([f"\\\\textbf{{{h}}}" for h in escaped_headers]) + " \\\\\\\\n\\\\midrule\\n"
        for row in data:
            escaped_row = [str(x).replace("%", "\\\\%").replace("_", "\\\\_").replace("&", "\\&").replace("+-", "$\\\\pm$") for x in row]
            latex += " & ".join(escaped_row) + " \\\\\\\\n"
        latex += f"\\\\bottomrule\\n\\\\end{{tabular}}\\n}}\\n\\\\end{{{env}}}\\n"
        return latex

    fig_width = "0.95\\\\linewidth" if is_revised else "0.7\\\\textwidth"
    fig_placement = "[htbp]" if is_revised else "[H]"
    
    if is_revised:
        intro_text = en_secs['Introduction']
        if intro_text.startswith("Pancreatic"):
            intro_text = "\\\\IEEEPARstart{P}{ancreatic}" + intro_text[10:]
        target_sentence = "Synthetic biology provides a powerful paradigm to address this challenge by engineering logic-gated genetic circuits. "
        replacement_sentence = target_sentence + "\\\\IEEEpubidadjcol "
        intro_text = intro_text.replace(target_sentence, replacement_sentence)
        
        preamble = f\"\"\"% !TEX program = xelatex
% !BIB program = biber
% Auto-generated English report for PDAC Biosensor Project
\\\\documentclass[12pt, journal]{{IEEEtran}}

\\\\usepackage{{fontspec}}
\\\\usepackage{{graphicx}}
\\\\graphicspath{{{{../shared/figures/}}}}
\\\\usepackage{{float}}
\\\\usepackage{{booktabs}}
\\\\usepackage{{amsmath}}
\\\\usepackage{{amssymb}}
\\\\usepackage{{siunitx}}
\\\\usepackage{{xcolor}}
\\\\usepackage{{url}}
\\\\usepackage{{hyperref}}
\\\\usepackage{{orcidlink}}
\\\\usepackage{{stfloats}}
\\\\usepackage{{subcaption}}
\\\\usepackage{{array}}
\\\\usepackage{{multirow}}
\\\\usepackage{{tabularx}}

\\\\setmainfont{{Times New Roman}}
\\\\setsansfont{{Arial}}
\\\\setmonofont{{Courier New}}

\\\\usepackage[style=ieee,backend=biber]{{biblatex}}
\\\\addbibresource{{references_en.bib}}

\\\\markboth{{Cognitive Security Vol. X Issue. X}}{{}}
\\\\IEEEpubid{{XXXXXXX/csip.XXXXXXXX  ~\\\\copyright~2026 CSI Press}}

\\\\title{{{en_secs['Title']}}}

\\\\author{{\\\\IEEEauthorblockN{{SHIH, Chen-Jung\\\\IEEEauthorrefmark{{1}}, SU, Te-Fang\\\\IEEEauthorrefmark{{1}}, LIAO, Xuan-You\\\\IEEEauthorrefmark{{2}}, and LIN, Chia-I\\\\IEEEauthorrefmark{{2}}}} \\\\\\\\
\\\\vspace{{4pt}}
\\\\IEEEauthorblockA{{\\\\footnotesize
\\\\IEEEauthorrefmark{{1}}Department of Life Science, National Taiwan University, Taipei, Taiwan \\\\\\\\
\\\\IEEEauthorrefmark{{2}}Department of Biochemical Science and Technology, National Taiwan University, Taipei, Taiwan}}
\\\\thanks{{\\\\hrule \\\\vspace{{4pt}} \\\\noindent Manuscript received May 25, 2026; revised May 25, 2026. \\\\vspace{{3pt}} \\\\\\\\
Corresponding Author Email: \\\\href{{mailto:email@example.com}}{{email@example.com}} \\\\vspace{{3pt}}}}
}}

\\\\IEEEaftertitletext{{\\\\vspace{{-1\\\\baselineskip}}\\\\noindent\\\\begin{{abstract}}
{en_secs['Abstract']}
\\\\end{{abstract}}
\\\\noindent\\\\begin{{IEEEkeywords}}
Pancreatic ductal adenocarcinoma, AND-gate biosensor, transcriptomics, explainable AI, UBE2S, CCR6
\\\\end{{IEEEkeywords}}
\\\\vspace{{1\\\\baselineskip}}}}

\\\\begin{{document}}
\\\\maketitle
\"\"\"
    else:
        intro_text = en_secs['Introduction']
        doc_class = "\\\\documentclass[12pt, a4paper]{article}"
        style_file = "report_style.tex"
        
        preamble = f\"\"\"% !TEX program = xelatex
% !BIB program = biber
% Auto-generated English report for PDAC Biosensor Project
{doc_class}

\\\\input{{../shared/{style_file}}}
\\\\input{{../shared/macros.tex}}

\\\\setmainfont{{Times New Roman}}
\\\\setsansfont{{Arial}}
\\\\setmonofont{{Courier New}}

\\\\usepackage[style=apa,backend=biber]{{biblatex}}
\\\\addbibresource{{references_en.bib}}

\\\\title{{{en_secs['Title']}}}
\\\\author{{{en_secs['Author']}}}
\\\\affil{{{en_secs['Affiliation']}}}
\\\\date{{{en_secs['Date']}}}

\\\\begin{{document}}
\\\\maketitle
\\\\newpage

\\\\begin{{abstract}}
{en_secs['Abstract']}
\\\\end{{abstract}}
\\\\newpage
\"\"\"

    content = preamble + f\"\"\"
\\\\section{{Introduction}}
{intro_text}

\\\\section{{Scientific Rationale and Unmet Need}}
{en_secs['Rationale']}

\\\\section{{Data Sources}}
{en_secs['DataSources']}

{make_latex_table(t1_headers, t1_data, "Data Cohorts and Sample Size Distribution", "tab:datasets", span_columns=False)}

\\\\section{{Computational Pipeline}}
{en_secs['Pipeline']}

\\\\section{{Quality Control and Batch-Effect Assessment}}
{en_secs['QC']}

\\\\section{{Differential Expression Analysis}}
{en_secs['DE']}

\\\\begin{{figure}}{fig_placement}
\\\\centering
\\\\includegraphics[width={fig_width}]{{volcano_discovery.png}}
\\\\caption{{Volcano plot highlighting significantly differentially expressed genes in the discovery cohort (TCGA-PAAD vs GTEx Normal Pancreas). UBE2S and CCR6 are annotated as significant upregulated candidates.}}
\\\\label{{fig:volcano}}
\\\\end{{figure}}

{make_latex_table(t2_headers, t2_data, "Top 10 Differentially Expressed Genes Sorted by Specificity Score", "tab:top_de", span_columns=True)}

\\\\section{{Machine Learning Classifier Performance}}
{en_secs['ML']}

{make_latex_table(t3_headers, t3_data, "Machine Learning Classifier Performance and Cross-Validation Summary", "tab:ml_perf", span_columns=True)}

\\\\section{{SHAP-Based Explainable AI Analysis}}
{en_secs['SHAP']}

\\\\begin{{figure}}{fig_placement}
\\\\centering
\\\\includegraphics[width={fig_width}]{{shap_summary.png}}
\\\\caption{{SHAP summary plot showing feature importances for the top-ranked genes driving the L1 Logistic Regression classifier.}}
\\\\label{{fig:shap_summary}}
\\\\end{{figure}}

{make_latex_table(t4_headers, t4_data, "Top 10 SHAP Feature Importance and Inferred Expression Thresholds", "tab:shap_thresh", span_columns=True)}

\\\\section{{Candidate Gene Pair Selection}}
{en_secs['PairSelection']}

{make_latex_table(t5_headers, t5_data, "Detailed Molecular Profile of Selected Candidate Pair", "tab:candidate_pair", span_columns=True)}

\\\\section{{Orthogonality Assessment}}
{en_secs['Orthogonality']}

\\\\begin{{figure}}{fig_placement}
\\\\centering
\\\\includegraphics[width={fig_width}]{{gene_pair_scatter_final.png}}
\\\\caption{{Scatter plot of UBE2S vs CCR6 rescaled expression in discovery cohort, demonstrating decision boundary quadrants and sample clustering.}}
\\\\label{{fig:scatter}}
\\\\end{{figure}}

\\\\section{{Need for Single-Cell and Spatial Validation}}
{en_secs['SingleCell']}

\\\\section{{Hill-Equation-Based AND Gate Modeling}}
{en_secs['HillModeling']}

\\\\section{{In Silico Validation}}
{en_secs['InSilico']}

\\\\begin{{figure}}{fig_placement}
\\\\centering
\\\\includegraphics[width={fig_width}]{{and_gate_heatmap_final.png}}
\\\\caption{{2D Contour heatmap demonstrating simulation output of UBE2S AND CCR6 logical AND gate, with rescaled expression and tumor/normal sample overlays.}}
\\\\label{{fig:heatmap}}
\\\\end{{figure}}

{make_latex_table(t6_headers, t6_data, "AND Gate Simulation Performance Summary in Discovery Cohort", "tab:and_perf", span_columns=False)}

\\\\begin{{figure}}{fig_placement}
\\\\centering
\\\\includegraphics[width={fig_width}]{{roc_curves.png}}
\\\\caption{{ROC curves comparing individual inputs (UBE2S, CCR6) against the combined logic gate output.}}
\\\\label{{fig:roc}}
\\\\end{{figure}}

{make_latex_table(t7_headers, t7_data, "External Validation Results on GSE62452 Dataset", "tab:ext_val", span_columns=True)}

\\\\section{{Robustness and Negative Controls}}
{en_secs['Robustness']}

\\\\section{{Limitations}}
{en_secs['Limitations']}

\\\\section{{Future Experimental Directions}}
{en_secs['WetLab']}

\\\\section{{Conclusion}}
{en_secs['Conclusion']}

\"\"\"
    bib_prefix = "" if is_revised else "\\\\newpage\\n"
    content += f\"\"\"{bib_prefix}\\\\nocite{{*}}
\\\\printbibliography[title={{References}}]

\"\"\"
    supp_prefix = "\\\\newpage\\n\\\\onecolumn\\n" if is_revised else "\\\\newpage\\n"
    
    content += f\"\"\"{supp_prefix}\\\\section{{Supplementary Tables and Figures}}
{en_secs['Supplementary']}

\\\\subsection{{Supplementary Table 1: Parameter Sweep}}
{make_latex_table(["Hill Coefficient (n)", "Basal Leakiness (P_basal)", "ROC-AUC", "Accuracy", "Sensitivity", "Specificity"], 
                  [[str(x[0]), str(x[1]), f"{x[2]:.4f}", f"{x[4]*100:.1f}\\\\%", f"{x[5]*100:.1f}\\\\%", f"{x[6]*100:.1f}\\\\%"] for x in and_sweep.values[:6]] if and_sweep is not None else [], 
                  "Hill Equation Grid Search Parameter Sweep Performance", "tab:supp_sweep", span_columns=True)}

\\\\subsection{{Supplementary Table 2: Threshold Sensitivity}}
{make_latex_table(t8_headers, t8_data, "Sensitivity Analysis of K Parameter Perturbations", "tab:supp_sensitivity", span_columns=True)}

\\\\subsection{{Supplementary Figures}}
\\\\begin{{figure}}[H]
\\\\centering
\\\\begin{{subfigure}}[b]{{0.48\\\\textwidth}}
\\\\centering
\\\\includegraphics[width=\\\\textwidth]{{shap_dependence_top_genes/UBE2S_shap_dependence.png}}
\\\\caption{{UBE2S SHAP dependence}}
\\\\end{{subfigure}}
\\\\hfill
\\\\begin{{subfigure}}[b]{{0.48\\\\textwidth}}
\\\\centering
\\\\includegraphics[width=\\\\textwidth]{{shap_dependence_top_genes/CCR6_shap_dependence.png}}
\\\\caption{{CCR6 SHAP dependence}}
\\\\end{{subfigure}}
\\\\caption{{SHAP dependence plots for selected candidate genes UBE2S and CCR6 showing threshold transition inflection points.}}
\\\\label{{fig:supp_shap_dependence}}
\\\\end{{figure}}

\\\\end{{document}}
\"\"\"
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Generated {filepath}")
"""

start_marker = "def generate_latex_en(is_revised=False):"
end_marker = "def generate_latex_zh(is_revised=False):"

parts = code.split(start_marker, 1)
subparts = parts[1].split(end_marker, 1)

new_code = parts[0] + start_marker + new_body + "\n\n" + end_marker + subparts[1]

with open("src/generate_reports.py", "w") as f:
    f.write(new_code)

print("Patch applied successfully via string splitting!")
