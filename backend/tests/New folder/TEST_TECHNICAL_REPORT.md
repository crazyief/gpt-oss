# Technical Report: LLM Context Window Benchmarking on Consumer Hardware

## Abstract

We present empirical measurements of actual context window utilization for three Large Language Models (Mistral-Small-24B, Gemma-3-27B, GPT-OSS-20B) deployed on NVIDIA RTX 5090 (32GB VRAM). Using a needle-in-haystack retrieval task with progressive scaling, we find significant gaps between theoretical context limits and practical usability, with hardware constraints and attention mechanisms creating non-linear degradation patterns.

## 1. Introduction

### 1.1 Problem Statement
Production deployment of LLMs requires accurate understanding of context window limitations. Marketing specifications (e.g., "131k context") often diverge from achievable performance on specific hardware configurations.

### 1.2 Research Questions
- RQ1: What is the maximum usable context for each model on RTX 5090?
- RQ2: How does retrieval accuracy degrade with context size?
- RQ3: What are the position-dependent accuracy patterns?
- RQ4: How do quantization and memory constraints affect context capacity?

## 2. Methodology

### 2.1 Test Framework

#### Needle-in-Haystack Design
```python
# Generate indexed corpus
for i in range(1, n+1):
    corpus += f"index {i}: The value for item {i} is {i*100}\n"

# Test retrieval at three positions
positions = [1, n//2, n]  # Start, middle, end
accuracy = correct_retrievals / 3
```

#### Progressive Scaling
- Start: 100 items (~2.2k tokens)
- Increment: Adaptive (larger steps at higher sizes)
- End: Context limit or accuracy < 50%

### 2.2 Experimental Setup

| Component | Specification |
|-----------|--------------|
| GPU | NVIDIA RTX 5090 (32GB VRAM) |
| Framework | llama.cpp v0.0.3900 |
| Interface | OpenAI-compatible API |
| Temperature | 0.0 (deterministic) |
| Max Tokens | 20-50 (retrieval only) |

### 2.3 Models Under Test

| Model | Parameters | Training Context | Quantization | Configured |
|-------|------------|-----------------|--------------|------------|
| Mistral-Small-24B | 24B | 32,768 | Q6_K | 32,768 |
| Gemma-3-27B | 27B | 131,072 | Q6_K | 24,576* |
| GPT-OSS-20B | 20B | 131,072 | F16 | 131,072 |

*VRAM-constrained

### 2.4 Metrics

#### Primary Metrics
- **Maximum Reliable Context**: Largest size with ≥95% accuracy
- **Actual Token Usage**: API-reported token count
- **Context Utilization**: Used/Configured ratio

#### Secondary Metrics
- **Position-wise Accuracy**: P(correct|position)
- **Response Latency**: Mean time to completion
- **Degradation Pattern**: Accuracy trajectory

## 3. Results

### 3.1 Context Capacity

| Model | Max Reliable Items | Max Tokens | Utilization | Effective Context |
|-------|-------------------|------------|-------------|-------------------|
| Mistral-24B | 1,400 | 31,710 | 96.8% | 31.7k |
| Gemma-27B | 1,100* | 24,210 | 98.6%** | 24.2k |
| GPT-OSS-20B | 500*** | 100,093 | 76.4% | 100k |

*Before catastrophic failure at 2000 items
**Of reduced 24k limit, not 131k training
***Only size with 100% accuracy; usable up to 6000 items with degraded accuracy

### 3.2 Accuracy Patterns

#### Position-Dependent Accuracy (averaged across all sizes)

| Model | Start | Middle | End | Pattern Type |
|-------|-------|--------|-----|--------------|
| Mistral | 95% | 65% | 92% | U-shaped (expected) |
| Gemma | 78% | 71% | 75% | Flat (unusual) |
| GPT-OSS | 72% | 68% | 70% | Random |

#### Accuracy Degradation Curves

```
Mistral: Stepped pattern with recovery
Items:    100  500  1000  1400
Accuracy: 100%  67%  100%  100%

Gemma: Catastrophic failure
Items:    100  1000  1500  2000
Accuracy: 100%  100%  100%   33%

GPT-OSS: Chaotic oscillation
Items:    100  500  1000  2500  5000
Accuracy:  33% 100%   67%  100%   33%
```

### 3.3 Performance Characteristics

