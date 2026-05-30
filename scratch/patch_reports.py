import os

def main():
    filepath = '/Users/Janet/Documents/Antigravity/SynBio final/src/generate_reports.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # 1. Update imports around line 7-10
    # Let's find where 'from docx.oxml' is
    oxml_idx = -1
    for i, line in enumerate(lines[:20]):
        if 'from docx.oxml' in line:
            oxml_idx = i
            break
            
    if oxml_idx != -1:
        # Insert additional imports
        lines.insert(oxml_idx + 1, "from docx.enum.section import WD_SECTION\nimport shutil\nimport time")
        
    # 2. In Table 5 setup (originally line 107), replace Pearson with Spearman
    # Let's find the lines with Pairwise Pearson Correlation
    for i, line in enumerate(lines):
        if 'Pairwise Pearson Correlation' in line:
            lines[i] = '        ["Pairwise Spearman Correlation (r_s)", f"{r[\'correlation\']:.4f}", "—", "—"],'
            print(f"Updated Pearson to Spearman at line {i+1}")
            
    # 3. We want to keep lines from 0 to 594 (which is up to the end of zh_sections)
    # Let's find where CJK main font settings start (i.e. generate_latex_en or escape_text_for_latex)
    cutoff_idx = -1
    for i, line in enumerate(lines):
        if 'def escape_text_for_latex' in line:
            cutoff_idx = i
            break
            
    if cutoff_idx == -1:
        print("Error: def escape_text_for_latex not found!")
        return
        
    print(f"Cutting off from line {cutoff_idx+1}")
    header_lines = lines[:cutoff_idx]
    
    # 4. Append our new generators and helpers
    appended_code = """
def escape_text_for_latex(text):
    import re
    pattern = r"(\\$.*?\\$|\\\\\\[.*?\\\\\\])"
    tokens = re.split(pattern, text, flags=re.DOTALL)
    escaped_tokens = []
    for i, token in enumerate(tokens):
        if i % 2 == 0:
            escaped_token = token.replace("_", "\\\\_").replace("%", "\\\\%")
            escaped_tokens.append(escaped_token)
        else:
            escaped_tokens.append(token)
    return "".join(escaped_tokens)

def clean_math_for_word(text):
    if not isinstance(text, str):
        return text
    import re
    # Replace display equations \\\\[ ... \\\\] with simpler text representation
    def repl_display(m):
        eq = m.group(1).strip()
        eq = eq.replace(r"\\text{basal}", "basal")
        eq = eq.replace(r"\\max", "max")
        eq = eq.replace(r"\\left(", "(")
        eq = eq.replace(r"\\right)", ")")
        eq = re.sub(r"\\\\frac\\{([^{}]+)\\}\\{([^{}]+)\\}", r"(\\1/\\2)", eq)
        eq = eq.replace("{", "").replace("}", "")
        eq = eq.replace("_", "")
        return f"\\n{eq}\\n"
    
    text = re.sub(r"\\\\\\\\[(.*?)\\\\\\\\]", repl_display, text, flags=re.DOTALL)
    
    # Replace inline equations $ ... $ with simplified text
    def repl_inline(m):
        eq = m.group(1).strip()
        eq = eq.replace(r"\\text{basal}", "basal")
        eq = eq.replace(r"\\max", "max")
        eq = eq.replace(r"\\pm", "±")
        eq = eq.replace(r"\\in", "in")
        eq = eq.replace(r"\\le", "≤")
        eq = eq.replace(r"\\ge", "≥")
        eq = eq.replace(r"\\langle", "<")
        eq = eq.replace(r"\\rangle", ">")
        eq = eq.replace(r"\\infty", "∞")
        eq = eq.replace(r"\\{", "{").replace(r"\\}", "}")
        eq = eq.replace(r"\\\\", "")
        eq = re.sub(r"\\\\[a-zA-Z]+\\{([^{}]+)\\}", r"\\1", eq)
        eq = eq.replace("\\\\", "")
        return eq
        
    text = re.sub(r"\\$(.*?)\\$", repl_inline, text)
    
    text = text.replace(r"\\pm", "±")
    text = text.replace(r"\\\\&", "&")
    text = text.replace(r"\\\\%", "%")
    text = text.replace(r"\\\\_", "_")
    return text

def generate_latex_en(is_revised=False):
    filename = "pdac_biosensor_report_en_revised.tex" if is_revised else "pdac_biosensor_report_en.tex"
    filepath = os.path.join(LATEX_DIR, "en", filename)
    
    en_sections_esc = {k: (escape_text_for_latex(v) if isinstance(v, str) else v) for k, v in globals()['en_sections'].items()}
    en_sections = en_sections_esc

    def make_latex_table(headers, data, caption, label, spec=None, span_columns=False):
        actual_span = span_columns and is_revised
        if spec is None:
            spec = "l" + "c"*(len(headers)-1)
        env = "table*" if actual_span else "table"
        pos = "[t]" if actual_span else "[H]"
        latex = f"\\\\begin{{{env}}}{pos}\\n\\\\centering\\n"
        latex += f"\\\\caption{{{caption}}}\\\\label{{{label}}}\\n"
        latex += f"\\\\begin{{tabular}}{{{spec}}}\\n\\\\toprule\\n"
        escaped_headers = [h.replace("%", "\\\\%").replace("_", "\\\\_") for h in headers]
        latex += " & ".join([f"\\\\textbf{{{h}}}" for h in escaped_headers]) + " \\\\\\\\\\n\\\\midrule\\n"
        for row in data:
            escaped_row = [str(x).replace("%", "\\\\%").replace("_", "\\\\_").replace("&", "\\\\&").replace("+-", "$\\\\pm$") for x in row]
            latex += " & ".join(escaped_row) + " \\\\\\\\\\n"
        latex += f"\\\\bottomrule\\n\\\\end{{tabular}}\\n\\\\end{{{env}}}\\n"
        return latex

    doc_class = "\\\\documentclass[10pt, a4paper, twocolumn]{article}" if is_revised else "\\\\documentclass[12pt, a4paper]{article}"
    style_file = "report_style_revised.tex" if is_revised else "report_style.tex"
    fig_width = "0.95\\\\linewidth" if is_revised else "0.7\\\\textwidth"
    
    if is_revised:
        title_block = f\"\"\"
\\\\twocolumn[
  \\\\begin{{@twocolumnfalse}}
    \\\\maketitle
    \\\\begin{{abstract}}
      {en_sections['Abstract']}
    \\\\end{{abstract}}
    \\\\vspace{{1.5em}}
  \\\\end{{@twocolumnfalse}}
]
\"\"\"
    else:
        title_block = f\"\"\"
\\\\maketitle
\\\\newpage

\\\\begin{{abstract}}
{en_sections['Abstract']}
\\\\end{{abstract}}
\\\\newpage
\"\"\"

    content = f\"\"\"% Auto-generated English report for PDAC Biosensor Project
{doc_class}

\\\\input{{../shared/{style_file}}}
\\\\input{{../shared/macros.tex}}

\\\\setmainfont{{Times New Roman}}
\\\\setsansfont{{Arial}}
\\\\setmonofont{{Courier New}}

\\\\usepackage[style=apa,backend=biber]{{biblatex}}
\\\\addbibresource{{references_en.bib}}

\\\\title{{{en_sections['Title']}}}
\\\\author[1]{{{en_sections['Author']}}}
\\\\affil[1]{{{en_sections['Affiliation']}}}
\\\\date{{{en_sections['Date']}}}

\\\\begin{{document}}

{title_block}
\\\\tableofcontents
\\\\newpage

\\\\section{{Introduction}}
{en_sections['Introduction']}

\\\\section{{Scientific Rationale and Unmet Need}}
{en_sections['Rationale']}

\\\\section{{Data Sources}}
{en_sections['DataSources']}

{make_latex_table(t1_headers, t1_data, "Data Cohorts and Sample Size Distribution", "tab:datasets", span_columns=False)}

\\\\section{{Computational Pipeline}}
{en_sections['Pipeline']}

\\\\section{{Quality Control and Batch-Effect Assessment}}
{en_sections['QC']}

\\\\section{{Differential Expression Analysis}}
{en_sections['DE']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{volcano_discovery.png}}
\\\\caption{{Volcano plot highlighting significantly differentially expressed genes in the discovery cohort (TCGA-PAAD vs GTEx Normal Pancreas). UBE2S and CCR6 are annotated as significant upregulated candidates.}}
\\\\label{{fig:volcano}}
\\\\end{{figure}}

{make_latex_table(t2_headers, t2_data, "Top 10 Differentially Expressed Genes Sorted by Specificity Score", "tab:top_de", span_columns=True)}

\\\\section{{Machine Learning Classifier Performance}}
{en_sections['ML']}

{make_latex_table(t3_headers, t3_data, "Machine Learning Classifier Performance and Cross-Validation Summary", "tab:ml_perf", span_columns=True)}

\\\\section{{SHAP-Based Explainable AI Analysis}}
{en_sections['SHAP']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{shap_summary.png}}
\\\\caption{{SHAP summary plot showing feature importances for the top-ranked genes driving the L1 Logistic Regression classifier.}}
\\\\label{{fig:shap_summary}}
\\\\end{{figure}}

{make_latex_table(t4_headers, t4_data, "Top 10 SHAP Feature Importance and Inferred Expression Thresholds", "tab:shap_thresh", span_columns=True)}

\\\\section{{Candidate Gene Pair Selection}}
{en_sections['PairSelection']}

{make_latex_table(t5_headers, t5_data, "Detailed Molecular Profile of Selected Candidate Pair", "tab:candidate_pair", span_columns=True)}

\\\\section{{Orthogonality Assessment}}
{en_sections['Orthogonality']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{gene_pair_scatter_final.png}}
\\\\caption{{Scatter plot of UBE2S vs CCR6 rescaled expression in discovery cohort, demonstrating decision boundary quadrants and sample clustering.}}
\\\\label{{fig:scatter}}
\\\\end{{figure}}

\\\\section{{Need for Single-Cell and Spatial Validation}}
{en_sections['SingleCell']}

\\\\section{{Hill-Equation-Based AND Gate Modeling}}
{en_sections['HillModeling']}
Here, we present the formal model parameters optimized to capture this logic.

\\\\section{{In Silico Validation}}
{en_sections['InSilico']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{and_gate_heatmap_final.png}}
\\\\caption{{2D Contour heatmap demonstrating simulation output of UBE2S AND CCR6 logical AND gate, with rescaled expression and tumor/normal sample overlays.}}
\\\\label{{fig:heatmap}}
\\\\end{{figure}}

{make_latex_table(t6_headers, t6_data, "AND Gate Simulation Performance Summary in Discovery Cohort", "tab:and_perf", span_columns=False)}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{roc_curves.png}}
\\\\caption{{ROC curves comparing individual inputs (UBE2S, CCR6) against the combined logic gate output.}}
\\\\label{{fig:roc}}
\\\\end{{figure}}

{make_latex_table(t7_headers, t7_data, "External Validation Results on GSE62452 Dataset", "tab:ext_val", span_columns=True)}

\\\\section{{Robustness and Negative Controls}}
{en_sections['Robustness']}

\\\\section{{Limitations}}
\\\\begin{{enumerate}}
\"\"\"
    limitations_list = [
        "This is an in silico proof-of-concept; biochemical kinetics may differ.",
        "SHAP-inferred thresholds are statistical inflection points and do not map directly to biochemical dissociation constants.",
        "Bulk RNA-seq data reflects average cell populations and is highly influenced by stromal density and immune infiltration.",
        "The comparison between TCGA (tumor) and GTEx (normal) may contain subtle batch effects despite TOIL harmonization.",
        "External validation cohort demonstrated extremely low sensitivity (4.3%), indicating significant challenge in threshold transfer.",
        "The selected candidate pair (UBE2S + CCR6) is not strictly statistically orthogonal, exhibiting a correlation of 0.714.",
        "Transcriptomic abundance differences do not guarantee equivalent sensor accessibility or protein translation.",
        "The final candidates require promoter engineering or RNA sensor design, which introduces additional complexity.",
        "Any diagnostic or therapeutic application requires extensive wet-lab validation and safety testing in model organisms."
    ]
    for lim in limitations_list:
        content += f"\\\\item {lim}\\n"
        
    supp_prefix = "\\\\newpage\\n\\\\onecolumn\\n" if is_revised else "\\\\newpage\\n"
    
    content += f\"\"\"\\\\end{{enumerate}}

\\\\section{{Proposed Wet-Lab Validation}}
{en_sections['WetLab']}

\\\\section{{Conclusion}}
{en_sections['Conclusion']}

\\\\newpage
\\\\printbibliography[title={{References}}]

{supp_prefix}\\\\section{{Supplementary Tables and Figures}}
{en_sections['Supplementary']}

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

def generate_latex_zh(is_revised=False):
    filename = "pdac_biosensor_report_zh_revised.tex" if is_revised else "pdac_biosensor_report_zh.tex"
    filepath = os.path.join(LATEX_DIR, "zh", filename)
    
    zh_sections_esc = {k: (escape_text_for_latex(v) if isinstance(v, str) else v) for k, v in globals()['zh_sections'].items()}
    zh_sections = zh_sections_esc

    def make_latex_table(headers, data, caption, label, spec=None, span_columns=False):
        actual_span = span_columns and is_revised
        if spec is None:
            spec = "l" + "c"*(len(headers)-1)
        env = "table*" if actual_span else "table"
        pos = "[t]" if actual_span else "[H]"
        latex = f"\\\\begin{{{env}}}{pos}\\n\\\\centering\\n"
        latex += f"\\\\caption{{{caption}}}\\\\label{{{label}}}\\n"
        latex += f"\\\\begin{{tabular}}{{{spec}}}\\n\\\\toprule\\n"
        escaped_headers = [h.replace("%", "\\\\%").replace("_", "\\\\_") for h in headers]
        latex += " & ".join([f"\\\\textbf{{{h}}}" for h in escaped_headers]) + " \\\\\n\\\\midrule\\n"
        for row in data:
            escaped_row = [str(x).replace("%", "\\\\%").replace("_", "\\\\_").replace("&", "\\\\&").replace("+-", "$\\\\pm$") for x in row]
            latex += " & ".join(escaped_row) + " \\\\\n"
        latex += f"\\\\bottomrule\\n\\\\end{{tabular}}\\n\\\\end{{{env}}}\\n"
        return latex

    doc_class = "\\\\documentclass[10pt, a4paper, twocolumn]{article}" if is_revised else "\\\\documentclass[12pt, a4paper]{article}"
    style_file = "report_style_revised.tex" if is_revised else "report_style.tex"
    fig_width = "0.95\\\\linewidth" if is_revised else "0.7\\\\textwidth"

    if is_revised:
        title_block = f\"\"\"
\\\\twocolumn[
  \\\\begin{{@twocolumnfalse}}
    \\\\maketitle
    \\\\begin{{abstract}}
      {zh_sections['Abstract']}
    \\\\end{{abstract}}
    \\\\vspace{{1.5em}}
  \\\\end{{@twocolumnfalse}}
]
\"\"\"
    else:
        title_block = f\"\"\"
\\\\maketitle
\\\\newpage

\\\\begin{{abstract}}
{zh_sections['Abstract']}
\\\\end{{abstract}}
\\\\newpage
\"\"\"

    content = f\"\"\"% Auto-generated Chinese report for PDAC Biosensor Project
{doc_class}

\\\\input{{../shared/{style_file}}}
\\\\input{{../shared/macros.tex}}
\\\\usepackage{{xeCJK}}
\\\\setCJKmainfont{{DFKai-SB}}
\\\\setCJKsansfont{{DFKai-SB}}

\\\\setmainfont{{Times New Roman}}
\\\\setsansfont{{Arial}}
\\\\setmonofont{{Courier New}}

\\\\usepackage[style=apa,backend=biber]{{biblatex}}
\\\\addbibresource{{references_zh.bib}}

\\\\title{{\\\\Large \\\\bfseries {zh_sections['Title']} \\\\\\\\ \\\\vspace{{0.5em}} \\\\large {zh_sections['Subtitle']}}}
\\\\author{{{zh_sections['Author']}}}
\\\\affil{{{zh_sections['Affiliation']}}}
\\\\date{{{zh_sections['Date']}}}

\\\\begin{{document}}

{title_block}
\\\\tableofcontents
\\\\newpage

\\\\section{{前言}}
{zh_sections['Introduction']}

\\\\section{{科學背景與未滿足之臨床需求}}
{zh_sections['Rationale']}

\\\\section{{資料來源}}
{zh_sections['DataSources']}

{make_latex_table(t1_headers, t1_data, "數據世代與樣本量分布", "tab:datasets_zh", span_columns=False)}

\\\\section{{運算分析管線}}
{zh_sections['Pipeline']}

\\\\section{{品質控制與批次效應評估}}
{zh_sections['QC']}

\\\\section{{差異表現分析}}
{zh_sections['DE']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{volcano_discovery.png}}
\\\\caption{{發現世代中的火山圖，標記顯著差異表現基因。其中 UBE2S 與 CCR6 被註記為顯著上調之候選基因。}}
\\\\label{{fig:volcano_zh}}
\\\\end{{figure}}

{make_latex_table(t2_headers, t2_data, "前 10 個差異表現基因 (按特異性得分排序)", "tab:top_de_zh", span_columns=True)}

\\\\section{{機器學習分類器表現}}
{zh_sections['ML']}

{make_latex_table(t3_headers, t3_data, "機器學習分類器表現與五折交叉驗證結果摘要", "tab:ml_perf_zh", span_columns=True)}

\\\\section{{基於 SHAP 的可解釋型人工智慧分析}}
{zh_sections['SHAP']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{shap_summary.png}}
\\\\caption{{SHAP 摘要圖，顯示推動 L1 邏輯斯迴歸分類器決策的前 15 個特徵重要性排名。}}
\\\\label{{fig:shap_summary_zh}}
\\\\end{{figure}}

{make_latex_table(t4_headers, t4_data, "前 10 個 SHAP 特徵重要性與模型推估表達閾值", "tab:shap_thresh_zh", span_columns=True)}

\\\\section{{候選基因組合篩選}}
{zh_sections['PairSelection']}

{make_latex_table(t5_headers, t5_data, "選定候選基因組合的詳細分子譜描述", "tab:candidate_pair_zh", span_columns=True)}

\\\\section{{正交性評估}}
{zh_sections['Orthogonality']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{gene_pair_scatter_final.png}}
\\\\caption{{UBE2S 與 CCR6 在發現世代中的表達量散佈圖，呈現決策邊界與樣本分布象限。}}
\\\\label{{fig:scatter_zh}}
\\\\end{{figure}}

\\\\section{{單細胞與空間轉錄體驗證之必要性}}
{zh_sections['SingleCell']}

\\\\section{{基於希爾方程式的 AND gate 建模}}
{zh_sections['HillModeling']}

\\\\section{{電腦模擬驗證}}
{zh_sections['InSilico']}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{and_gate_heatmap_final.png}}
\\\\caption{{UBE2S 與 CCR6 及閘模擬輸出之二維等高線熱圖，並疊加腫瘤與健康樣本。}}
\\\\label{{fig:heatmap_zh}}
\\\\end{{figure}}

{make_latex_table(t6_headers, t6_data, "及閘模擬在發現世代中的分類效能指標摘要", "tab:and_perf_zh", span_columns=False)}

\\\\begin{{figure}}[H]
\\\\centering
\\\\includegraphics[width={fig_width}]{{roc_curves.png}}
\\\\caption{{比較單一基因輸入 (UBE2S, CCR6) 與雙輸入邏輯及閘輸出的 ROC 曲線。}}
\\\\label{{fig:roc_zh}}
\\\\end{{figure}}

{make_latex_table(t7_headers, t7_data, "GSE62452 外部驗證結果摘要", "tab:ext_val_zh", span_columns=True)}

\\\\section{{穩健性分析與負控制}}
{zh_sections['Robustness']}

\\\\section{{研究限制}}
\\\\begin{{enumerate}}
\"\"\"
    limitations_list_zh = [
        "本研究僅為電腦模擬之概念驗證，實際生化反應之動力學可能有所不同。",
        "SHAP 推估之表達閾值為統計學之拐點，無法直接對應至物理學上的生化解離常數。",
        "組織轉錄體 (Bulk RNA-seq) 表達數據易受到細胞組成、腫瘤純度及免疫細胞浸潤之干擾。",
        "儘管經過 TOIL 管線標準化，TCGA (腫瘤) 與 GTEx (健康) 的比較可能仍存在部分批次效應。",
        "外部驗證世代中顯示極低的敏感度 (4.3%)，顯示跨平台定量尺度的不匹配是閾值轉移的重大挑戰。",
        "選定的候選基因對 (UBE2S + CCR6) 統計上並非嚴格正交，在 bulk RNA-seq 中的相關係數達 0.714。",
        "轉錄體層級之豐度差異不代表合成感測器之可及性，亦不保證有同等程度的蛋白質翻譯表現。",
        "將此候選組合轉譯為合成基因線路，仍需進行啟動子工程或 RNA 轉錄調節器設計，程序較為複雜。",
        "任何診斷或治療性之臨床應用，皆須經過細胞、動物與安全性的嚴格檢驗。"
    ]
    for lim in limitations_list_zh:
        content += f"\\\\item {lim}\\n"
        
    supp_prefix = "\\\\newpage\\n\\\\onecolumn\\n" if is_revised else "\\\\newpage\\n"

    content += f\"\"\"\\\\end{{enumerate}}

\\\\section{{後續濕實驗驗證規劃}}
{zh_sections['WetLab']}

\\\\section{{結論}}
{zh_sections['Conclusion']}

\\\\newpage
\\\\printbibliography[title={{參考文獻}}]

{supp_prefix}\\\\section{{補充表格與圖}}
{zh_sections['Supplementary']}

\\\\subsection{{補充表格 1：參數掃描結果}}
{make_latex_table(["Hill 係數 (n)", "基底洩漏量 (P_basal)", "ROC-AUC", "準確度", "敏感度", "特異度"], 
                  [[str(x[0]), str(x[1]), f"{x[2]:.4f}", f"{x[4]*100:.1f}\\\\%", f"{x[5]*100:.1f}\\\\%", f"{x[6]*100:.1f}\\\\%"] for x in and_sweep.values[:6]] if and_sweep is not None else [], 
                  "希爾方程式網格掃描參數表現結果", "tab:supp_sweep_zh", span_columns=True)}

\\\\subsection{{補充表格 2：K 參數微擾對分類效能影響之敏感度分析}}
{make_latex_table(t8_headers, t8_data, "K 參數微擾對分類效能影響之敏感度分析", "tab:supp_sensitivity_zh", span_columns=True)}

\\\\subsection{{補充圖}}
\\\\begin{{figure}}[H]
\\\\centering
\\\\begin{{subfigure}}[b]{{0.48\\\\textwidth}}
\\\\centering
\\\\includegraphics[width=\\\\textwidth]{{shap_dependence_top_genes/UBE2S_shap_dependence.png}}
\\\\caption{{UBE2S SHAP 依賴性}}
\\\\end{{subfigure}}
\\\\hfill
\\\\begin{{subfigure}}[b]{{0.48\\\\textwidth}}
\\\\centering
\\\\includegraphics[width=\\\\textwidth]{{shap_dependence_top_genes/CCR6_shap_dependence.png}}
\\\\caption{{CCR6 SHAP 依賴性}}
\\\\end{{subfigure}}
\\\\caption{{選定候選基因 UBE2S 與 CCR6 之 SHAP 依賴圖，呈現出拐點轉換閾值。}}
\\\\label{{fig:supp_shap_dependence_zh}}
\\\\end{{figure}}

\\\\end{{document}}
\"\"\"
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Generated {filepath}")

def add_word_paragraph(doc, text, style='Normal', space_after=6, line_spacing=1.5, bold=False, italic=False, font_name='Times New Roman', font_size=12, is_chinese=False):
    text = clean_math_for_word(text)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = font_name
    run.font.size = Pt(font_size)
    if is_chinese:
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    return p

def add_word_heading(doc, text, level, is_chinese=False):
    text = clean_math_for_word(text)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    
    font_size = 18 if level == 1 else (14 if level == 2 else 12)
    run = p.add_run(text)
    run.bold = True
    run.font.name = 'Arial' if not is_chinese else 'DFKai-SB'
    run.font.size = Pt(font_size)
    if is_chinese:
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    return p

def add_word_table(doc, headers, data, is_chinese=False):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Shading Accent 1'
    
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        title_clean = clean_math_for_word(title)
        hdr_cells[i].text = title_clean
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.name = 'Arial' if not is_chinese else 'DFKai-SB'
        run.font.size = Pt(10)
        if is_chinese:
            run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
            
    for row in data:
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            val_clean = clean_math_for_word(val)
            row_cells[i].text = str(val_clean)
            p = row_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            if p.runs:
                run = p.runs[0]
                run.font.name = 'Times New Roman' if not is_chinese else 'DFKai-SB'
                run.font.size = Pt(10)
                if is_chinese:
                    run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
                    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table

def add_word_image(doc, filepath, caption, is_chinese=False, width=Inches(5.0)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    if os.path.exists(filepath):
        p.add_run().add_picture(filepath, width=width)
    else:
        r = p.add_run(f"[Image placeholder: {filepath}]")
        r.italic = True
        
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(12)
    run_cap = p_cap.add_run(f"Figure: {clean_math_for_word(caption)}")
    run_cap.italic = True
    run_cap.font.name = 'Times New Roman' if not is_chinese else 'DFKai-SB'
    run_cap.font.size = Pt(10)
    if is_chinese:
        run_cap._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')

def set_section_columns(section, num_cols, col_space=None):
    sectPr = section._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    cols.set(qn('w:num'), str(num_cols))
    if num_cols > 1:
        cols.set(qn('w:equalWidth'), '1')
        if col_space is not None:
            cols.set(qn('w:space'), str(col_space))

def generate_word_en(is_revised=False):
    filename = "pdac_biosensor_report_en_revised.docx" if is_revised else "pdac_biosensor_report_en.docx"
    filepath = os.path.join(WORD_DIR, "en", filename)
    doc = docx.Document()
    
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.98)
    sec1.bottom_margin = Inches(0.98)
    sec1.left_margin = Inches(0.98)
    sec1.right_margin = Inches(0.98)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(80)
    p_title.paragraph_format.space_after = Pt(18)
    run_title = p_title.add_run(clean_math_for_word(en_sections["Title"]))
    run_title.bold = True
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(20)
    
    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_after = Pt(6)
    run_author = p_author.add_run(clean_math_for_word(en_sections["Author"]))
    run_author.font.name = 'Times New Roman'
    run_author.font.size = Pt(12)
    
    p_aff = doc.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_after = Pt(18)
    run_aff = p_aff.add_run(clean_math_for_word(en_sections["Affiliation"]))
    run_aff.font.name = 'Times New Roman'
    run_aff.font.size = Pt(10)
    
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_date = p_date.add_run(clean_math_for_word(en_sections["Date"]))
    run_date.font.name = 'Times New Roman'
    run_date.font.size = Pt(11)
    
    doc.add_page_break()
    
    add_word_heading(doc, "Abstract", 1)
    add_word_paragraph(doc, en_sections["Abstract"])
    
    if is_revised:
        sec2 = doc.add_section(start_type=WD_SECTION.NEW_PAGE)
        set_section_columns(sec2, 2, col_space=720)
        sec2.top_margin = Inches(0.7)
        sec2.bottom_margin = Inches(0.7)
        sec2.left_margin = Inches(0.7)
        sec2.right_margin = Inches(0.7)
        main_fig_width = Inches(3.0)
    else:
        doc.add_page_break()
        main_fig_width = Inches(5.0)
        
    sections_order = [
        ("1. Introduction", en_sections["Introduction"]),
        ("2. Scientific Rationale and Unmet Need", en_sections["Rationale"]),
        ("3. Data Sources", en_sections["DataSources"]),
        ("4. Computational Pipeline", en_sections["Pipeline"]),
        ("5. Quality Control and Batch-Effect Assessment", en_sections["QC"]),
        ("6. Differential Expression Analysis", en_sections["DE"]),
        ("7. Machine Learning Classifier Performance", en_sections["ML"]),
        ("8. SHAP-Based Explainable AI Analysis", en_sections["SHAP"]),
        ("9. Candidate Gene Pair Selection", en_sections["PairSelection"]),
        ("10. Orthogonality Assessment", en_sections["Orthogonality"]),
        ("11. Need for Single-Cell and Spatial Validation", en_sections["SingleCell"]),
        ("12. Hill-Equation-Based AND Gate Modeling", en_sections["HillModeling"]),
        ("13. In Silico Validation", en_sections["InSilico"]),
        ("14. Robustness and Controls", en_sections["Robustness"])
    ]
    
    for title, text in sections_order:
        add_word_heading(doc, title, 1)
        add_word_paragraph(doc, text)
        
        if "3. Data Sources" in title:
            add_word_table(doc, t1_headers, t1_data)
        elif "6. Differential Expression" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "volcano_discovery.png"), "Volcano plot of discovery cohort", width=main_fig_width)
            add_word_table(doc, t2_headers, t2_data)
        elif "7. Machine Learning" in title:
            add_word_table(doc, t3_headers, t3_data)
        elif "8. SHAP-Based" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "shap_summary.png"), "SHAP Feature Importance Summary Bar Plot", width=main_fig_width)
            add_word_table(doc, t4_headers, t4_data)
        elif "9. Candidate Gene" in title:
            add_word_table(doc, t5_headers, t5_data)
        elif "10. Orthogonality" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "gene_pair_scatter_final.png"), "UBE2S vs CCR6 rescaled expression scatter plot", width=main_fig_width)
        elif "13. In Silico Validation" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "and_gate_heatmap_final.png"), "AND gate logical activation surface heatmap", width=main_fig_width)
            add_word_table(doc, t6_headers, t6_data)
            add_word_image(doc, os.path.join(FIGURES_DIR, "roc_curves.png"), "ROC curves comparison: single vs logical combination", width=main_fig_width)
            add_word_heading(doc, "Table 7: External Validation Results (GSE62452)", 2)
            add_word_table(doc, t7_headers, t7_data)
            
    add_word_heading(doc, "15. Limitations", 1)
    limitations_list = [
        "This is an in silico proof-of-concept; biochemical kinetics may differ.",
        "SHAP-inferred thresholds are statistical inflection points and do not map directly to biochemical dissociation constants.",
        "Bulk RNA-seq data reflects average cell populations and is highly influenced by stromal density and immune infiltration.",
        "The comparison between TCGA (tumor) and GTEx (normal) may contain subtle batch effects despite TOIL harmonization.",
        "External validation cohort demonstrated extremely low sensitivity (4.3%), indicating significant challenge in threshold transfer.",
        "The selected candidate pair (UBE2S + CCR6) is not strictly statistically orthogonal, exhibiting a correlation of 0.714.",
        "Transcriptomic abundance differences do not guarantee equivalent sensor accessibility or protein translation.",
        "The final candidates require promoter engineering or RNA sensor design, which introduces additional complexity.",
        "Any diagnostic or therapeutic application requires extensive wet-lab validation and safety testing in model organisms."
    ]
    for lim in limitations_list:
        add_word_paragraph(doc, f"- {lim}", space_after=4)
        
    add_word_heading(doc, "16. Proposed Wet-Lab Validation", 1)
    add_word_paragraph(doc, en_sections["WetLab"])
    
    add_word_heading(doc, "17. Conclusion", 1)
    add_word_paragraph(doc, en_sections["Conclusion"])
    
    add_word_heading(doc, "18. References", 1)
    refs = en_sections["References"].split("\\n")
    for ref in refs:
        add_word_paragraph(doc, ref, space_after=4)
        
    if is_revised:
        sec3 = doc.add_section(start_type=WD_SECTION.NEW_PAGE)
        set_section_columns(sec3, 1)
        sec3.top_margin = Inches(0.98)
        sec3.bottom_margin = Inches(0.98)
        sec3.left_margin = Inches(0.98)
        sec3.right_margin = Inches(0.98)
    else:
        doc.add_page_break()
        
    add_word_heading(doc, "19. Supplementary Tables and Figures", 1)
    add_word_paragraph(doc, en_sections["Supplementary"])
    
    add_word_heading(doc, "Supplementary Table 1: Grid Search Sweep", 2)
    add_word_table(doc, ["Hill Coefficient (n)", "Basal Leakiness (P_basal)", "ROC-AUC", "Accuracy", "Sensitivity", "Specificity"],
                   [[str(x[0]), str(x[1]), f"{x[2]:.4f}", f"{x[4]*100:.1f}%", f"{x[5]*100:.1f}%", f"{x[6]*100:.1f}%"] for x in and_sweep.values[:6]] if and_sweep is not None else [])
    
    add_word_heading(doc, "Supplementary Table 2: Sensitivity analysis", 2)
    add_word_table(doc, t8_headers, t8_data)
    
    add_word_heading(doc, "Supplementary Figures: SHAP dependence plots", 2)
    add_word_image(doc, os.path.join(FIGURES_DIR, "shap_dependence_top_genes/UBE2S_shap_dependence.png"), "UBE2S SHAP dependence plot", width=Inches(4.5))
    add_word_image(doc, os.path.join(FIGURES_DIR, "shap_dependence_top_genes/CCR6_shap_dependence.png"), "CCR6 SHAP dependence plot", width=Inches(4.5))
    
    doc.save(filepath)
    print(f"Generated {filepath}")

def generate_word_zh(is_revised=False):
    filename = "pdac_biosensor_report_zh_revised.docx" if is_revised else "pdac_biosensor_report_zh.docx"
    filepath = os.path.join(WORD_DIR, "zh", filename)
    doc = docx.Document()
    
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.98)
    sec1.bottom_margin = Inches(0.98)
    sec1.left_margin = Inches(0.98)
    sec1.right_margin = Inches(0.98)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(80)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run(clean_math_for_word(zh_sections["Title"]))
    run_title.bold = True
    run_title.font.name = 'DFKai-SB'
    run_title.font.size = Pt(20)
    run_title._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run(clean_math_for_word(zh_sections["Subtitle"]))
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(12)
    
    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_after = Pt(6)
    run_author = p_author.add_run(clean_math_for_word(zh_sections["Author"]))
    run_author.font.name = 'DFKai-SB'
    run_author.font.size = Pt(12)
    run_author._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    
    p_aff = doc.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_after = Pt(18)
    run_aff = p_aff.add_run(clean_math_for_word(zh_sections["Affiliation"]))
    run_aff.font.name = 'DFKai-SB'
    run_aff.font.size = Pt(10)
    run_aff._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_date = p_date.add_run(clean_math_for_word(zh_sections["Date"]))
    run_date.font.name = 'DFKai-SB'
    run_date.font.size = Pt(11)
    run_date._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'DFKai-SB')
    
    doc.add_page_break()
    
    add_word_heading(doc, "摘要", 1, is_chinese=True)
    add_word_paragraph(doc, zh_sections["Abstract"], is_chinese=True, font_name='DFKai-SB')
    
    if is_revised:
        sec2 = doc.add_section(start_type=WD_SECTION.NEW_PAGE)
        set_section_columns(sec2, 2, col_space=720)
        sec2.top_margin = Inches(0.7)
        sec2.bottom_margin = Inches(0.7)
        sec2.left_margin = Inches(0.7)
        sec2.right_margin = Inches(0.7)
        main_fig_width = Inches(3.0)
    else:
        doc.add_page_break()
        main_fig_width = Inches(5.0)
        
    sections_order_zh = [
        ("一、前言", zh_sections["Introduction"]),
        ("二、科學背景與未滿足之臨床需求", zh_sections["Rationale"]),
        ("三、資料來源", zh_sections["DataSources"]),
        ("四、運算分析管線", zh_sections["Pipeline"]),
        ("五、品質控制與批次效應評估", zh_sections["QC"]),
        ("六、差異表現分析", zh_sections["DE"]),
        ("七、機器學習分類器表現", zh_sections["ML"]),
        ("八、基於 SHAP 的可解釋型人工智慧分析", zh_sections["SHAP"]),
        ("九、候選基因組合篩選", zh_sections["PairSelection"]),
        ("十、正交性評估", zh_sections["Orthogonality"]),
        ("十一、單細胞與空間轉錄體驗證之必要性", zh_sections["SingleCell"]),
        ("十二、基於希爾方程式的 AND gate 建模", zh_sections["HillModeling"]),
        ("十三、電腦模擬驗證", zh_sections["InSilico"]),
        ("十四、穩健性分析與負控制", zh_sections["Robustness"])
    ]
    
    for title, text in sections_order_zh:
        add_word_heading(doc, title, 1, is_chinese=True)
        add_word_paragraph(doc, text, is_chinese=True, font_name='DFKai-SB')
        
        if "三、資料來源" in title:
            add_word_table(doc, t1_headers, t1_data, is_chinese=True)
        elif "六、差異表現分析" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "volcano_discovery.png"), "發現世代之火山圖", is_chinese=True, width=main_fig_width)
            add_word_table(doc, t2_headers, t2_data, is_chinese=True)
        elif "七、機器學習" in title:
            add_word_table(doc, t3_headers, t3_data, is_chinese=True)
        elif "八、基於 SHAP" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "shap_summary.png"), "SHAP 特徵重要性摘要條形圖", is_chinese=True, width=main_fig_width)
            add_word_table(doc, t4_headers, t4_data, is_chinese=True)
        elif "九、候選基因" in title:
            add_word_table(doc, t5_headers, t5_data, is_chinese=True)
        elif "十、正交性評估" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "gene_pair_scatter_final.png"), "UBE2S 與 CCR6 表達量散佈圖", is_chinese=True, width=main_fig_width)
        elif "十三、電腦模擬驗證" in title:
            add_word_image(doc, os.path.join(FIGURES_DIR, "and_gate_heatmap_final.png"), "邏輯及閘活化熱圖", is_chinese=True, width=main_fig_width)
            add_word_table(doc, t6_headers, t6_data, is_chinese=True)
            add_word_image(doc, os.path.join(FIGURES_DIR, "roc_curves.png"), "ROC 曲線比較圖", is_chinese=True, width=main_fig_width)
            add_word_heading(doc, "表格 7：外部驗證結果 (GSE62452)", 2, is_chinese=True)
            add_word_table(doc, t7_headers, t7_data, is_chinese=True)
            
    add_word_heading(doc, "十五、研究限制", 1, is_chinese=True)
    limitations_list_zh = [
        "本研究僅為電腦模擬之概念驗證，實際生化反應之動力學可能有所不同。",
        "SHAP 推估之表達閾值為統計學之拐點，無法直接對應至物理學上的生化解離常數。",
        "組織轉錄體 (Bulk RNA-seq) 表達數據易受到細胞組成、腫瘤純度及免疫細胞浸潤之干擾。",
        "儘管經過 TOIL 管線標準化，TCGA (腫瘤) 與 GTEx (健康) 的比較可能仍存在部分批次效應。",
        "外部驗證世代中顯示極低的敏感度 (4.3%)，顯示跨平台定量尺度的不匹配是閾值轉移的重大挑戰。",
        "選定的候選基因對 (UBE2S + CCR6) 統計上並非嚴格正交，在 bulk RNA-seq 中的相關係數達 0.714。",
        "轉錄體層級之豐度差異不代表合成感測器之可及性，亦不保證有同等程度的蛋白質翻譯表現。",
        "將此候選組合轉譯為合成基因線路，仍需進行啟動子工程或 RNA 轉錄調節器設計，程序較為複雜。",
        "任何診斷或治療性之臨床應用，皆須經過細胞、動物與安全性的嚴格檢驗。"
    ]
    for lim in limitations_list_zh:
        add_word_paragraph(doc, f"- {lim}", is_chinese=True, font_name='DFKai-SB', space_after=4)
        
    add_word_heading(doc, "十六、後續濕實驗驗證規劃", 1, is_chinese=True)
    add_word_paragraph(doc, zh_sections["WetLab"], is_chinese=True, font_name='DFKai-SB')
    
    add_word_heading(doc, "十七、結論", 1, is_chinese=True)
    add_word_paragraph(doc, zh_sections["Conclusion"], is_chinese=True, font_name='DFKai-SB')
    
    add_word_heading(doc, "十八、參考文獻", 1, is_chinese=True)
    refs = zh_sections["References"].split("\\n")
    for ref in refs:
        add_word_paragraph(doc, ref, is_chinese=True, font_name='DFKai-SB', space_after=4)
        
    if is_revised:
        sec3 = doc.add_section(start_type=WD_SECTION.NEW_PAGE)
        set_section_columns(sec3, 1)
        sec3.top_margin = Inches(0.98)
        sec3.bottom_margin = Inches(0.98)
        sec3.left_margin = Inches(0.98)
        sec3.right_margin = Inches(0.98)
    else:
        doc.add_page_break()
        
    add_word_heading(doc, "十九、補充表格與圖", 1, is_chinese=True)
    add_word_paragraph(doc, zh_sections["Supplementary"], is_chinese=True, font_name='DFKai-SB')
    
    add_word_heading(doc, "補充表格 1：希爾方程式網格掃描參數表現結果", 2, is_chinese=True)
    add_word_table(doc, ["Hill 係數 (n)", "基底洩漏量 (P_basal)", "ROC-AUC", "準確度", "敏感度", "特異度"],
                   [[str(x[0]), str(x[1]), f"{x[2]:.4f}", f"{x[4]*100:.1f}%", f"{x[5]*100:.1f}%", f"{x[6]*100:.1f}%"] for x in and_sweep.values[:6]] if and_sweep is not None else [], is_chinese=True)
    
    add_word_heading(doc, "補充表格 2：K 參數微擾對分類效能影響之敏感度分析", 2, is_chinese=True)
    add_word_table(doc, t8_headers, t8_data, is_chinese=True)
    
    add_word_heading(doc, "補充圖：SHAP 依賴圖", 2, is_chinese=True)
    add_word_image(doc, os.path.join(FIGURES_DIR, "shap_dependence_top_genes/UBE2S_shap_dependence.png"), "UBE2S SHAP 依賴圖", is_chinese=True, width=Inches(4.5))
    add_word_image(doc, os.path.join(FIGURES_DIR, "shap_dependence_top_genes/CCR6_shap_dependence.png"), "CCR6 SHAP 依賴圖", is_chinese=True, width=Inches(4.5))
    
    doc.save(filepath)
    print(f"Generated {filepath}")

import shutil
import time

def make_backup(path):
    if os.path.exists(path):
        ts = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{ts}"
        shutil.copy2(path, backup_path)
        print(f"Created backup of {path} at {backup_path}")

def main():
    original_files = [
        os.path.join(LATEX_DIR, "en", "pdac_biosensor_report_en.tex"),
        os.path.join(LATEX_DIR, "zh", "pdac_biosensor_report_zh.tex"),
        os.path.join(WORD_DIR, "en", "pdac_biosensor_report_en.docx"),
        os.path.join(WORD_DIR, "zh", "pdac_biosensor_report_zh.docx")
    ]
    for path in original_files:
        make_backup(path)
        
    print("Writing English LaTeX files...")
    generate_latex_en(is_revised=False)
    generate_latex_en(is_revised=True)
    
    print("Writing Chinese LaTeX files...")
    generate_latex_zh(is_revised=False)
    generate_latex_zh(is_revised=True)
    
    print("Writing English Word documents...")
    generate_word_en(is_revised=False)
    generate_word_en(is_revised=True)
    
    print("Writing Chinese Word documents...")
    generate_word_zh(is_revised=False)
    generate_word_zh(is_revised=True)
    
    print("\\nAll files written successfully!")

if __name__ == "__main__":
    main()
"""
    
    # 5. Write the combined code
    patched_content = "\\n".join(header_lines) + appended_code
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(patched_content)
        
    print("Writing completed!")

if __name__ == '__main__':
    main()
