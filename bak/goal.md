

# ✅ **一、產品願景（Product Vision） — 更新後**

建立一個 **基於 LightRAG 思維的本地端 AI 知識助理系統**，
能在不外洩資料的情況下：

* 分析與查找 Cyber Security、產品測試、Risk Assessment（RA）相關文件
* 處理與理解各種專業標準

  * IEC 62443 系列
  * ETSI EN 303 645
  * EN 18031
* 找到條文、找答案、找證據、找不符合之處
* 提供有來源、有理由的專業判讀

所有操作均在本地端進行，適合敏感資料。

---

# ✅ **二、核心目標（High-level Goals） — LightRAG 架構下的更新版**

### **1. 可持續對話的本地 LLM Chatroom（資料庫永久保存）**

* 長對話不中斷
* 上下文不丟失
* 每個 chatroom 自動存入資料庫
* 可隨時繼續先前的工作

---

### **2. 完整文件解析（支援所有必要格式）**

* PDF（含 scanned PDF）
* Excel
* Word
* TXT
* Markdown
* 圖片文字（OCR）

---

### **3. LightRAG 風格的知識建模與查找能力**

* 自動切分文件
* 自動建立語意關係
* 自動產生跨文件的知識網絡
* 回答時提供 PDF yellow highlight（來源位置透明）

---

### **4. 專業領域支援：Cyber Security / 產品測試 / RA / 標準**

包括：

* IEC 62443
* ETSI EN 303 645
* EN 18031
* 各類國際法規
* 各類產品安全測試資料

---

### **5. 查詢能力（基於 LightRAG 思維）**

* 找條文
* 找依據
* 找答案
* 判斷不符合
* 文本比對
* 差異分析
* Answer & Evidence Matching

而且**若資料不齊全，AI 必須回答：
「我無法回答此問題，因為資料不齊全。」**

---

# ✅ **三、系統功能需求（Functional Requirements） — LightRAG 版本**

---

## **A. Chatroom 與工作空間**

1. 系統應提供可持續運作的聊天介面
2. 每個 chatroom 都自動存入資料庫
3. 使用者可重新打開任何 chatroom 並繼續對話
4. Chatroom 支援多專案、多主題並長期追蹤
5. 所有資料皆在本地端，不進行外部傳輸

---

## **B. 文件匯入與知識建模（基於 LightRAG 思維）**

6. 系統支援 PDF、Excel、Word、TXT、Markdown、OCR
7. 自動切分文件並建立 LightRAG-style 語意知識網絡
8. 支援解析法規與標準條款
   　　- IEC 62443
   　　- ETSI EN 303 645
   　　- EN 18031
9. 回答需附來源文件、頁碼、段落
10. PDF 應提供 yellow highlight 顯示原文位置

---

## **C. 查詢與問答能力（LightRAG 模式）**

11. 系統應能找到與問題最相關的文件片段
12. 系統應能找出標準條款在文件中對應的位置
13. 系統應能找出其他文件中的 support evidence
14. 系統能判斷：
    　　- 上傳的 answer 是否符合要求
    　　- 哪些部分符合
    　　- 哪些部分不符合
15. 系統若找不到資料，應回覆：
    　　**「我無法回答此問題，因為資料不齊全。」**

---

## **D. 使用體驗**

16. 系統應在 UI 中顯示引用的 highlight
17. 文件匯入後應可立即查詢
18. 操作流程不需使用者調參
19. 所有引用來源都需清晰明確

---

## **E. GPU 與硬體（依你設備）**

20. 系統將運作於：
    　　- RTX 5090 eGPU（32GB VRAM）
    　　- RTX 4070（8GB VRAM）
21. 系統應優先使用 5090 執行主要推理與 LightRAG 查找負載
22. 不需支援單 GPU 或無 GPU

---

# ✅ **四、User Stories — 更新後（LightRAG 版）**

---

### **User Story 1 — 文件匯入與解析**

「我希望能匯入 PDF、Excel、Word、TXT、Markdown、圖片，
系統自動分析並建立 LightRAG-style 知識網絡。」

---

### **User Story 2 — 找標準條款**

「我希望輸入：

> 幫我找 IEC 62443-4-2 CR 2.11
> 系統能找到條文，並以 PDF yellow highlight 顯示原文位置。」

---

### **User Story 3 — 跨標準差異比較**

「我希望系統能同時比較 IEC 62443、EN 303 645、EN 18031，
產生差異表與對應關係，引用來源透明。」

---

### **User Story 4 — Risk Assessment（RA）分析**

「我希望丟一段技術需求，
系統能從文件中找出風險、控制項、對應標準條文。
資料不足時會明確說明。」

---

### **User Story 5 — Chatroom 長期保存**

「我希望每次對話都能永久保存，
下次可以直接開啟繼續工作。」

---

### **User Story 6 — 來源透明性**

「我希望所有回答都有明確來源與 highlight，
能知道 AI 的推論基礎。」

---

### **User Story 7 — 資料尋找與解答（新加入）**

「我希望可以上傳一個 **question**，
並讓 AI 去：

1. 找到對應的 **標準條款**
2. 在我上傳的其他文件裡
   　- 找出 **answer**
   　- 找出 **evidence (證據)**
3. 或判斷我上傳的 answer：
   　- 是否符合 question 的要求
   　- 哪些地方符合
   　- 哪些地方不符合
   　- 缺少什麼證據

確保回答是透明、有來源、不亂猜的。」

