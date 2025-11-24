# LLM Context Testing - Executive Summary

## 🎯 Test Goal

**Find out how much text these AI models can REALLY handle on a gaming GPU (RTX 5090)**

We tested 4 models to answer:
- How much can they actually process? (vs what they claim)
- Do they stay accurate with large documents?
- Which one should you actually use?

## 🔬 How We Tested

### The "Needle in Haystack" Method

1. **Create a huge list** with numbered items:
```
index 1: value is 100
index 2: value is 200
...
index 6000: value is 600000
```

2. **Ask the model** to find specific items:
   - Beginning (index 1) - Usually works ✅
   - Middle (index 3000) - Often fails ❌
   - End (index 6000) - Usually works ✅

3. **Keep making the list bigger** until the model:
   - Runs out of memory
   - Starts giving wrong answers
   - Becomes too slow

### Why This Test Matters

- **Marketing vs Reality**: A "131k context" model might only handle 24k on your hardware
- **Real documents**: IEC standards are 300+ pages - need to know what fits
- **Cost planning**: Bigger context = slower = more expensive

## 📊 Results Summary

### On RTX 5090 (32GB VRAM):

| Model | Advertised | Actual Usable | IEC Pages | Speed | Should You Use? |
|-------|------------|---------------|-----------|-------|-----------------|
| **Mistral 24B Q6_K** | 32k tokens | 28k (87%) | **55 pages** ⚠️ | 0.6s ⚡ | ⚠️ **YES BUT CAREFUL** - Bugs at 500/750/1200 items |
| **Magistral 2506** | 32k tokens | 11k (33%) | **21 pages** ⚠️ | 0.7s ⚡ | ❌ **NO - Systematic Bug at 750+ items** |
| **Gemma 27B** | 131k tokens | **12k (9%)** ❌ | **25 pages** ❌ | 1.5s 🐌 | ❌ **NO - Hard limit at 600 items (HTTP 400)** |
| **GPT-OSS 20B** | 131k tokens | 100k (76%) | 200 pages | 2.7s 🐢 | ⚠️ MAYBE - If accuracy not critical |

### Visual Comparison:
```
What they can handle (SAFE capacity):
Mistral:    [███████████░] 55 pages  - Fast, BUGS at 500/750/1200 items ⚠️
Magistral:  [███░░░░░░░░░] 21 pages  - Fast but SYSTEMATIC BUG at 750+ ❌
Gemma:      [█████░░░░░░░] 25 pages  - HTTP 400 hard limit at 600 items ❌
GPT-OSS:    [████████████████████████████████████] 200 pages - Huge but Unreliable
```

## 💡 Key Findings

### 1. Bigger ≠ Better (And Bugs Matter!)
- **Mistral**: Medium context, **SYSTEMATIC BUGS** at 500/750/1200 items (0% middle) ⚠️
- **Magistral**: Medium context, **SYSTEMATIC BUG** at 750+ items (0% middle) ❌
- **GPT-OSS**: Huge context, random accuracy (0-100%)
- **Lesson**: BOTH Mistral models have bugs - must avoid specific item counts!

### 2. Hardware Limits Are Real
- **Gemma** claims 131k but only gets 24k on RTX 5090
- **Why?** Not enough VRAM for the KV cache
- **Lesson**: Check YOUR hardware, not the specs

### 3. Middle Content Gets Lost (Or Broken!)
Both Mistral models have systematic bugs, but at different item counts:
```
Mistral Q6_K (at 500/750/1200 items):
Beginning: 100% accurate ✅
Middle:      0% accurate ❌❌ <- SYSTEMATIC BUG (returns LAST value)
End:       100% accurate ✅

Mistral Q6_K (at 1250 items - SAFE ZONE):
Beginning: 100% accurate ✅
Middle:    100% accurate ✅  <- Works perfectly
End:       100% accurate ✅

Magistral 2506 (≤500 items):
Beginning: 100% accurate ✅
Middle:    100% accurate ✅  <- Works perfectly
End:       100% accurate ✅

Magistral 2506 (750+ items):
Beginning: 100% accurate ✅
Middle:      0% accurate ❌❌ <- SYSTEMATIC BUG (returns wrong value)
End:       100% accurate ✅

Safe Zones for Mistral Q6_K: 100, 250, 1000, 1100, 1250-1400 items
```

