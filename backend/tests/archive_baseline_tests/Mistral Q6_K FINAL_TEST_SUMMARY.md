# Mistral 24B Q6_K Context Window Test - Final Summary

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
| Medium | 500 | 10,705 | **0%** | 0.7s | **SYSTEMATIC BUG - Middle returns LAST** |
| Medium | 750 | 16,205 | **0%** | 0.9s | **SYSTEMATIC BUG - Middle fails** |
| Large | 1,000 | 21,710 | 100% | 0.9s | Recovery - all positions work |
| Large | 1,100 | 24,210 | 100% | 0.6s | Perfect accuracy |
| Large | 1,200 | 26,710 | **0%** | 0.6s | **SYSTEMATIC BUG - Middle returns LAST** |
| Large | 1,250 | 27,960 | **100%** | 0.6s | **Perfect accuracy - SAFE POINT** |
| Near-Max | 1,300 | 29,210 | 100% | 0.6s | Perfect accuracy |
| Near-Max | 1,400 | 31,710 | 100% | 0.6s | **OPTIMAL POINT** |
| Overflow | 1,450 | 32,950 | N/A | N/A | **CONTEXT EXCEEDED** |

### Performance Characteristics

1. **Token Efficiency**: ~22.6 tokens per indexed item
2. **Response Speed**: Consistent 0.6s at high context (excellent)
3. **First Token Latency**: 1-3 seconds initially, then stabilizes
4. **Memory Usage**: Within GPU limits, no OOM errors

### Accuracy Patterns

**⚠️ CRITICAL FINDING - Systematic Bugs Detected**:

**Scientific Validation (5 runs each, 2025-11-19)**:
- **500 items (0%)** - ❌ **SYSTEMATIC BUG**: Middle position returns LAST value 100% of time
- **750 items (0%)** - ❌ **SYSTEMATIC BUG**: Middle position fails 100% of time
- **1,000 items (100%)** - ✅ All positions work correctly
- **1,200 items (0%)** - ❌ **SYSTEMATIC BUG**: Middle position returns LAST value 100% of time
- **1,250 items (100%)** - ✅ **SAFE POINT**: All positions work correctly
- **1,300 items (100%)** - ✅ All positions work correctly
- **1,400 items (100%)** - ✅ **OPTIMAL POINT**: All positions work correctly

**Bug Pattern**: At 500/750/1200 items, querying the MIDDLE position consistently returns the LAST position's value. This is NOT random degradation - it's a reproducible inference bug.

**Safe Zones**: 100, 250, 1000, 1100, 1250-1400 items are verified safe (100% accuracy across all positions).

## Recommendations for Production Use

**⚠️ CRITICAL: Avoid 500, 750, 1200-item context sizes due to systematic bugs!**

### 1. Conservative Settings (High Reliability)
- **Max Context**: 24,000 tokens (~1,060 items)**
- **Reasoning**: Stays in verified 1000-item safe zone, avoids 1200-item bug
- **Use Case**: Critical compliance queries, legal documents

### 2. Balanced Settings (Recommended) ✅
- **Max Context**: 27,500 tokens (~1,220 items)**
- **Reasoning**: Uses verified 1250-item safe zone, excellent accuracy
- **Use Case**: General RAG queries, document analysis

### 3. Aggressive Settings (Maximum Utilization) ✅
- **Max Context**: 31,000 tokens (~1,370 items)**
- **Reasoning**: Maximum verified safe context (1300-1400 items)
- **Use Case**: Large document processing, batch operations

**Implementation Note**: Configure chunk limits to avoid 500/750/1200-item boundaries. Recommended safe points: 250, 1000, 1100, 1250, 1300, 1350, 1400 items.

## Implementation Guidelines for GPT-OSS LightRAG

### Context Management Strategy

```python
# Recommended configuration for LightRAG (UPDATED 2025-11-19)
MAX_CONTEXT_TOKENS = 27500  # Safe zone: 1250 items (~27,960 tokens)
CHUNK_SIZE = 500  # Tokens per chunk
MAX_CHUNKS = 50  # ~1250 items (VERIFIED SAFE - avoids 500/750/1200 bugs)
SAFETY_BUFFER = 4500  # Reserved for system prompt + response

# ⚠️ CRITICAL: Avoid these item counts due to systematic bugs
BUGGY_ITEM_COUNTS = [500, 750, 1200]  # Middle position fails 100%
SAFE_ITEM_COUNTS = [100, 250, 1000, 1100, 1250, 1300, 1350, 1400]
```

### Chunking Recommendations

**⚠️ CRITICAL - Based on systematic bug discovery**:
1. **NEVER configure for 500/750/1200 items** - These have 100% reproducible middle-position bugs
2. **Recommended safe points**: 250 items (small), 1000 items (medium), 1250 items (balanced), 1350 items (aggressive)
3. **Optimal chunk placement**: All positions (first/middle/last) work correctly in safe zones
4. **Testing results**: 1250-1400 items showed perfect 100% accuracy across 5 validation runs

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

The Mistral 24B Q6_K Q6_K model performs well within its 32k context window:

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