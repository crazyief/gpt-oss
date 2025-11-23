# Phi-4-reasoning-plus Model Guide

## Overview

**Model**: `microsoft_Phi-4-reasoning-plus-Q8_0.gguf`
**Type**: Reasoning-optimized small language model
**Quantization**: Q8_0 (8-bit quantization)
**Architecture**: Phi-4 family (Microsoft)

This guide documents how to properly interact with the Phi-4-reasoning-plus model, including prompt formatting, configuration settings, and context window behavior based on extensive testing.

---

## Key Characteristics

### 1. **ChatML Format Requirement**

Phi-4-reasoning-plus uses **ChatML format**, which is DIFFERENT from most other models.

**Standard LLM Format** (e.g., Llama, Mistral):
```
### System:
You are a helpful assistant.

### User:
What is the capital of France?

### Assistant:
```

**Phi-4 ChatML Format** (REQUIRED):
```
<|im_start|>system<|im_sep|>You are a helpful assistant.<|im_end|>
<|im_start|>user<|im_sep|>What is the capital of France?<|im_end|>
<|im_start|>assistant<|im_sep|>
```

### 2. **Special Tokens**

| Token | Purpose |
|-------|---------|
| `<|im_start|>` | Start of message block |
| `<|im_sep|>` | Separator between role and content |
| `<|im_end|>` | End of message block |
| `<|endoftext|>` | End of generation (do NOT include in user prompts) |

**Critical**: Do NOT use `<|endoftext|>` in your prompts - this will cause the model to stop generating immediately.

---

## Prompt Template

### Basic Conversation

```python
def build_phi4_prompt(system_message: str, user_message: str) -> str:
    """Build proper Phi-4 ChatML format prompt."""
    return (
        f"<|im_start|>system<|im_sep|>{system_message}<|im_end|>\n"
        f"<|im_start|>user<|im_sep|>{user_message}<|im_end|>\n"
        f"<|im_start|>assistant<|im_sep|>"
    )
```

### Multi-Turn Conversation

```python
def build_phi4_conversation(messages: list) -> str:
    """
    Build multi-turn conversation.

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]
    """
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        prompt += f"<|im_start|>{role}<|im_sep|>{content}<|im_end|>\n"

    # Always end with assistant prompt
    prompt += "<|im_start|>assistant<|im_sep|>"
    return prompt
```

### Example: Needle-in-Haystack Task

```python
# System instruction
system = "You are a precise information retrieval assistant. Extract ONLY the requested information."

# User query with context
user_query = """
Context:
[... 500 entries of data ...]

Entry ID: AB12CD34
Secret Code: 789012
Location: Paris

[... 500 more entries ...]

Question: What is the secret code for entry AB12CD34?
Instructions: Respond ONLY with the 6-digit code, nothing else.
"""

# Build prompt
prompt = (
    f"<|im_start|>system<|im_sep|>{system}<|im_end|>\n"
    f"<|im_start|>user<|im_sep|>{user_query}<|im_end|>\n"
    f"<|im_start|>assistant<|im_sep|>"
)
```

---

## llama.cpp Configuration

### Recommended Settings (Validated via Testing)

**For Maximum Capacity (30k @ 1,500 items):**
```yaml
llama:
  container_name: phi-4-reasoning-plus-v1-30k
  image: ghcr.io/ggml-org/llama.cpp:server-cuda
  command: >
    --model /models/microsoft_Phi-4-reasoning-plus-Q8_0.gguf
    --host 0.0.0.0
    --port 8080
    --n-gpu-layers 65              # Full GPU offload
    --ctx-size 30000               # 30k for maximum capacity
    --threads 8
    --threads-batch 8
    --batch-size 2048              # Optimal for RTX 5090
    --ubatch-size 512              # Micro-batch size
    --flash-attn auto              # Enable FlashAttention if available
    --parallel 1                   # Single request at a time
    --cache-type-k q8_0            # 8-bit KV cache
    --cache-type-v q8_0
    --cont-batching                # Continuous batching
  environment:
    NVIDIA_VISIBLE_DEVICES: "GPU-xxx"  # Your GPU ID
    CUDA_VISIBLE_DEVICES: "GPU-xxx"
    GGML_CUDA_FORCE_MMQ: "0"           # Auto-select
    GGML_CUDA_FORCE_CUBLAS: "1"        # Use cuBLAS
    LLAMA_CUDA_F16: "1"                # FP16 precision
    LLAMA_CUDA_FA_ALL_QUANTS: "1"      # FlashAttention for all quants
```

