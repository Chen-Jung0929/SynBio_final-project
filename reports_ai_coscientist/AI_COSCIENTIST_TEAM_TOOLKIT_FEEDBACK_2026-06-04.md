# AI Co-Scientist Team Toolkit 使用回饋

Date: 2026-06-04  
Project: SynBio Final Project / PDAC logic-gated biosensor discovery  
Toolkit reviewed: `C:\AI_CoScientist_Team_Toolkit`

## Executive Summary

這次在 SynBio final project 中，`AI_CoScientist_Team_Toolkit` 最有價值的地方不是單純產生更多想法，而是把專案從「漂亮候選結果」推向「可審核、可反駁、可交接」的科學流程。它協助我們識別 v3/v4/v5 中的核心風險：外部驗證 leakage、single-cell circularity、bulk-first pipeline 的 cell-level failure mode、以及資料缺失時不可用模擬結果補洞。

與 Antigravity 的協作也顯示，多代理研究團隊的正確分工應該是：

```text
Antigravity = pipeline execution / rapid implementation
Codex + AI Co-Scientist = scientific audit / claim discipline / validation gates
```

這個分工非常有效，但目前 toolkit 還缺少正式的 multi-agent handoff、append-only event log、claim-evidence ledger、以及 dirty-worktree / concurrent-edit protection。這些不是小 UX 問題，而是會直接影響科學結論可信度的基礎設施。

## What Worked Well

### 1. Project/toolkit boundary 設計正確

`README.md` 和 `DO_NOT_STORE_PROJECT_CONTEXT_HERE.md` 明確規定不要把 project-specific context 寫進 toolkit，而要寫到 target project 的 `.ai_scientist/` 或 repo 文件中。這是非常重要的設計，因為研究記憶、假設、樣本資訊、pipeline 狀態都應該跟專案版本一起走，而不是污染 reusable framework。

本次實際上也遵守了這個原則：SynBio 專案的 review、audit、handoff、report 都放在 `C:\合成生物學期末專題` 內，並同步到 GitHub。

### 2. Biomedical research board 的價值很高

`biomedical_research_board` 對這個專題的幫助主要體現在 claim discipline 和 validation logic，而不是產生更多候選基因。它讓我們反覆回到這幾個問題：

- 目前證據支持的是 computational prioritization，還是 biological causality？
- AUC / sensitivity / specificity 是否來自 true locked validation？
- scRNA-seq validation 是否有 circular marker leakage？
- pair selection 是否穩定，還是依賴 top-N search space？
- threshold 是 model-derived decision boundary，還是被誤講成 biochemical Kd？

這些問題直接改善了 v3/v4/v5 的科學敘事。

### 3. Security auditor 有實際效益

`security_auditor` 對專案有幾個具體貢獻：

- 強化 `.gitignore`，避免 credential/token/raw-data 類型檔案被誤提交。
- 提醒 public dataset pseudonymous sample IDs 雖非直接個資，但仍應當作 research sample codes 謹慎處理。
- 對 raw gzip / large data file 進 Git 的風險有實際防護價值。

這類安全檢查對生醫專案非常重要，因為資料治理錯誤常常比模型錯誤更難補救。

### 4. Agent registry / tool registry 讓能力邊界比較清楚

`AGENT_REGISTRY.md` 和 `TOOL_INDEX.md` 對 AI agent 很有幫助。它們讓我可以先確認有哪些正式 agent / tool，而不是靠猜測呼叫不存在的能力。尤其以下分類是有價值的：

- `biomedical_research_board`
- `ml_validation_scientist`
- `evidence_synthesis_specialist`
- `security_auditor`
- `tool_dispatcher`
- `nchc_connector`
- `latex_formatter`

建議後續所有 agent 都應該維持這種「可列出、可描述、可追溯 entrypoint」的形式。

## Impact On The SynBio Project

### 1. v3 從候選敘事變成可審核 pipeline

AI Co-Scientist review 幫助我們把 v3 的主張從「找到 PDAC detector」降到更準確的：

```text
computationally prioritized candidate pair with moderate locked external validation
```

這使報告不再過度依賴 near-perfect discovery performance，而是開始重視 locked GSE28735、top-N stability、threshold uncertainty、single-cell validation。

### 2. v4 的 circularity issue 被正確揭露

