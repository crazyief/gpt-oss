# 3-Model Context Comparison on RTX 5090

## Executive Summary

Testing completed for three models on RTX 5090 (32GB VRAM) with real-world needle-in-haystack context tests:

| Model | Winner | Why |
|-------|--------|-----|
| **Mistral 24B** | 🥈 Silver | Most stable, fast, reliable 32k context |
| **Gemma 3 27B** | 🥉 Bronze | VRAM limited to 24k, slower |
| **GPT-OSS 20B** | 🥇 Gold* | Largest usable context (100k) but unstable |

*With significant caveats - see details below

## Detailed Test Results

### Configuration vs Reality on RTX 5090

| Model | Trained On | Configured | Actually Usable | Utilization |
|-------|-----------|------------|----------------|-------------|
| **Mistral Small 24B** | 32k | 32k | 31,710 tokens | 96.8% ✅ |
| **Gemma 3 27B** | 131k | 24k* | 21,928 tokens | 89.2% of 24k |
| **GPT-OSS 20B** | 131k | 131k | ~100k tokens | 76.3% ⚠️ |

*Gemma limited by VRAM despite 131k training

### Performance Metrics

| Model | Max Items | Max Tokens | Avg Speed | Reliability |
|-------|-----------|------------|-----------|-------------|
| **Mistral 24B** | 1,400 | 31,710 | 0.6s | Stable (67-100%) |
| **Gemma 3 27B** | 1,500 | 21,928 | 1.5s | Unstable (33-100%) |
| **GPT-OSS 20B** | 6,000 | 100,093 | 2.7s | Very Unstable (0-100%) |

### Accuracy Patterns

#### Mistral 24B (Most Predictable)
```
100 items:   100% ✅
500 items:    67% (middle fails)
1000 items:  100% ✅
1400 items:  100% ✅
Pattern: Consistent middle-position weakness
```

#### Gemma 3 27B (Erratic)
```
100 items:   100% ✅
500 items:   100% ✅
1250 items:   67% (middle fails)
1750 items:   67% (first fails!)
2000 items:   33% ❌ (catastrophic)
Pattern: Unpredictable failures
```

#### GPT-OSS 20B (Chaotic)
```
10 items:    100% ✅
50 items:    100% ✅
100 items:    33% ❌
500 items:   100% ✅
1000 items:   67%
2500 items:  100% ✅
4500 items:  100% ✅
5000 items:   33% ❌
6000 items:   33% ❌
Pattern: Completely random!
```

## Real-World Implications

### For IEC 62443 Document Processing

| Model | Pages Capacity | Use Case | Recommendation |
|-------|---------------|----------|----------------|
| **Mistral** | 60-65 pages | Single sections | ✅ Production ready |
| **Gemma** | 45-50 pages | Small docs | ⚠️ Too limited |
| **GPT-OSS** | 200+ pages | Entire standards | ⚠️ If accuracy not critical |

### Context Window Visualization

```
Mistral:  [████████████████] 32k (Fully utilized)
Gemma:    [████████████░░░░] 24k (VRAM limited from 131k)
GPT-OSS:  [████████████████████████████████████████░░░░] 100k of 131k
          0        32k       64k       96k      128k
```

## Critical Issues Discovered

### 1. GPT-OSS Output Format Issue
```
Normal models: "100"
GPT-OSS: "<|channel|>analysis<|message|>...<|channel|>final<|message|>100"
```
Requires special parsing to extract actual answers.

### 2. Gemma VRAM Limitation
- Model supports 131k context
- RTX 5090 can only provide 24k
- Worse than Mistral despite being newer

### 3. Accuracy vs Context Trade-off
```
Mistral: Small context, high reliability
GPT-OSS: Large context, terrible reliability
Gemma:   Small context, poor reliability (worst of both)
```

## Speed Analysis

| Model | First Token | Avg Response | 10 Queries | Suitable For |
|-------|------------|--------------|------------|--------------|
| **Mistral** | 0.6-1.4s | 0.6s | 6s | Real-time chat ✅ |
| **Gemma** | 0.7-3.9s | 1.5s | 15s | Batch processing |
| **GPT-OSS** | 0.6-5.5s | 2.7s | 27s | Background jobs |

## Memory Usage on RTX 5090 (32GB)

| Model | Model Size | Context Memory | Total Used | Free |
|-------|-----------|---------------|------------|------|
| **Mistral 24B Q6_K** | ~15GB | ~6GB | ~21GB | 11GB |
| **Gemma 27B Q6_K** | ~18GB | ~8GB | ~26GB | 6GB |
| **GPT-OSS 20B F16** | ~14GB | ~15GB | ~29GB | 3GB |

## Final Recommendations

### Choose Mistral 24B if:
- ✅ Need reliable, production-ready solution
- ✅ Speed is important (0.6s responses)
- ✅ 60 pages is sufficient
- ✅ Stability matters

### Choose GPT-OSS 20B if:
- ✅ Need to process 100+ page documents
- ✅ Can tolerate inconsistent accuracy
- ✅ Have time for multiple retries
- ⚠️ Can handle special output format

### Avoid Gemma 3 27B because:
- ❌ Smallest usable context (worse than Mistral)
- ❌ Slowest speed (1.5s)
- ❌ Poor accuracy patterns
- ❌ No advantages on RTX 5090

## Verdict for Your GPT-OSS Project

**For production use: Mistral 24B**
- Most reliable for IEC 62443 analysis
- Fast enough for real-time queries
- Predictable behavior

**For experimentation: GPT-OSS 20B**
- Can handle full documents
- Interesting for research
- But needs accuracy improvements

**Skip: Gemma 3 27B**
- Handicapped by VRAM limits
- No benefits over Mistral
- Wait for better hardware

## Test Methodology

- **Test Type**: Needle-in-haystack (indexed items 1-N)
- **Positions Tested**: First, Middle, Last
- **Hardware**: RTX 5090 (32GB VRAM)
- **Quantization**: Mistral Q6_K, Gemma Q6_K, GPT-OSS F16
- **Success Criteria**: 95%+ accuracy for "reliable"

---

*Testing completed: 2025-11-16*
*Total test time: ~2 hours*
*Total API calls: ~180*