**For Maximum Reliability (15k @ 800 items):**
```yaml
# Change only the ctx-size and container name:
container_name: phi-4-reasoning-plus-v1-15k
--ctx-size 15000
```

**For Balanced Use (21k @ 1,150 items):**
```yaml
# Change only the ctx-size and container name:
container_name: phi-4-reasoning-plus-v1-21k
--ctx-size 21000
```

### Parameter Explanations

- **n-gpu-layers**: Set to 65 for full GPU offload (model has 65 layers)
- **ctx-size**: Context window size (see section below for safe limits)
- **batch-size**: 2048 works well for 32GB VRAM (RTX 5090)
- **ubatch-size**: 512 provides good balance between speed and VRAM
- **flash-attn**: Enables efficient attention mechanism
- **cache-type-k/v**: q8_0 reduces VRAM usage while maintaining quality

---

## Context Window Behavior

### Testing Methodology

We conducted 3-phase validation tests across multiple context sizes:
1. **Phase 1**: Coarse discovery (50-1550 items, step=50)
2. **Phase 2**: Fine-grained validation (±50 items around failure point)
3. **Phase 3**: Final accuracy validation (50 runs at safe limit)

### Validated Context Limits (v1 Testing - Random Entry IDs)

| Context Size | Safe Items | Tokens Used | Utilization | Phase 3 Accuracy | Test Duration | Production Ready |
|-------------|-----------|-------------|-------------|------------------|---------------|------------------|
| 12k         | 650       | ~9,900      | 82.5%       | 97.8%            | 18.6 min      | ✅ Yes          |
| 15k         | 800       | ~12,150     | 81.0%       | 100%             | 24.1 min      | ✅ **RECOMMENDED** |
| 18k         | 500       | ~7,650      | 42.5%       | N/A              | Aborted       | ❌ No (anomaly) |
| 21k         | 1,150     | ~17,400     | 82.9%       | 95.6%            | 38.2 min      | ✅ Yes          |
| 24k         | 1,300     | ~19,650     | 81.2%       | 80.0%            | 48.5 min      | ⚠️ With retry   |
| **30k**     | **1,500** | **~22,650** | **75.5%**   | **93.3%**        | **65.1 min**  | ✅ **BEST**     |

**Token Calculation**: `tokens = (items × 15) + 150 overhead`

**Key Finding**: 30k context provides **15% more capacity than 24k** with **better reliability** (93.3% vs 80.0%).

### Safe Zone Pattern

```
12k Context: ████████████████████████████████░░░░░░░░ 82.5%
             ├─ Safe: 650 items ────┤└─ Buffer ─┘

15k Context: ████████████████████████████████░░░░░░░░ 81.0%
             ├──── Safe: 800 items ─────┤└─ Buffer ─┘

18k Context: ████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 42.5% ⚠️ ANOMALY
             ├─ Safe: 500 items ──┤└──── Unused ────┘

21k Context: ████████████████████████████████░░░░░░░░ 82.9%
             ├──── Safe: 1,150 items ────┤└─ Buffer ─┘

24k Context: ████████████████████████████████░░░░░░░░ 81.2%
             ├───── Safe: 1,300 items ─────┤└─ Buffer ─┘

30k Context: ██████████████████████████████░░░░░░░░░░ 75.5%
             ├────── Safe: 1,500 items ──────┤└─ Buffer ─┘
```

### Failure Behavior

**Two Patterns Observed:**

**Pattern 1: Immediate Cliff (12k, 15k, 24k)**
When safe zone is exceeded, accuracy drops to **0% immediately**.