Antigravity 先快速推進 V4 pipeline，最初 `OCIAD2 + CEACAM5` 看起來很漂亮。但在 Codex / AI co-scientist 的 audit framing 下，我們發現 `CEACAM5` 與 target-cell annotation 有 circularity 風險。修正 annotation 後，V4 的漂亮結果消失，改為暴露 bulk-first strategy 的 failure mode。

這是 toolkit 最值得肯定的一點：它幫助團隊接受「負結果也是科學進展」。

### 3. v5 的方向變得更合理

V5 改成 scRNA-first discovery，再 backward validate bulk cohorts。這個方向不是單純換模型，而是根據 v1-v4 的失敗模式改變科學問題定義：

```text
bulk-first classification pair
→ cell-compartment-aware AND-gate input hypothesis
```

這正是 AI 科學研究團隊應該做的事：不是永遠優化同一個指標，而是在證據顯示舊 framing 錯誤時，協助人類重新定義問題。

## Antigravity Collaboration Experience

### What Worked

Antigravity 的強項是快速實作與推進 pipeline。它能很快建立 `analysis_v4/`、`analysis_v5/`、產生候選表格、補 report generator，並在遇到資料缺失時主動尋找替代資料來源。

Codex / AI Co-Scientist 的強項則是：

- 檢查結果是否被過度解讀。
- 將「好看的結果」轉成「可驗證的 evidence chain」。
- 補上 audit table、guardrail report、claim limitation。
- 在資料缺失時要求輸出 `UNAVAILABLE_*`，而不是模擬 validation。

這個互補性非常好。若沒有 Antigravity，pipeline 可能推得太慢；若沒有 audit/gatekeeper，pipeline 可能太快變成過度宣稱。

### What Did Not Work

最大的問題是協作 protocol 不夠強：

1. **同步檔案發生 race condition**
   - `ANTIGRAVITY_CODEX_SYNC.md` 曾被多人/多代理同時編輯。
   - 有些段落被覆蓋或回復成舊敘事。
   - 後來才改成 append-only，但這應該由 toolkit 原生提供。

2. **缺少 active-owner / lock 機制**
   - Antigravity 會在 Codex 正在讀或修改檔案時同步新版本。
   - 這導致必須頻繁重讀 `git status` / `git diff`。
   - 對研究 pipeline 來說，這可能造成 report 跟 table 版本不一致。

3. **沒有標準 handoff schema**
   - handoff 有靠人工寫清楚，但沒有強制欄位。
   - 建議 toolkit 定義固定格式：current branch、latest commit、dirty files、generated outputs、blocked tasks、next commands、claim guardrails。

4. **沒有 claim-evidence ledger**
   - 多代理會反覆寫「成功」「完成」「final」之類字眼。
   - 但沒有一張表要求每個 claim 對應到 artifact / command / validation status。

## Main Pain Points

### 1. 缺少科學 claim gate

Toolkit 應該內建一個 `claim_guardian` 或 `evidence_gatekeeper` agent，專門掃描報告中的下列語句：

- clinically validated
- final detector
- wet-lab ready
- fully resolved
- perfect biosensor
- causality
- biochemical Kd

並要求每句高風險 claim 綁定證據。

建議輸出格式：

```csv
claim,claim_type,evidence_file,evidence_status,allowed_wording,rejected_wording
```

### 2. 缺少資料缺失時的標準行為

這次一個重大 guardrail 是：缺少 bulk matrix 或 probe mapping 時，不可以模擬 validation。Toolkit 應該把這變成跨 agent 規則：

```text
missing required data → write UNAVAILABLE_* audit
never fabricate or simulate validation metrics unless explicitly labeled as simulation
simulation cannot be used as validation evidence
```

### 3. 缺少 run manifest / provenance

每次 agent run 都應該自動產生：

```text
agent_name
agent_version_or_commit
project_root
branch
start_time
end_time
input_files
output_files
commands_run
data_files_required
data_files_missing
claim_status
```

這對多代理研究非常必要，否則後續很難知道哪個表格是誰、用哪版 script、在哪個資料狀態下產生的。

### 4. 缺少 Git-aware safety

Toolkit 應該在每個 agent 修改檔案前自動檢查：

- current branch
- dirty files
- untracked outputs
- remote ahead/behind
- 是否有別的 agent lock

