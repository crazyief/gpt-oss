這是一份根據您提供的 **3 顆 LLM 在 RTX 5090 硬體上的 Context Window 實測數據**所整理的技術報告。

本報告採用的結構已完全符合您的要求：**完整的技術報告架構 (A 方案)，並將結論置於報告開頭的執行摘要中。**

---

# 技術報告：消費者級硬體 (RTX 5090) 上的 LLM 實用 Context Window 基準測試

## 執行摘要 (Executive Summary)

### **RAG 專案核心建議**

在 NVIDIA RTX 5090 (32GB VRAM) 的硬體限制下，針對 Local RAG 專案的 LLM 選擇，我們的實證結果顯示：

| 評估項目 | Mistral-Small-24B | Gemma-3-27B | GPT-OSS-20B | **RAG 專案推薦** |
| :--- | :--- | :--- | :--- | :--- |
| **實際可用 Context** | [cite_start]31.7k Tokens (96.8% 配置) [cite: 11] | [cite_start]24.2k Tokens (VRAM 限制) [cite: 18, 12] | [cite_start]100k Tokens (76.4% 配置) [cite: 18] | **Mistral (高穩定性)** |
| **平均響應速度** | [cite_start]**0.6s (極速)** [cite: 18] | [cite_start]1.5s (慢 2.5 倍) [cite: 18] | [cite_start]2.7s (慢 4.5 倍) [cite: 18] | **Mistral (即時互動性)** |
| **穩定性模式** | [cite_start]可預測 (特定中間區塊弱點) [cite: 15] | [cite_start]飄忽不定 (偶發性災難式崩潰) [cite: 12] | [cite_start]**完全混亂 (Chaotic)** [cite: 13] | **Mistral (生產環境首選)** |
| **VRAM 瓶頸** | [cite_start]低 (總用量 23GB) [cite: 18] | [cite_start]**高 (總用量 29GB 導致 context 縮減)** [cite: 18] | [cite_start]高 (總用量 31GB) [cite: 18] | **Mistral (硬體優化)** |

**核心結論：**

[cite_start]**Mistral-Small-24B 是目前在 RTX 5090 平台上最適合 Local RAG 專案的 LLM。** [cite: 14]

[cite_start]儘管其最大 Context 較小 (31.7k)，但它提供了 **極高的 Context 利用率 (96.8%)**、**最快的響應速度 (0.6s)**，以及 **可預期的準確度模式** [cite: 17][cite_start]。對於 RAG 應用至關重要的 **穩定性 (Reliability)**，Mistral 明顯優於其他兩者 [cite: 17]。

***

## 1. 緒論 (Introduction)

### 1.1 問題陳述 (Problem Statement)

[cite_start]LLM 模型的官方宣傳 Context Window (例如 131k tokens) 往往與實際部署在消費者級硬體 (如 RTX 5090 32GB VRAM) 上的效能存在顯著差異 [cite: 16][cite_start]。這種理論與實務的落差會直接影響 RAG 系統的設計，包括 Chunk 大小、檢索策略和終端使用者體驗 [cite: 14]。

### 1.2 測試目的 (Objectives)

[cite_start]本基準測試旨在實證量化以下關鍵問題 [cite: 18, 16]：

1.  **實際 Context 容量 (RQ1)：** 每個模型在 RTX 5090 上實際可處理的最大 Tokens 數量。
2.  **準確度衰退點 (RQ2)：** 準確度開始降至可接受水準 (95% 以下) 的 Context 大小。
3.  **位置依賴性 (RQ3)：** 檢索準確度是否會因資訊在 Context 中的位置 (頭/中/尾) 而異。
4.  **性能影響 (RQ4)：** Context 擴大對延遲 (Latency) 和 VRAM 消耗的影響。

***

## 2. 測試方法 (Methodology)

### 2.1 測試設計：「大海撈針」法 (Needle-in-Haystack)

[cite_start]本測試採用經典的「大海撈針」(Needle-in-Haystack) 方法，這是一種客觀、可量化的檢索任務 [cite: 16, 14]：

* [cite_start]**資料結構：** 建立一個包含編號索引和對應值的超大清單 (e.g., `index N: The value for item N is N*100`) [cite: 16]。
* [cite_start]**查詢方式：** 向模型提問「index X 的值是什麼？」[cite: 16]。
* [cite_start]**結果評估：** 答案客觀可判斷 (要麼對要麼錯)，避免主觀性 [cite: 16]。

### 2.2 位置測試策略 (Position Testing)

[cite_start]對於每個 Context 大小，我們測試三個位置以評估 Attention 機制 [cite: 16, 18]：