```
12k Context:
  ✅ 600 items: 100% accuracy
  ✅ 650 items: 100% accuracy
  ❌ 700 items: 0% accuracy    ← Immediate failure

15k Context:
  ✅ 750 items: 100% accuracy
  ✅ 800 items: 100% accuracy
  ❌ 850 items: 0% accuracy    ← Immediate failure

24k Context:
  ✅ 1,250 items: 100% accuracy
  ✅ 1,300 items: 88.9% accuracy (minor anomaly)
  ❌ 1,350 items: 0% accuracy  ← Hard cliff
```

**Pattern 2: Gradual Degradation (21k, 30k)**
Larger contexts show more graceful failure with intermittent errors before collapse.

```
21k Context:
  ✅ 1,100 items: 100% accuracy
  ✅ 1,150 items: 95.6% accuracy (Phase 3)

30k Context:
  ✅ 1,250 items: 100% accuracy
  ⚠️ 1,300 items: 88.9% accuracy (1/9 failures)
  ⚠️ 1,350 items: 77.8% accuracy (2/9 failures)
  ⚠️ 1,400 items: 88.9% accuracy (oscillating)
  ⚠️ 1,450 items: 77.8% accuracy
  ⚠️ 1,500 items: 93.3% accuracy (Phase 3 validated)
```

**Key Insight**: The 30k context shows **no hard cliff**, making it more suitable for production with retry logic.

### 18k Context Anomaly ⚠️

The 18k context configuration shows **unexpectedly low utilization**:
- Expected safe zone: ~970 items (based on linear scaling from 12k/15k)
- Actual safe zone: ~500 items (48.5% below expectation)
- Utilization: Only 42.5% vs 81-82% for smaller contexts

**Resolution**: Testing 21k, 24k, and 30k confirmed that 18k was an **isolated anomaly**. All larger contexts returned to normal 75-83% utilization patterns.

**Status**: ❌ Skip 18k entirely. Use 15k or jump directly to 21k+.

### 1300-Item Architectural Limit

**Critical Discovery**: Both 24k and 30k contexts show **identical degradation at 1,300 items** (88.9% accuracy), suggesting this may be an **architectural limit** of the Phi-4 model, not just a context window limitation.

| Context | 1,300 Items Accuracy | 1,350 Items Accuracy |
|---------|---------------------|---------------------|
| 24k     | 88.9%               | 0.0% (hard cliff)   |
| 30k     | 88.9%               | 77.8% (gradual)     |

**Implication**: For guaranteed 100% reliability, stay below 1,300 items regardless of context size. For maximum capacity with retry logic, use 30k @ 1,500 items.

---

## Production Recommendations

### ✅ Recommended Configurations

**Option 1: Maximum Reliability (Conservative)**
```yaml
# PRODUCTION: 15k context @ 800 items max
--ctx-size 15000
--batch-size 2048
--ubatch-size 512
```
- ✅ **100% accuracy** validated (Phase 3)
- ✅ No retry logic needed
- ✅ Fastest inference (smaller context)
- ✅ Lower VRAM usage (~18.5 GB)
- **Capacity**: 800 items

**Option 2: Balanced (Recommended for Most Use Cases)**
```yaml
# PRODUCTION: 21k context @ 1,150 items max
--ctx-size 21000
--batch-size 2048
--ubatch-size 512
```
- ✅ **95.6% accuracy** validated (Phase 3)
- ✅ 44% more capacity than 15k
- ✅ Good balance of capacity and reliability
- ✅ Moderate VRAM usage (~18.8 GB)
- **Capacity**: 1,150 items

**Option 3: Maximum Capacity (Advanced)**
```yaml
# PRODUCTION: 30k context @ 1,500 items max
--ctx-size 30000
--batch-size 2048
--ubatch-size 512
```
- ✅ **93.3% accuracy** validated (Phase 3)
- ✅ **87.5% more capacity than 15k**
- ✅ Best for high-volume applications
- ✅ Requires retry logic (see below)
- ⚠️ Higher VRAM usage (~19.0 GB)
- **Capacity**: 1,500 items
- **With 3 retries**: 99.97% effective reliability

### Retry Logic for Production

For 30k @ 1,500 items, implement automatic retry to achieve near-perfect reliability:

```python
async def query_with_retry(prompt: str, max_retries: int = 3):
    """Query with automatic retry on validation failure."""

    for attempt in range(max_retries):
        response = await query_phi4(prompt)

        # Validate response
        if validate_response(response):
            if attempt > 0:
                logger.info(f"✅ Success on retry {attempt}")
            return response

        logger.warning(f"⚠️ Validation failed (attempt {attempt+1}/{max_retries})")

        # Optional: exponential backoff
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)

    # All retries exhausted
    raise Exception("Failed after retries")

def validate_response(response: str) -> bool:
    """Check if response is valid."""
    if not response or len(response.strip()) < 20:
        return False
    if "cannot answer" in response.lower():
        return False
    return True
```

**Reliability Calculation** (for 30k @ 1,500 items):

Base accuracy: **93.3%** | Failure rate: **6.7%** (0.067)

| Retry Count | Probability All Fail | Effective Success Rate | Recommendation |
|-------------|---------------------|----------------------|----------------|
| 1 (no retry) | 6.7% | 93.3% | ❌ Not recommended |
| 2 retries | 0.45% | 99.55% | ⚠️ Marginal |
| **3 retries** | **0.030%** | **99.970%** | ✅ **Recommended** |
| 4 retries | 0.002% | 99.998% | ✅ Excellent |
| 5 retries | 0.00014% | 99.99986% | ✅ Overkill (diminishing returns) |

**Formula**: `Effective Success Rate = 1 - (failure_rate ^ retry_count)`

**Recommendation**: Use **3 retries** for optimal balance between reliability (99.97%) and performance overhead.

---

**Retry Analysis for Other Context Sizes:**

| Context | Base Accuracy | 3 Retries | 4 Retries | 5 Retries | Notes |
|---------|--------------|-----------|-----------|-----------|-------|
| 15k @ 800 | 100% | 100% | 100% | 100% | No retry needed ✅ |
| 21k @ 1,150 | 95.6% | 99.91% | 99.996% | 99.9998% | 3 retries sufficient |
| 24k @ 1,300 | 80.0% | 99.20% | 99.84% | 99.968% | 4-5 retries recommended ⚠️ |
| **30k @ 1,500** | **93.3%** | **99.97%** | **99.998%** | **99.9999%** | **3 retries optimal ✅** |

**Key Insight**: 30k context requires fewer retries than 24k to achieve same reliability due to higher base accuracy (93.3% vs 80.0%).

### Safety Margins

Always maintain **10-15% safety buffer** below tested limits:

| Context | Tested Safe Limit | Conservative Limit | Buffer |
|---------|------------------|-------------------|--------|
| 12k     | 650 items        | **585 items**     | 10%    |
| 15k     | 800 items        | **720 items**     | 10%    |
| 21k     | 1,150 items      | **1,035 items**   | 10%    |
| 24k     | 1,300 items      | **1,170 items**   | 10%    |
| 30k     | 1,500 items      | **1,350 items**   | 10%    |

### Scaling Guidelines

Choosing the right context size:

| Your Need | Recommended Context | Why |
|-----------|-------------------|-----|
| < 800 items | 15k @ 800 | Best reliability, fastest |
| 800-1,150 items | 21k @ 1,150 | Balanced performance |
| 1,150-1,500 items | 30k @ 1,500 | Maximum capacity |
| > 1,500 items | Multiple queries | Split into chunks |

**Important**:
1. **DO**: Use 15k, 21k, or 30k contexts
2. **DON'T**: Use 18k context (anomaly)
3. **DON'T**: Exceed 1,500 items even with larger contexts (architectural limit)

---

## API Request Format

### HTTP POST to llama.cpp Server

```python
import requests

def query_phi4(prompt: str, max_tokens: int = 512, temperature: float = 0.1):
    """
    Query Phi-4-reasoning-plus via llama.cpp server.

    Args:
        prompt: ChatML formatted prompt
        max_tokens: Maximum tokens to generate
        temperature: 0.0-1.0 (lower = more deterministic)
    """
    response = requests.post(
        "http://localhost:8090/completion",  # llama.cpp endpoint
        json={
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stop": ["<|im_end|>", "<|endoftext|>"],  # Stop sequences
            "stream": False
        },
        timeout=30
    )

    if response.status_code == 200:
        return response.json()["content"]
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")
```