若偵測到 concurrent edits，應要求 append-only 或切分支，而不是直接覆蓋。

### 5. 缺少 machine-readable audit summaries

目前很多 report 是 Markdown，人讀很好，但 agent 接續時最好也有 CSV/JSON：

```text
results_*/audit/*_audit_summary.csv
```

Toolkit 應鼓勵每份 Markdown report 同時輸出 machine-readable gate table。

## Recommended Improvements

### P0: Highest priority

1. **Append-only collaboration log**
   - Toolkit should provide `collaboration_log append --agent Codex --message ...`
   - Automatic timestamp.
   - No in-place editing by default.

2. **Agent handoff schema**
   - Required fields:
     - branch
     - latest commit
     - dirty files
     - generated outputs
     - commands run
     - blockers
     - next exact commands
     - scientific claims allowed / not allowed

3. **Claim-evidence ledger**
   - Every final report claim should map to evidence.
   - High-risk biomedical claims require explicit allowed wording.

4. **Unavailable-data protocol**
   - Missing input should create an audit file, not a fabricated result.
   - This should be enforced globally by the ML / validation agents.

5. **Git dirty-worktree guard**
   - Before file edits, agent runner should show branch, ahead/behind, dirty files.
   - Optionally refuse to write if another agent lock exists.

### P1: Strongly recommended

1. **Run manifest generator**
   - Auto-write `run_manifest.json` per agent run.

2. **Evidence grading module**
   - Grade each result as:
     - discovery only
     - same-cohort validation
     - locked external validation
     - single-cell support
     - spatial support
     - wet-lab validated

3. **Report consistency checker**
   - Compare report values against CSV tables.
   - Fail if report says PASS but audit CSV says UNAVAILABLE or FAIL.

4. **Threshold profile registry**
   - Any threshold relaxation must be named and recorded.
   - Prevent silent movement from strict to relaxed criteria.

5. **Multi-agent role templates**
   - executor
   - reviewer
   - security auditor
   - claim guardian
   - data steward
   - handoff coordinator

### P2: Nice to have

1. Lightweight dashboard for current project state.
2. Local GPU worker queue integrated with project-scoped audit logs.
3. Literature synthesis adapter that outputs citation-backed evidence tables.
4. NCHC job templates that automatically include data provenance and output hashes.

## Suggested New Agents

### `claim_guardian`

Scans reports and slides for overclaims. Produces allowed/rejected wording.

### `handoff_coordinator`

Creates and validates structured handoff notes between Codex, Antigravity, and other agents.

### `provenance_recorder`

Writes run manifests and output inventories.

### `report_consistency_checker`

Checks whether Markdown reports match CSV/JSON outputs.

### `data_availability_auditor`

Checks required datasets before a run and writes `AVAILABLE`, `MISSING`, or `UNAVAILABLE_MAPPING_REQUIRED`.

## Specific Feedback About Antigravity + Codex Collaboration

The collaboration was productive precisely because the two systems had different temperaments:

- Antigravity was willing to push the pipeline forward aggressively.
- Codex was skeptical, slower, and more focused on auditability.

This tension improved the science. Antigravity generated V4/V5 candidates quickly; Codex then caught overclaims, circularity risks, off-target interpretation problems, and missing-data validation hazards.

However, this setup needs stronger coordination infrastructure. Without append-only logs and branch-aware locks, the same productive tension can become file churn or inconsistent reports. The toolkit should formalize this pattern rather than relying on agents to remember etiquette.

Recommended collaboration pattern:

```text
1. Executor agent creates or updates pipeline outputs.
2. Audit agent reviews outputs and writes machine-readable gates.
3. Claim guardian rewrites report language.
4. Handoff coordinator records next steps in append-only log.
5. Git-aware guard commits only after worktree consistency checks.
```

## Bottom Line

The AI Co-Scientist Team Toolkit is already useful for real scientific work. Its biggest value in this project was not answer generation, but scientific self-correction: it helped the team accept when a candidate was weaker than expected and pivot from bulk-first to scRNA-first reasoning.

The next improvement should be infrastructure, not more personas. The toolkit needs stronger collaboration logs, evidence ledgers, run manifests, claim gates, and Git-aware safety. Those changes would make multi-agent scientific work both faster and more trustworthy.