1.  **開頭 (Primacy)：** 測試第一個項目。
2.  **正中間 (Middle)：** 測試最困難的 Context 中間區塊 (`num_items // 2`)。
3.  **結尾 (Recency)：** 測試最後一個項目 (`num_items`)。

**準確度閾值：**
* [cite_start]**可靠 (Reliable)：** 準確度 ≥ 95% (生產級) [cite: 16]。
* [cite_start]**可用 (Usable)：** 準確度 ≥ 67% (表示有一個位置失敗，通常是中間) [cite: 16]。

### 2.3 實驗環境與配置 (Setup)

[cite_start]所有測試皆在標準化硬體上執行 [cite: 16, 18]：

| 組件 | 規格 (Specification) |
| :--- | :--- |
| **GPU** | NVIDIA RTX 5090 (32GB VRAM) |
| [cite_start]**推理框架** | llama.cpp server (v0.0.3900) [cite: 16, 18] |
| **溫度 (Temperature)** | [cite_start]0.0 (確保確定性輸出) [cite: 18] |
| **查詢模式** | [cite_start]OpenAI-compatible API, 僅取數字答案 [cite: 16] |
| **量化 (Quantization)** | [cite_start]Mistral/Gemma 採用 Q6\_K；GPT-OSS 採用 F16 [cite: 18] |

***

## 3. 測試結果 (Results)

### 3.1 Context 容量與利用率 (Capacity & Utilization)

| 模型 | 訓練 Context (Train) | 配置 Context (Config) | 實際可用 Tokens (Actual) | 利用率 (Utilization) |
| :--- | :--- | :--- | :--- | :--- |
| **Mistral-24B** | 32k | 32,768 | [cite_start]**31,710** [cite: 18] | [cite_start]**96.8%** [cite: 18] |
| **Gemma-27B** | 131k | [cite_start]24,576 [cite: 18] | [cite_start]24,210 [cite: 18] | [cite_start]98.6% (基於 24k 配置) [cite: 18] |
| **GPT-OSS-20B** | 131k | 131,072 | [cite_start]**100,093** [cite: 18] | [cite_start]76.4% [cite: 18] |

**關鍵發現：**
* [cite_start]**Mistral-24B** 幾乎完整利用了其 32k 的 Context [cite: 11]。
* [cite_start]**Gemma-27B** 儘管宣稱 131k，但在 RTX 5090 上被 **VRAM 瓶頸** 限制到只能配置 24k，**大幅降低了潛在能力** [cite: 18, 12]。
* [cite_start]**GPT-OSS-20B** 實現了最大的 Context (100k+)，但其 **Max Reliable Items** 僅有 **500 個** [cite: 18]。

### 3.2 性能指標 (Performance Metrics)

| 模型 | 平均響應延遲 (Avg Latency) | P95 延遲 (P95 Latency) | Tokens/秒 (Tokens/sec) |
| :--- | :--- | :--- | :--- |
| **Mistral-24B** | [cite_start]**0.6s** [cite: 18] | [cite_start]1.4s [cite: 18] | [cite_start]**52.8** [cite: 18] |
| **Gemma-27B** | [cite_start]1.5s [cite: 18] | [cite_start]3.9s [cite: 18] | [cite_start]21.2 [cite: 18] |
| **GPT-OSS-20B** | [cite_start]2.7s [cite: 18] | [cite_start]5.5s [cite: 18] | [cite_start]14.8 [cite: 18] |

**關鍵發現：**
* [cite_start]**Mistral** 在速度上具有壓倒性優勢，**響應速度是 Gemma 的 2.5 倍，是 GPT-OSS 的 4.5 倍** [cite: 18][cite_start]。這對於需要即時互動的 RAG 應用至關重要 [cite: 14]。

### 3.3 準確度模式 (Accuracy Patterns)

[cite_start]所有模型都展現出獨特的、**非線性 (Non-linear)** 的準確度衰退模式 [cite: 18]。

| 模型 | 開頭 (Start) | 中間 (Middle) | 結尾 (End) | 準確度退化模式 |
| :--- | :--- | :--- | :--- | :--- |
| **Mistral-24B** | [cite_start]95% [cite: 18] | [cite_start]65% [cite: 18] | [cite_start]92% [cite: 18] | [cite_start]U 型 (預期模式，特定位置可復原) [cite: 18, 15] |
| **Gemma-27B** | [cite_start]78% [cite: 18] | [cite_start]71% [cite: 18] | [cite_start]75% [cite: 18] | [cite_start]災難式崩潰 (在 2000 個項目時從 100% 暴跌至 33%) [cite: 18, 12] |
| **GPT-OSS-20B** | [cite_start]72% [cite: 18] | [cite_start]68% [cite: 18] | [cite_start]70% [cite: 18] | [cite_start]**完全混亂 (Chaotic)** (準確度在 33%、67%、100% 之間隨機跳動) [cite: 13, 18] |