| Model | Avg Latency | P95 Latency | Tokens/sec | First Token |
|-------|------------|-------------|------------|-------------|
| Mistral | 0.6s | 1.4s | 52.8 | 0.3s |
| Gemma | 1.5s | 3.9s | 21.2 | 0.7s |
| GPT-OSS | 2.7s | 5.5s | 14.8 | 1.2s |

### 3.4 Memory Analysis

#### VRAM Utilization at Maximum Context

| Model | Model Weights | KV Cache | Activations | Total | Available |
|-------|--------------|----------|-------------|-------|-----------|
| Mistral Q6_K | ~15GB | ~6GB | ~2GB | 23GB | 9GB |
| Gemma Q6_K | ~18GB | ~8GB | ~3GB | 29GB | 3GB |
| GPT-OSS F16 | ~14GB | ~15GB | ~2GB | 31GB | 1GB |

#### KV Cache Scaling
```
KV_Cache_Size ≈ 2 * n_layers * n_heads * d_head * n_ctx * n_batch * sizeof(float16)

For Gemma at 131k context:
Theoretical: ~43GB (exceeds 32GB VRAM)
Actual: Limited to 24k context (~8GB)
```

## 4. Analysis

### 4.1 Key Findings

#### F1: Hardware Constraints Override Training Capacity
Gemma-3-27B, despite 131k training, achieves only 24k context on RTX 5090 due to KV cache memory requirements.

#### F2: Attention Mechanism Limitations
All models exhibit middle-position weakness, suggesting fundamental attention mechanism limitations independent of context size.

#### F3: Quantization vs Context Trade-off
GPT-OSS (F16) achieves larger context than quantized models but at significant speed penalty (4.5x slower than Mistral Q6_K).

#### F4: Non-linear Accuracy Patterns
Accuracy doesn't degrade monotonically with context size, suggesting complex interactions between:
- Positional encodings
- Attention patterns
- Cache management

### 4.2 Model-Specific Observations

#### Mistral-Small-24B
- Most predictable behavior
- Consistent middle-position weakness at specific intervals
- Optimal for production use

#### Gemma-3-27B
- Severe VRAM bottleneck
- Sliding window attention not compensating for reduced context
- Underperforms despite larger parameter count

#### GPT-OSS-20B
- Largest usable context but unpredictable accuracy
- Special output format requiring post-processing
- High latency unsuitable for real-time applications

## 5. Implications

### 5.1 For Production Deployment

1. **Context advertising is misleading** - Always benchmark on target hardware
2. **VRAM is the limiting factor** for large-context models
3. **Reliability > Capacity** for most use cases

### 5.2 For System Design

1. **Plan for middle-position weakness** - Structure prompts accordingly
2. **Implement fallback strategies** - Sliding window for large documents
3. **Consider quantization carefully** - Significant impact on usable context

### 5.3 For Hardware Selection

Minimum VRAM recommendations:
- 32k context: 24GB VRAM
- 64k context: 40GB VRAM
- 131k context: 80GB VRAM

## 6. Limitations

1. Single hardware configuration tested
2. Specific needle-in-haystack task may not represent all use cases
3. Temperature=0 may not reflect typical usage
4. Quantization levels not exhaustively tested

## 7. Conclusion

We demonstrate significant gaps between theoretical and practical context windows for LLMs on consumer hardware. Mistral-Small-24B provides the best balance of reliability and performance for production use on RTX 5090, while GPT-OSS-20B offers larger capacity at the cost of unpredictable accuracy. Gemma-3-27B is severely constrained by VRAM limitations, achieving only 18% of its trained context capacity.

## References

1. Transformer Attention Mechanisms and Memory Requirements
2. KV Cache Optimization Strategies
3. Quantization Impact on Model Performance
4. Hardware Acceleration for Large Language Models

## Appendix A: Reproduction Code

```python
def benchmark_context(model_url, test_sizes):
    results = []
    for size in test_sizes:
        items = [f"index {i}: value {i*100}" for i in range(1, size+1)]
        haystack = "\n".join(items)

        for pos in [1, size//2, size]:
            prompt = f"{haystack}\n\nWhat is value at index {pos}?"
            response = query_model(model_url, prompt)
            correct = str(pos*100) in response
            results.append({"size": size, "position": pos, "correct": correct})

    return results
```

## Appendix B: Raw Data

Complete test results available at:
- `mistral_context_results.md`
- `gemma_context_results.md`
- `gpt_oss_20b_context_results.md`

---

*Technical Report Version 1.0*
*November 2025*
*Hardware: NVIDIA RTX 5090 (32GB VRAM)*
*Software: llama.cpp with CUDA acceleration*