# 為什麼 GPT-OSS 20B 測試顯示一堆 0%？

## 🔍 問題解釋

### 你看到的 0% 不是模型真的失敗，是**輸出格式問題**！

## 問題示範

### 我們問模型：
```
index 1: value is 100
index 2: value is 200
...
Question: What is the value of index 1?
```

### 期待的答案：
```
100
```

### GPT-OSS 20B 實際回答：
```
<|channel|>analysis<|message|>Let me analyze the list to find index 1. Looking through the items...<|end|>
<|channel|>final<|message|>100<|end|>
```

### 為什麼顯示 0%？

第一次測試程式碼：
```python
# 檢查答案
if "100" in response:  # 找 "100"
    correct = True
```

但 response 是：
```
"<|channel|>analysis<|message|>We need to..."
```

**"100" 被包在特殊標記裡面**，所以每次都判定為錯誤 = 0%！

## 修正後的測試

### 新的解析程式：
```python
def extract_answer(response):
    # 找到 <|channel|>final<|message|> 後面的內容
    pattern = r'<\|channel\|>final<\|message\|>(.*?)(?:<\|end\|>|$)'
    match = re.search(pattern, response)
    if match:
        return match.group(1)  # 提取 "100"
```

### 修正後的結果：
```
10 items:    100% ✅ (原本 0%)
50 items:    100% ✅ (原本 0%)
500 items:   100% ✅ (原本 0%)
2500 items:  100% ✅ (原本 0%)
4500 items:  100% ✅ (原本 0%)
```

## 真正的問題

修正格式後發現 GPT-OSS 20B 的**真正問題**：

### 1. 準確度亂跳
```
100 items:  33% ❌
500 items: 100% ✅ (為什麼變好？)
1000 items: 67%
2500 items:100% ✅ (又變好？)
5000 items: 33% ❌ (又壞了)
```

### 2. 沒有規律
- Mistral：中間位置容易失敗（可預測）
- GPT-OSS：完全隨機（不可預測）

## 結論

### 第一次測試（都是 0%）
- **不是**模型無法理解
- **是**輸出格式解析錯誤

### 修正後測試（33%-100% 亂跳）
- **不是**格式問題了
- **是**模型本身不穩定

## GPT-OSS 20B 特殊之處

### 為什麼有 Channel 格式？

GPT-OSS 20B 設計用於**多階段推理**：
1. `<|channel|>analysis` - 分析階段（思考過程）
2. `<|channel|>final` - 最終答案

類似 OpenAI 的 Chain of Thought，但用特殊標記分隔。

### 優點：
- 可以看到推理過程
- 適合複雜問題

### 缺點：
- 需要特殊解析
- 增加 token 使用量
- 不兼容標準 API

## 實用建議

如果要用 GPT-OSS 20B：

### 1. 必須包裝 API
```python
class GPTOSSWrapper:
    def query(self, prompt):
        raw = call_api(prompt)
        return self.extract_final_answer(raw)

    def extract_final_answer(self, raw):
        # 解析特殊格式
        ...
```

### 2. 預期不穩定
- 同樣問題可能 33% 或 100%
- 需要重試機制
- 不適合要求精確的場合

### 3. 利用大 Context
- 唯一優勢是 100k tokens
- 如果能容忍不穩定性
- 適合實驗性質的大文檔處理

---

**總結**：0% 是**格式問題**，修正後發現**穩定性問題**更嚴重！