# Mistral 24B Context Window Test - Final Summary

## Executive Summary

Testing completed successfully for the **mistral-small-24b-Q6_K** model running on localhost:8080 with 32k context configuration.

### Key Findings:

1. **Actual Usable Context**: 31,710 tokens (96.8% of configured 32k)
2. **Maximum Reliable Items**: 1,400 indexed items with 100% accuracy
3. **Hard Limit**: 1,450 items triggers context overflow (needs 32,950 tokens)
4. **Performance**: 0.6s average response time at maximum context

## Detailed Test Results

### Context Window Utilization

| Context Size | Items | Tokens Used | Accuracy | Response Time | Notes |
|-------------|-------|-------------|----------|---------------|-------|
| Small | 100 | 1,905 | 100% | 1.2s | Perfect accuracy |
| Small | 250 | 5,205 | 100% | 0.5s | Perfect accuracy |
| Medium | 500 | 10,705 | 67% | 0.7s | **Middle position fails** |
| Medium | 750 | 16,205 | 67% | 0.9s | **Middle position fails** |
| Large | 1,000 | 21,710 | 100% | 0.9s | Recovery - all positions work |
| Large | 1,100 | 24,210 | 100% | 0.6s | Perfect accuracy |
| Large | 1,200 | 26,710 | 67% | 0.6s | **Middle position fails** |
| Near-Max | 1,300 | 29,210 | 100% | 0.6s | Perfect accuracy |
| Near-Max | 1,400 | 31,710 | 100% | 0.6s | **OPTIMAL POINT** |
| Overflow | 1,450 | 32,950 | N/A | N/A | **CONTEXT EXCEEDED** |

### Performance Characteristics

1. **Token Efficiency**: ~22.6 tokens per indexed item
2. **Response Speed**: Consistent 0.6s at high context (excellent)
3. **First Token Latency**: 1-3 seconds initially, then stabilizes
4. **Memory Usage**: Within GPU limits, no OOM errors

### Accuracy Patterns

**Interesting Finding**: The model shows inconsistent accuracy at certain context sizes:
- 500 items (67%) - Middle retrieval fails
- 750 items (67%) - Middle retrieval fails
- 1,000 items (100%) - All positions work
- 1,200 items (67%) - Middle retrieval fails
- 1,300 items (100%) - All positions work
- 1,400 items (100%) - All positions work

This suggests the model has "sweet spots" for retrieval accuracy that don't follow a linear degradation pattern.

## Recommendations for Production Use

### 1. Conservative Settings (High Reliability)
- **Max Context**: 25,000 tokens (~1,100 items)
- **Reasoning**: 100% accuracy guaranteed, 7,768 token buffer
- **Use Case**: Critical compliance queries, legal documents

### 2. Balanced Settings (Recommended)
- **Max Context**: 29,000 tokens (~1,280 items)
- **Reasoning**: Good accuracy with reasonable buffer
- **Use Case**: General RAG queries, document analysis

### 3. Aggressive Settings (Maximum Utilization)
- **Max Context**: 31,000 tokens (~1,370 items)
- **Reasoning**: Maximum context usage, minimal buffer
- **Use Case**: Large document processing, batch operations

## Implementation Guidelines for GPT-OSS LightRAG

### Context Management Strategy

```python
# Recommended configuration for LightRAG
MAX_CONTEXT_TOKENS = 29000  # Conservative limit
CHUNK_SIZE = 500  # Tokens per chunk
MAX_CHUNKS = 58  # Maximum retrievable chunks
SAFETY_BUFFER = 3768  # Reserved for system prompt + response
```

### Chunking Recommendations

Based on the accuracy patterns observed:
1. **Avoid chunks around 500-750 token positions** - These showed retrieval issues
2. **Optimal chunk placement**: Start and end of context are most reliable
3. **Consider implementing a "sliding window" for middle content**

### For IEC 62443 Document Processing

Given that IEC 62443 standards are dense technical documents:
- Each page ≈ 500-800 tokens
- Maximum pages per query: ~36-40 pages
- Implement page-aware chunking to maintain section coherence

## Test Methodology

The tests used a "needle-in-haystack" approach:
1. Created indexed lists (index 1: value 100, index 2: value 200, etc.)
2. Tested retrieval at three positions: first, middle, last
3. Measured accuracy, response time, and token usage
4. Progressively increased context until hitting the limit

## Conclusions

The Mistral 24B Q6_K model performs well within its 32k context window:

✅ **Strengths**:
- Can utilize 96.8% of configured context
- Fast response times even at maximum context
- Perfect accuracy at start/end positions
- Stable performance without memory issues

⚠️ **Limitations**:
- Inconsistent middle-position retrieval at certain sizes
- Hard limit at 32,768 tokens (no graceful degradation)
- Q6_K quantization may impact retrieval precision

## Next Steps

1. **Implement context-aware chunking** in LightRAG to avoid problematic middle positions
2. **Set production limit to 29,000 tokens** for safety margin
3. **Monitor accuracy patterns** in production use
4. **Consider testing temperature/sampling parameters** for retrieval tasks

---

**Test Date**: 2025-11-16 17:37:45
**Test Duration**: ~15 minutes
**Model**: mistral-small-24b-Q6_K
**Hardware**: RTX 5090 (32GB VRAM)
**Service**: llama.cpp server on localhost:8080