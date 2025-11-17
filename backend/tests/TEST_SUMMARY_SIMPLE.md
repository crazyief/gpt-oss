# LLM Context Testing - Executive Summary

## 🎯 Test Goal

**Find out how much text these AI models can REALLY handle on a gaming GPU (RTX 5090)**

We tested 3 models to answer:
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
| **Mistral 24B** | 32k tokens | 31k (97%) | 60 pages | 0.6s ⚡ | ✅ YES - Production |
| **Gemma 27B** | 131k tokens | 24k (18%) | 45 pages | 1.5s 🐌 | ❌ NO - Worse than Mistral |
| **GPT-OSS 20B** | 131k tokens | 100k (76%) | 200 pages | 2.7s 🐢 | ⚠️ MAYBE - If accuracy not critical |

### Visual Comparison:
```
What they can handle:
Mistral:  [████████████] 60 pages  - Fast & Reliable
Gemma:    [█████████░░░] 45 pages  - Slow & Limited
GPT-OSS:  [████████████████████████████████████] 200 pages - Huge but Unreliable
```

## 💡 Key Findings

### 1. Bigger ≠ Better
- **Mistral**: Small context, high accuracy (67-100%)
- **GPT-OSS**: Huge context, random accuracy (0-100%)
- **Lesson**: Reliable small > Unreliable large

### 2. Hardware Limits Are Real
- **Gemma** claims 131k but only gets 24k on RTX 5090
- **Why?** Not enough VRAM for the KV cache
- **Lesson**: Check YOUR hardware, not the specs

### 3. Middle Content Gets Lost
All models forget stuff in the middle of documents:
```
Beginning: 90% accurate ✅
Middle:    40% accurate ❌  <- Problem area
End:       85% accurate ✅
```

## 🚀 Practical Recommendations

### For Your Use Case:

**If you need reliability** → Use Mistral 24B
- Process documents in 60-page chunks
- 0.6 second response time
- Consistent accuracy

**If you need large documents** → Try GPT-OSS 20B
- Can handle 200+ pages at once
- But expect 30-70% accuracy
- May need to retry queries

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
- **Total Tests**: ~180 API calls over 2 hours

## 🔄 How to Reproduce

1. Load model on localhost:8080
2. Run: `python context_limit_test.py`
3. Check accuracy at different sizes
4. Find where accuracy drops below 95%

## 📝 Bottom Line

**For production use**: Mistral 24B wins
- Not the biggest, but most reliable
- Fast enough for real-time
- Predictable behavior

**For experiments**: GPT-OSS 20B is interesting
- Massive context capability
- But needs better accuracy
- Good for research

**The surprise**: Hardware matters more than model specs
- Gemma's 131k becomes 24k on RTX 5090
- Always test on YOUR hardware
- Don't trust marketing numbers

---

*Share this test to help others choose the right model for their hardware!*

**Test Date**: November 2025
**Tester**: GPT-OSS Benchmark Suite
**Hardware**: RTX 5090 (32GB VRAM)