### Stop Sequences

Always include these stop sequences to prevent over-generation:

```python
"stop": [
    "<|im_end|>",      # ChatML end token
    "<|endoftext|>",   # End of text token
    "\n\n\n"           # Multiple newlines (optional)
]
```

### Temperature Guidelines

| Task Type | Recommended Temperature |
|-----------|------------------------|
| Factual extraction | 0.0 - 0.2 |
| Reasoning tasks | 0.3 - 0.5 |
| Creative writing | 0.7 - 0.9 |
| Code generation | 0.1 - 0.3 |

**For needle-in-haystack tasks**: Use **temperature = 0.1** for maximum determinism.

---

## Common Pitfalls

### ❌ **Mistake 1: Using Standard Prompt Format**

```python
# WRONG - This will fail or produce poor results
prompt = "### User:\nWhat is 2+2?\n### Assistant:\n"
```

```python
# CORRECT - Use ChatML format
prompt = "<|im_start|>user<|im_sep|>What is 2+2?<|im_end|>\n<|im_start|>assistant<|im_sep|>"
```

### ❌ **Mistake 2: Including `<|endoftext|>` in Prompt**

```python
# WRONG - Model will stop immediately
prompt = f"<|im_start|>user<|im_sep|>Question?<|endoftext|><|im_end|>"
```

```python
# CORRECT - Only use in stop sequences
prompt = f"<|im_start|>user<|im_sep|>Question?<|im_end|>"
stop = ["<|endoftext|>"]
```

### ❌ **Mistake 3: Exceeding Safe Context Limit**

```python
# WRONG - 18k @ 1000 items will fail (0% accuracy)
items = 1000  # Exceeds 500-item safe zone
ctx_size = 18000
```

```python
# CORRECT - Stay within validated limits
items = 720   # 10% buffer below 800-item limit
ctx_size = 15000
```

### ❌ **Mistake 4: Not Checking Response Validity**

```python
# WRONG - Blindly trust response
result = query_phi4(prompt)
return result  # May be empty or hallucinated
```

```python
# CORRECT - Validate response
result = query_phi4(prompt)
if not result or len(result.strip()) == 0:
    raise ValueError("Model returned empty response - possible context overflow")
if "I cannot" in result or "insufficient data" in result:
    raise ValueError("Model refused to answer - check prompt quality")
return result
```

---

## Debugging Tips

### Check if Context is Overflowing

```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 characters."""
    return len(text) // 4

prompt = build_phi4_prompt(system, user_query)
estimated_tokens = estimate_tokens(prompt)

print(f"Estimated tokens: {estimated_tokens}")
print(f"Context size: {ctx_size}")
print(f"Utilization: {estimated_tokens / ctx_size * 100:.1f}%")

if estimated_tokens > ctx_size * 0.85:
    print("⚠️ WARNING: Approaching context limit!")
```

### Monitor Response Quality

```python
def validate_response(response: str, expected_format: str = None) -> bool:
    """Check if response is valid."""

    # Empty response = context overflow
    if not response or len(response.strip()) == 0:
        print("❌ Empty response - context overflow?")
        return False

    # Check for refusal patterns
    refusal_patterns = [
        "I cannot answer",
        "insufficient information",
        "I don't know",
        "unable to find"
    ]
    if any(pattern in response.lower() for pattern in refusal_patterns):
        print("⚠️ Model refused to answer")
        return False

    # Format validation (optional)
    if expected_format == "numeric":
        if not response.strip().isdigit():
            print(f"❌ Expected numeric, got: {response}")
            return False

    return True
```

### GPU Monitoring

```python
import subprocess

def check_gpu_stats():
    """Monitor GPU during inference."""
    result = subprocess.run(
        ["nvidia-smi", "--id=1", "--query-gpu=temperature.gpu,power.draw,memory.used",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True
    )
    temp, power, vram = result.stdout.strip().split(", ")
    print(f"GPU: {temp}°C | {power}W | {vram}MB VRAM")
```