### 4. Context Utilization Matters
- **Mistral & Magistral**: Both achieve 96-97% of 32k (excellent)
- **Gemma**: Only 89% of 24k (VRAM-limited)
- **Lesson**: Full hardware utilization = better value

## 🚀 Practical Recommendations

### For Your Use Case:

**If you need reliability** → Use Mistral 24B Q6_K **WITH CAUTION** ⚠️
- Process documents in **55-page chunks** (1250 items max)
- **AVOID 500/750/1200-item boundaries** (systematic bugs)
- **SAFE ZONES**: 250, 1000, 1100, 1250-1400 items
- 0.6 second response time
- Configure chunk limits carefully to avoid bug zones
- Still best option despite bugs (if configured correctly)

**DO NOT use Magistral-Small-2506** ❌
- **SYSTEMATIC BUG**: 0% middle accuracy at 750+ items
- Only reliable for ≤21 page documents (500 items)
- Returns wrong value for middle-position queries
- Downgraded from "Secondary" to "Not Recommended"
- ⚠️ **NOT for production use**

**If you need large documents** → Try GPT-OSS 20B
- Can handle 200+ pages at once
- But expect 30-70% accuracy
- May need to retry queries
- Research use only

**Avoid Gemma 27B** on RTX 5090
- Gets limited to 24k (less than Mistral)
- Slower than Mistral
- No advantages

## 📈 Test Details

- **Hardware**: NVIDIA RTX 5090 (32GB VRAM)
- **Test Type**: Progressive scaling from 100 to 6,500 items
- **Positions**: Test retrieval at start, middle, end
- **Temperature**: 0 (deterministic)
- **Iterations**: 3 queries per size (start/middle/end)
- **Total Tests**: ~200 API calls over 3 hours (4 models)

## 🔄 How to Reproduce

1. Load model on localhost:8080
2. Run: `python context_limit_test.py`
3. Check accuracy at different sizes
4. Find where accuracy drops below 95%

## 📝 Bottom Line

**For production use**: Mistral 24B Q6_K **with careful configuration** ⚠️
- Not the biggest, but best available (despite bugs)
- Fast enough for real-time (0.6s)
- **HAS systematic bugs at 500/750/1200 items** (0% middle accuracy)
- **MUST configure safe zones**: 250, 1000, 1100, 1250-1400 items
- Handles 55-page documents safely (1250 items max)

**DO NOT use for production**: Magistral-Small-2506 ❌
- **SYSTEMATIC BUG discovered** (0% middle accuracy at 750+)
- Only reliable for ≤21 page documents
- Downgraded from "Backup" to "Not Recommended"
- Bug cannot be fixed with prompting
- Use Mistral instead

**For experiments**: GPT-OSS 20B is interesting ⚠️
- Massive context capability (200 pages)
- But needs better accuracy
- Good for research
- Not production-ready

**The surprises**:
1. **BOTH Mistral models have bugs** - Q6_K at 500/750/1200, 2506 at 750+
2. **Bugs are item-count specific** - Works perfectly at 1250, fails at 1200
3. **Hardware matters** - Gemma's 131k becomes 24k on RTX 5090
4. **Always test on YOUR hardware** - Don't trust marketing OR single tests

---

*Share this test to help others avoid these systematic bugs!*

**Test Date**: November 2025 (Updated 2025-11-19 with Mistral Q6_K bug validation)
**Models Tested**: 4 (Mistral 24B Q6_K, Magistral-Small-2506, Gemma 27B, GPT-OSS 20B)
**Tester**: GPT-OSS Benchmark Suite
**Hardware**: RTX 5090 (32GB VRAM)