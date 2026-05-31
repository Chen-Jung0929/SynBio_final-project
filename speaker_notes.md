# Speaker Notes — Computational Explanation Slide Deck

## Slide 1 — Title

### 動畫目的
無動畫；建立報告主題：用 transcriptomic data 推導 logic-gated biosensor candidate。

### 講稿
今天我要報告的是一個資料驅動的 biosensor 設計流程。重點不是直接宣稱找到可用的臨床診斷工具，而是示範如何從全基因表現資料，一步一步縮小到一組候選 AND-gate inputs。整份簡報會特別強調每張結果圖是怎麼算出來的，以及它能支持和不能支持什麼結論。

### 關鍵句
This deck explains how each result figure is computed, not just what the figure looks like.

## Slide 2 — The Pancreatic Tumor Microenvironment

### 動畫目的
無動畫；介紹為什麼 PDAC 的 tumor microenvironment 需要比單一 marker 更謹慎的 targeting strategy。

### 講稿
PDAC 的困難在於腫瘤周邊有很強的纖維化和免疫抑制環境。這使得單一 marker 的治療或偵測策略容易遇到 specificity 和 toxicity 的問題。這張投影片是設定生物學問題：我們需要的是一個能整合兩個訊號的設計，而不是只看一個高表現基因。

### 關鍵句
PDAC targeting needs contextual logic, not just one highly expressed marker.

## Slide 3 — Why a Single Marker is Insufficient

### 動畫目的
無動畫；說明 single-marker strategy 的 on-target off-tumor 風險。

### 講稿
即使某個 marker 在腫瘤中表現較高，它也可能在正常組織中有低量表現。對 CAR 或 synthetic circuit 來說，只要正常細胞達到觸發門檻，就可能產生 toxicity。這就是為什麼我們後面會把問題轉成二維 AND-gate：必須同時滿足兩個條件才 ON。

### 關鍵句
Single-marker overexpression is not enough to guarantee safety.

## Slide 4 — The AND-Gate Biosensor Paradigm

### 動畫目的
用簡單二維點圖說明：單一 marker 上的重疊，可以透過兩個 input 的 AND decision boundary 變成更嚴格的 activation region。

### 講稿
這個動畫先讓大家看到樣本在一個 marker 上可能有重疊。接著把第二個 input 加進來後，每個樣本變成二維空間中的一個點。真正會被啟動的區域不是任一 marker 高，而是右上角：Input A high 且 Input B high。這是後面所有分析的設計目標。

### 關鍵句
The AND gate turns two imperfect markers into a stricter two-dimensional decision rule.

## Slide 5 — Discovery Cohort & Sample Size

### 動畫目的
無動畫；交代 input data 的來源與 discovery / external validation 的資料平台差異。

### 講稿
Discovery cohort 使用 TCGA-PAAD tumor 和 GTEx normal pancreas 的 RNA-seq 資料。這讓我們能做 genome-wide 的 gene expression comparison。外部驗證則使用 GSE62452 microarray，這很重要，因為後面 validation 變差不一定只是候選 pair 沒用，也可能反映 RNA-seq 閾值轉移到 microarray 的平台差異。

### 關鍵句
Discovery and external validation are not only different cohorts; they are different measurement platforms.

## Slide 6 — Unbiased Selection Pipeline

### 動畫目的
讓觀眾先看到整體計算邏輯：raw data 會依序進入 DE、ML、SHAP、threshold、pair scoring、Hill modeling 和 validation controls。

### 講稿
這張是整個流程的地圖。接下來每一張重要結果圖，我都會用同一個框架講：input 是什麼、計算了什麼、圖上的元素代表什麼、支持什麼結論，以及不能證明什麼。特別要注意後面三種驗證的角色不同：random-pair control 是 against chance，threshold sensitivity 是 against parameter uncertainty，external validation 是 against dataset/platform shift。

### 關鍵句
The validation modules answer different failure modes: chance, parameter uncertainty, and platform shift.

## Slide 7 — Volcano plot / DE analysis

### 動畫目的
讓觀眾理解 volcano plot 不是直接畫出來的結果圖，而是從 gene expression matrix 經過分組平均、log2FC、p-value/FDR 後，每個 gene 被轉成一個點。

