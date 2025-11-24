# LLM Context Window Real-World Testing Methodology

## Test Goal

### Primary Objective
Determine the **actual usable context window** of Large Language Models (LLMs) when deployed on consumer hardware (RTX 5090 with 32GB VRAM), as opposed to their theoretical/advertised limits.

### Why This Matters
- **Theoretical ≠ Practical**: Models trained on 131k context may only achieve 24k-100k in practice
- **Hardware constraints**: VRAM limitations affect real-world performance
- **Accuracy degradation**: Larger contexts don't guarantee accurate retrieval
- **Production readiness**: Need to know actual limits for system design

### Specific Questions We Aimed to Answer
1. What is the maximum context each model can actually handle on RTX 5090?
2. At what point does accuracy degrade below acceptable levels (95%)?
3. How does retrieval accuracy vary by position (start/middle/end)?
4. What are the speed/latency implications of different context sizes?
5. Which model offers the best balance for production use?

## Testing Methodology

### 1. Test Design: Needle-in-Haystack

We use a "needle-in-haystack" approach - hide specific information in a large context and test if the model can retrieve it.

#### Test Data Structure
```
index 1: The value for item 1 is 100
index 2: The value for item 2 is 200
index 3: The value for item 3 is 300
...
index N: The value for item N is N*100

Question: What is the content of index X?
Expected Answer: X*100
```

#### Why This Design?
- **Objective measurement**: Clear right/wrong answers (no subjective evaluation)
- **Scalable**: Can test from 10 to 10,000+ items systematically
- **Position-sensitive**: Tests attention mechanism across the context
- **Reproducible**: Same test can be run on any model

### 2. Position Testing Strategy

For each context size, we test THREE positions:

```python
test_positions = [
    (1, "first"),           # Tests primacy bias
    (num_items // 2, "middle"),  # Tests attention in middle (hardest)
    (num_items, "last")     # Tests recency bias
]
```

#### Why Test Positions?
- **Attention patterns**: LLMs typically remember beginning and end better
- **Middle position weakness**: Most models struggle with middle content
- **Real-world relevance**: Documents have important info throughout

### 3. Progressive Scaling

Test sizes increase progressively to find the breaking point:

```
Small:   100, 250, 500, 750, 1000 items
Medium:  1500, 2000, 2500, 3000 items
Large:   3500, 4000, 4500, 5000 items
Extreme: 5500, 6000, 6500 items (for 131k models)
```

#### Scaling Strategy
- Start small to verify basic functionality
- Increase gradually to find degradation point
- Continue past failure to find hard limits
- Stop when context is exceeded or accuracy drops below 50%

### 4. Success Metrics

#### Accuracy Scoring
```
Per Size: (Correct Positions / 3) × 100%
- 100% = All three positions correct
- 67% = Two positions correct (typically middle fails)
- 33% = One position correct
- 0% = Complete failure
```

#### Reliability Threshold
- **Reliable**: ≥95% accuracy consistently
- **Usable**: ≥67% accuracy (with caveats)
- **Unreliable**: <67% accuracy
- **Failed**: 0% accuracy or context exceeded

#### Performance Metrics
- **Response time**: Average seconds per query
- **Token count**: Actual tokens used (reported by API)
- **First token latency**: Time to start generating
- **Context utilization**: Used tokens / configured limit

### 5. Test Implementation

#### API Configuration
```python
{
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0,      # Deterministic output
    "max_tokens": 20-50,   # Just need the number
    "timeout": 120         # Long timeout for large contexts
}
```

#### Error Handling
- Retry on timeout (once)
- Log HTTP 400 errors (context exceeded)
- Parse special formats (GPT-OSS channel markers)
- Continue testing even after failures

### 6. Hardware Standardization

All tests run on identical hardware:
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **Inference**: llama.cpp server
- **Endpoint**: localhost:8080
- **Quantization**: Model-specific (Q6_K or F16)

### 7. Models Tested

| Model | Training Context | Configured | Quantization |
|-------|-----------------|------------|--------------|
| Mistral Small 24B | 32k | 32k | Q6_K |
| Gemma 3 27B | 131k | 24k* | Q6_K |
| GPT-OSS 20B | 131k | 131k | F16 |