***

## 4. 分析與討論 (Analysis & Discussion)

### 4.1 硬體限制與 VRAM 瓶頸

[cite_start]**VRAM 是大型 Context LLM 在消費級硬體上的主要瓶頸** [cite: 16]。

* [cite_start]**Gemma-3-27B 案例：** 該模型的核心問題在於 **KV Cache (Key-Value Cache)** 的記憶體需求 [cite: 18, 12][cite_start]。對於 131k 的訓練 Context，其 KV Cache 理論上需要約 43GB 的 VRAM，遠超過 RTX 5090 的 32GB 限制 [cite: 18][cite_start]。因此，模型只能運行在 24k Context 配置下，浪費了其長 Context 的設計潛力 [cite: 12, 18]。
* [cite_start]**GPT-OSS-20B 案例：** 雖然實現了 100k Context，但採用了 F16 量化，使其總 VRAM 消耗逼近 31GB，並導致極高的延遲 (2.7s) [cite: 18]。

### 4.2 Attention 機制與準確度衰退

[cite_start]所有模型都展示了**中間位置弱點 (Middle Position Weakness)** 的趨勢 [cite: 17]。

* [cite_start]**Mistral-24B：** 展現出可預期的 U 形模式 (頭尾強、中間弱)，但其優勢在於**準確度會在特定 Context 大小 (如 1000 items) 處復原**，顯示其 Attention 演算法具有某種「甜點區」(Sweet Spots) [cite: 15, 18][cite_start]。這使得其行為模式相對可控 [cite: 15]。
* [cite_start]**GPT-OSS-20B：** 其**完全混亂的準確度模式** [cite: 13][cite_start]，即使在較小 Context (100 items) 時也可能突然崩潰 (33% 準確度)，使得它在生產環境中幾乎無法信賴 [cite: 13, 17]。

### 4.3 實作考量 (Implementation Considerations)

* [cite_start]**GPT-OSS 特殊輸出格式：** GPT-OSS 20B 的輸出包含特殊標記 (`<|channel|>...<|message|>...`)，需要額外的程式碼來進行後處理 (Parsing)，增加了實作的複雜度 [cite: 13]。
* [cite_start]**RAG Chunking 建議：** 由於所有模型皆有中間位置弱點，RAG 管道應考慮**避免讓關鍵資訊落入 Context 中間** [cite: 15][cite_start]。對於 Mistral，建議設置最大 Context 為 29,000 Tokens 作為安全緩衝區 [cite: 15]。

***

## 5. 結論與建議 (Conclusion & Recommendation)

### 5.1 最終模型評選

| 模型 | 適用情境 (Use Case) | 建議 (Recommendation) |
| :--- | :--- | :--- |
| **Mistral-24B** | [cite_start]**即時、關鍵準確度 RAG 查詢** [cite: 14] | [cite_start]**✅ 最佳選擇：** 性能、穩定性、硬體利用率的黃金平衡 [cite: 14]。 |
| **Gemma-27B** | N/A (在 RTX 5090 上) | [cite_start]**❌ 避免使用：** 效能遠遜於 Mistral，VRAM 瓶頸嚴重 [cite: 14]。 |
| **GPT-OSS-20B** | [cite_start]**非關鍵、批次處理大型文件 (200+ 頁)** [cite: 17] | [cite_start]**⚠️ 實驗用途：** 僅用於不在乎準確度，需要單次處理超長文件時 [cite: 17]。 |

### 5.2 RAG 專案實作建議

[cite_start]為了確保 Local RAG 專案的成功，我們強烈建議採用 **Mistral-Small-24B** 並執行以下策略 [cite: 15]：

1.  [cite_start]**設定 Context 安全邊界：** 將最大 Context 限制在 **29,000 tokens** 左右 (約 1,280 個 items)，以確保高穩定性 [cite: 15]。
2.  [cite_start]**優化 Chunking 策略：** 為了彌補模型的中間位置弱點，可考慮使用 **滑動視窗 (Sliding Window)** 或在檢索後，將最重要的 Top-K Chunk 置於 Context 的**開頭和結尾**，以最大化檢索準確度 [cite: 15]。
3.  [cite_start]**效能監控：** 在 RAG pipeline 中集成延遲監控，確保 Mistral 0.6s 的響應優勢得以保留 [cite: 18]。