### 講稿
這裡的 input 是 gene expression matrix，每一列是 gene，每一欄是 sample。動畫先選 UBE2S 當例子，把 PDAC samples 和 normal samples 分開，算出兩邊平均值，再用平均值比例轉成 log2 fold change。接著對每個 gene 做統計檢定並校正成 FDR，所以 y 軸是 -log10 FDR，也就是統計信心。最後每個 gene 都會變成 volcano plot 上的一個點，x 軸表示 tumor-normal expression difference，y 軸表示 statistical confidence，而 UBE2S 和 CCR6 被標出來是因為它們同時是 tumor-high 且顯著的候選。這張圖支持的是「哪些 genes 值得進入下一輪篩選」，但不能證明這些 genes 對 PDAC 有因果性，也不能證明它們一定能做成 biosensor input。

### 關鍵句
In a volcano plot, each dot is one gene after expression difference and statistical confidence have been computed.

## Slide 8 — Machine learning as feature prioritization

### 動畫目的
讓觀眾理解 ML 的角色是 feature prioritization tool，而不是臨床診斷模型。

### 講稿
這裡我們把原本 genes × samples 的矩陣轉置成 samples × genes，因為 machine learning model 需要每一列是一個 sample。每個 sample 都有 label：PDAC 記為 1，normal 記為 0。模型在 training split 中學習哪些 gene columns 有助於分類，然後在 test split 或 cross-validation 中輸出 PDAC probability 並計算 AUC。AUC 接近 1 代表在 discovery cohort 中分類能力很強，但它可能同時包含真實生物差異和 TCGA-vs-GTEx cohort effects，所以我們把 ML 當作 feature prioritization，不把它當作 clinical diagnosis。

### 關鍵句
Here, machine learning ranks informative genes; it is not a validated diagnostic device.

## Slide 9 — SHAP model attribution

### 動畫目的
讓觀眾理解 SHAP value 是從 trained classifier 的 prediction 分解而來，用來解釋某個 sample 的 prediction probability。

### 講稿
這張從一個 sample 的 expression profile 開始，讓模型先輸出 PDAC probability。接著 SHAP 把這個 prediction 拆成每個 gene 的 contribution：正 SHAP value 代表把 prediction 往 PDAC 推，負 SHAP value 代表把 prediction 往 normal 拉。最後形成的 SHAP importance plot 是模型決策的解釋，不是生物機制的證明。因此如果某個 gene SHAP 很高，我們只能說它在模型裡有用，不能說它一定是 PDAC 的 causal driver。

### 關鍵句
SHAP explains the model decision. It does not prove biological causality.

## Slide 10 — SHAP threshold inference

### 動畫目的
讓觀眾理解 threshold 不是憑空指定，而是從 expression value 與 SHAP value 的 dependence relationship 中找出 SHAP crossing zero 的位置。

### 講稿
這張圖的 x 軸是某個 gene 的 expression，y 軸是該 gene 在模型中的 SHAP value。當 SHAP value 小於 0，這個 expression range 對模型比較像 normal；當 SHAP value 大於 0，這個 expression range 開始把 prediction 往 PDAC 推。因此我們用 SHAP = 0 的 crossing point 當作 model-inferred activation threshold。這個 threshold 後面會被寫成 Hill equation 裡的 K_A 或 K_B，但它不是 biochemical Kd，也不是實驗量測到的分子親和力。

### 關鍵句
The SHAP threshold is a model-derived decision boundary, not a biochemical binding constant.

## Slide 11 — UBE2S + CCR6 scatter / pair selection

### 動畫目的
讓觀眾理解 UBE2S + CCR6 不是只因為 scatter plot 好看而被挑出，而是經過 pair scoring：tumor double-high、normal double-high leakage 和 correlation penalty。

### 講稿
這裡我們先從 candidate genes 出發，把 genes 兩兩組合成 candidate pairs。對每一組 pair，我們計算 tumor 中兩個 genes 都高的比例，這代表 sensitivity potential；也計算 normal 中兩個 genes 都高的比例，這代表 off-target leakage。除此之外，我們也加入 correlation penalty，因為兩個完全同步的 genes 對 AND gate 的資訊增益比較有限。最後 UBE2S + CCR6 被選出後，我們在 scatter plot 上畫出 UBE2S threshold vertical line 和 CCR6 threshold horizontal line，右上角就是 AND ON = UBE2S high AND CCR6 high。必須提醒的是 correlation = 0.714，代表它們功能上可能 divergent，但統計上並不 orthogonal。

### 關鍵句
UBE2S + CCR6 is selected by pair scoring, but correlation 0.714 means it is not statistically orthogonal.

## Slide 12 — Hill-equation AND-gate modeling