*Limited by VRAM on RTX 5090

## Test Execution Process

### Step 1: Verify Model Configuration
```bash
curl http://localhost:8080/v1/models  # Check model loaded
curl http://localhost:8080/props       # Check context size
```

### Step 2: Run Progressive Tests
```python
for size in test_sizes:
    accuracy, time, tokens = test_context_size(size)
    if accuracy < 0.5:
        continue  # But keep testing to find limits
    if tokens > context_limit:
        break  # Hard stop
```

### Step 3: Collect Metrics
- Accuracy per position
- Response times
- Token usage
- Failure patterns

### Step 4: Analysis
- Find maximum reliable size (≥95% accuracy)
- Identify degradation point (<95% accuracy)
- Calculate context utilization
- Compare across models

## Key Insights from Methodology

### 1. Accuracy Patterns Reveal Model Behavior

**Consistent patterns** (Mistral):
```
500:  67% (middle fails)
1000: 100% (recovers)
1200: 67% (middle fails)
```
→ Predictable, can work around limitations

**Chaotic patterns** (GPT-OSS):
```
100: 33%, 500: 100%, 1000: 67%, 2500: 100%
```
→ Unpredictable, difficult for production

### 2. Token Count vs Item Count

Different models have different token efficiency:
- Mistral: ~22.6 tokens per item
- Gemma: ~14.6 tokens per item
- GPT-OSS: ~16.7 tokens per item

This affects how much actual content fits in context.

### 3. VRAM Limitations Are Real

Gemma 3 27B example:
- Trained on: 131k tokens
- Theoretical: Should handle 131k
- Reality on RTX 5090: Only 24k tokens
- Reason: KV cache memory requirements

### 4. Special Output Formats

GPT-OSS 20B outputs:
```
<|channel|>analysis<|message|>...<|channel|>final<|message|>100
```
Required special parsing to extract answers.

## Reproducibility

### To Reproduce These Tests:

1. **Setup Model**:
```bash
docker run --gpus all -p 8080:8080 \
  -v /models:/models \
  ghcr.io/ggml-org/llama.cpp:server-cuda \
  -m /models/model.gguf \
  --ctx-size 32768 \
  --n-gpu-layers -1
```

2. **Run Test Script**:
```python
python context_limit_test.py
```

3. **Analyze Results**:
- Check accuracy patterns
- Find maximum reliable size
- Calculate context utilization

### Test Scripts Available:
- `mistral_context_test.py` - Mistral 24B Q6_K testing
- `gemma_context_test.py` - Gemma 27B testing
- `gpt_oss_20b_context_test.py` - GPT-OSS testing
- `sliding_window_rag.py` - Context extension techniques

## Conclusions from Methodology

### What We Learned:

1. **Context limits are hardware-dependent**: Same model performs differently on different GPUs

2. **Accuracy ≠ Context size**: Larger context doesn't guarantee better accuracy
   - Mistral: 32k context, stable accuracy
   - GPT-OSS: 100k context, unstable accuracy

3. **Middle position is universally weak**: All models struggle with information in the middle of context

4. **Real-world usable ≈ 70-95% of configured**: Models rarely achieve 100% of their configured context

5. **Speed vs Context trade-off is real**:
   - Small context = Fast (Mistral 0.6s)
   - Large context = Slow (GPT-OSS 2.7s)

## Recommendations for Practitioners

### Based on This Methodology:

1. **Always test actual context limits** - Don't trust advertised numbers

2. **Test with your actual hardware** - Results vary by GPU

3. **Design for middle-position weakness** - Put important info at start/end

4. **Consider accuracy vs capacity trade-off** - Bigger isn't always better

5. **Have fallback strategies** - Use sliding window when context exceeded

## Citation

If you use this methodology:

```
LLM Context Window Real-World Testing
Date: November 2025
Hardware: NVIDIA RTX 5090 (32GB VRAM)
Framework: llama.cpp
Test Type: Needle-in-Haystack Progressive Scaling
Repository: github.com/[your-repo]/gpt-oss
```

---

*This methodology provides reproducible, objective measurement of LLM context window capabilities in production environments.*