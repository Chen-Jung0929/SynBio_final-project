# SynBio Project Roadmap & Future Directions

這份文件旨在記錄本合成生物學期末專題後續的規畫與待辦事項，方便所有組員了解目前的進度與未來的實驗/分析方向。

## 📍 目前專案狀態 (Current Status)
- [x] **第二代 (v2) 管線建置**：完成差異表達分析、同世代過濾、機器學習共識排序。
- [x] **核心結果確立**：已選定 **CEACAM5 + CST1** 作為最佳的 AND-gate 生物感測器候選基因對。
- [x] **運算驗證完成**：在發現世代、同世代驗證 (GSE62452) 與獨立外部驗證 (GSE28735) 中均取得穩健的 AUC 表現。
- [x] **單細胞轉錄體驗證**：已利用 GSE154778 確認 CEACAM5 與 CST1 於惡性導管上皮細胞中高度特異性共表達，且在正常細胞中表現為絕對零 (0.0%)。
- [x] **專案重構與同步**：所有 v1 舊資料已封存至 `src_v1_archive/`，目前以 `analysis_v2/` 與 `scrna_validation/` 為核心架構。

---

## 🚀 未來規劃與實驗方向 (Future Directions)

本專案的計算生物學 (Computational Biology) 階段已經告一段落，接下來將進入**合成生物學線路設計與濕實驗驗證 (Wet-lab Validation)** 階段。請各組員參考以下方向進行分工與推進：

### 1. 合成生物學基因線路設計 (Circuit Design)
* **合成啟動子系統 (Synthetic Promoter Systems)**：嘗試將 CEACAM5 與 CST1 的上游調控區段分別克隆至驅動正交轉錄因子 (Orthogonal TFs) 的載體中，以 split-transactivator 架構實現轉錄層級的 AND 閘邏輯。
* **SynNotch 受體線路 (Synthetic Notch Receptors)**：評估藉由細胞表面對腫瘤相關配體的辨識，觸發細胞內部客製化轉錄因子釋放的可行性。
* **RNA 感測器設計 (RNA-based Sensors)**：探索使用 Toehold switches 或 Ribocomputing devices，直接偵測目標基因的內源性 mRNA 濃度，以避開複雜的啟動子工程。

### 2. 體外功能性驗證 (In Vitro Validation)
* **細胞株選擇**：
  * **陽性對照組**：胰臟癌細胞株 (例如：PANC-1, MIA PaCa-2)。
  * **陰性對照組**：人類正常胰管上皮細胞 (HPDE)。
* **測試項目**：進行劑量反應特性分析 (Dose-response characterization)，確保線路在目標癌細胞能精準啟動，而在正常細胞中保持關閉。

### 3. 中長期規劃 (Mid-to-Long Term Goals)
* **體內驗證 (In Vivo Validation)**：在患者來源異種移植 (PDX) 小鼠模型中進行體內驗證，確認感測器在複雜腫瘤微環境中的專一性。
* **穩定性評估**：評估基因電路在腫瘤代謝壓力 (如缺氧、低營養) 下的穩定性。
* **多輸入邏輯閘 (Multi-input Logic Gates)**：探索加入第三個輸入條件 (如 NOT gate 排除特定免疫細胞) 以進一步提升腫瘤特異度與降低脫靶風險。

---

## 📝 協作與討論 (Collaboration)
請各組員在有新進展時，於此文件下方新增紀錄，或是在 GitHub 提出 Issue 進行具體討論。