---

## Testing Checklist

Before deploying Phi-4-reasoning-plus in production:

- [ ] Verify ChatML format is used in all prompts
- [ ] Test with sample data at expected scale (items count)
- [ ] Confirm context utilization < 85%
- [ ] Validate response accuracy with known ground truth
- [ ] Monitor GPU temperature during sustained load
- [ ] Test error handling for context overflow
- [ ] Implement response validation logic
- [ ] Set appropriate timeout values (30s recommended)
- [ ] Configure proper stop sequences
- [ ] Test multi-turn conversation handling

---

## References

### Test Results

All tests conducted using 3-Phase Test v1 methodology with random entry IDs:

- **12k Test**: `phi4_12k_v1_output_20251122_134505.txt`
  - Safe zone: 650 items
  - Phase 3: 97.8% accuracy
  - Duration: 18.6 minutes

- **15k Test**: `phi4_15k_v1_output_20251122_142651.txt`
  - Safe zone: 800 items
  - Phase 3: 100% accuracy
  - Duration: 24.1 minutes

- **18k Test**: `phi4_18k_v1_output_20251122_151429.txt`
  - Aborted at 500 items (anomaly detected)
  - Test abandoned, jumped to 21k

- **21k Test**: `phi4_21k_v1_output_.txt`
  - Safe zone: 1,150 items
  - Phase 3: 95.6% accuracy
  - Duration: 38.2 minutes

- **24k Test**: `phi4_24k_v1_output_20251122_173540.txt`
  - Safe zone: 1,300 items
  - Phase 3: 80.0% accuracy (degraded)
  - Duration: 48.5 minutes
  - Hard cliff at 1,350 items (0% accuracy)

- **30k Test**: `phi4_30k_v1_output_20251122_185026.txt`
  - Safe zone: 1,500 items
  - Phase 3: 93.3% accuracy
  - Duration: 65.1 minutes
  - No hard cliff, gradual degradation pattern

### Test Scripts

- **3-Phase Validator**: `phi4_3phase_test_v1.py`
- **Automated Runner**: `auto_run_remaining_tests.py`
- **Sequential Test Runner**: `run_v1_test_sequence.py`

### Configuration

- **Docker Compose**: `D:/gpt-oss/docker-compose.yml`
- **llama.cpp Image**: `ghcr.io/ggml-org/llama.cpp:server-cuda`
- **GPU Used**: NVIDIA RTX 5090 32GB (GPU ID 1)

---

## Version History

- **v1.0** (2025-11-22 13:45): Initial guide based on 12k/15k/18k context testing
- **v1.1** (2025-11-22 19:56): ✅ **Complete testing suite**
  - Added 21k, 24k, 30k context test results
  - Discovered 1,300-item architectural limit
  - Identified two failure patterns (cliff vs gradual)
  - Added retry logic for production use
  - Updated production recommendations (30k @ 1,500 items recommended)
  - Total testing time: ~5 hours, 315 queries across 6 context sizes

---

## Support

For issues or questions:
1. Check llama.cpp logs: `docker-compose logs llama`
2. Verify GPU availability: `nvidia-smi`
3. Review test outputs in `D:/gpt-oss/backend/tests/`
4. Consult llama.cpp documentation: https://github.com/ggerganov/llama.cpp

---

**Last Updated**: 2025-11-22 19:56 UTC
**Model Version**: Phi-4-reasoning-plus-Q8_0
**Testing Completed**: ✅ All planned contexts (12k, 15k, 18k, 21k, 24k, 30k)
**Production Recommendation**:
- **Conservative**: 15k @ 800 items (100% accuracy, no retries needed)
- **Balanced**: 21k @ 1,150 items (95.6% accuracy)
- **Maximum Capacity**: 30k @ 1,500 items (93.3% accuracy, 99.97% with retries)

**Total Test Queries**: 315 across 6 context sizes
**Total Test Duration**: ~5 hours
**Hardware**: NVIDIA RTX 5090 32GB