### 動畫目的
讓觀眾理解 Hill equation 如何把 raw expression 轉成 continuous AND-gate output，而不是只看公式。

### 講稿
這張的 input 是 raw UBE2S 和 CCR6 expression。第一步先做 min-max scaling，把不同量綱的 expression 轉到 0 到 1。第二步分別套入 H(UBE2S) 和 H(CCR6) 兩條 Hill response curves，把 expression 轉成單一 input 的 activation level。第三步把兩個 response 相乘，所以只有兩者都高時，AND-gate output 才會高。最後 heatmap 顯示的是不同 UBE2S 和 CCR6 組合下的 output 強度。公式裡的 K_A 和 K_B 來自前面的 model-inferred thresholds，不是 biochemical dissociation constants。

### 關鍵句
The Hill model converts expression into a simulated AND output, but its K values are inferred expression thresholds.

## Slide 13 — Random-pair control

### 動畫目的
讓觀眾理解我們不是只展示 UBE2S + CCR6 的漂亮結果，而是把它和 1,000 組隨機基因配對形成的背景分布比較。

### 講稿
這裡我們做的是隨機基因組合負控制。問題是：如果我從所有候選基因裡隨便抽兩個，也有可能剛好得到很好的 AUC 嗎？因此我們重複 1,000 次，每次隨機抽兩個 genes，用完全相同的 AND-gate 計算方式算出 AUC，最後形成一個隨機背景分布。可以看到 UBE2S + CCR6 的 AUC 位在這個分布之外，empirical p-value 小於 0.0001。這代表它的表現不是隨機抽樣下常見的結果。不過這個 control 只能支持統計上的 non-random prioritization，不能證明生物因果性。

### 關鍵句
Random-pair control tests whether our selected pair is better than chance, not whether it is biologically causal.

## Slide 14 — Threshold sensitivity analysis

### 動畫目的
讓觀眾理解 SHAP 推估的 K_A 和 K_B 不是精準生化常數，因此必須測試閾值改變時模型是否仍穩定。

### 講稿
這裡我們做的是 threshold sensitivity analysis。因為 K_A 和 K_B 是從模型推估出來的 expression thresholds，不是真正量測到的生化常數，所以我們需要問：如果這些閾值估錯一點，結果會不會完全崩掉？因此我們把 K_A 和 K_B 分別擾動 ±10%、±25% 和 ±50%，每次重新計算 AND-gate output 和 AUC。結果顯示 AUC 仍維持在 0.994 以上，代表 tumor 和 normal 的相對排序在模型中相當穩定。不過 accuracy 仍會受到 decision threshold 影響，因此這不代表未來實驗電路不需要重新校準。

### 關鍵句
Threshold sensitivity shows computational robustness, not biochemical affinity validation.

## Slide 15 — External validation and interpretation

### 動畫目的
讓觀眾理解外部驗證不是單純「成功或失敗」，而是揭示 RNA-seq discovery threshold 轉移到 microarray external cohort 時的 platform-shift 問題。

### 講稿
左邊是 discovery cohort：RNA-seq TCGA/GTEx，AUC 0.9986、sensitivity 97.8%、specificity 99.4%。右邊是 external cohort：microarray GSE62452，AUC 降到 0.648，sensitivity 只有 4.3%，但 specificity 仍有 98.4%。這表示嚴格 threshold 仍然很少誤判 normal，所以 high specificity remains；可是很多 tumor 在 microarray 平台上沒有跨過 RNA-seq 推得的 threshold，所以 sensitivity collapse。正確解讀是：這是一個 high-specificity computational candidate，不是 validated sensitive PDAC detector。

### 關鍵句
External validation tests dataset and platform shift, and it changes the interpretation rather than simply failing the project.

## Slide 16 — Summary & Wet-Lab Translation

### 動畫目的
無動畫；總結三種 validation logic 與後續 wet-lab translation 需求。

### 講稿
總結來說，這份簡報現在不只是展示結果圖，而是交代每張圖如何從資料被計算出來。Random-pair control 回答的是「是不是隨便抽也能得到」，threshold sensitivity 回答的是「K 值估錯時模型排序是否穩定」，external validation 回答的是「跨資料集和平台是否能轉移」。目前 UBE2S + CCR6 應該被稱為 high-specificity computational candidate，而不是已驗證的 biosensor。下一步需要做平台校準、實驗 sensor design，以及 PDAC 和正常細胞的 wet-lab validation。

### 關鍵句
The candidate is computationally prioritized and high-specificity, but wet-lab validation remains essential.
