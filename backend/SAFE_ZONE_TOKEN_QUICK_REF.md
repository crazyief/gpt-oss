# SAFE_ZONE_TOKEN Quick Reference

## What You Need to Know

### The Hard Limit
```python
SAFE_ZONE_TOKEN = 22,800 tokens (TOTAL)
```

This is:
- Conversation history (prompt)
- **PLUS** LLM response
- **PLUS** formatting overhead

**NOT** just the response!

### How to Use

#### In API Endpoints (chat.py)
```python
from app.utils.token_counter import calculate_max_response_tokens
from app.config import settings

# Build prompt
prompt = llm_service.build_chat_prompt(history)

# Calculate dynamic max_tokens
max_response_tokens = calculate_max_response_tokens(
    prompt=prompt,
    safe_zone_token=settings.SAFE_ZONE_TOKEN,
    safety_buffer=100,
    minimum_response=500
)

# Use in streaming
async for token in llm_service.generate_stream(
    prompt=prompt,
    max_tokens=max_response_tokens,  # Dynamic!
    ...
):
```

#### For Token Estimation
```python
from app.utils.token_counter import estimate_tokens

# Estimate tokens in text
text = "Your text here"
tokens = estimate_tokens(text)  # ~characters / 4
```

#### For Conversation History
```python
from app.utils.token_counter import estimate_conversation_tokens

messages = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
]
tokens = estimate_conversation_tokens(messages)
```

### What Happens at Different Conversation Lengths

| History Tokens | Max Response | What User Gets |
|----------------|--------------|----------------|
| 100 | 22,600 | Very long, comprehensive answer |
| 1,000 | 21,700 | Very long answer |
| 5,000 | 17,700 | Long, detailed answer |
| 10,000 | 12,700 | Medium-length answer |
| 15,000 | 7,700 | Shorter but complete answer |
| 20,000 | 2,700 | Brief but useful answer |
| 22,000 | 700 | Very short answer |
| 22,500 | 200 | Minimal answer (ERROR logged) |

### Error Scenarios

#### WARNING: Long conversation
```python
# Logged when calculated max_response < minimum_response (500)
# BUT we can still use minimum without exceeding limit
# Action: Consider trimming history proactively
```

#### ERROR: Extremely long conversation
```python
# Logged when even minimum_response would exceed SAFE_ZONE_TOKEN
# Returns whatever tokens available (might be < 500)
# Action: MUST trim conversation history immediately
```

### Formula Reference

```
max_response_tokens = SAFE_ZONE_TOKEN - prompt_tokens - safety_buffer

where:
  SAFE_ZONE_TOKEN = 22,800 (hard limit)
  prompt_tokens = estimate_tokens(prompt)
  safety_buffer = 100 (formatting overhead)
```

### Common Mistakes to Avoid

❌ **WRONG:**
```python
# Fixed max_tokens - DANGEROUS!
max_tokens = 18000
```

✅ **CORRECT:**
```python
# Dynamic max_tokens - SAFE!
max_tokens = calculate_max_response_tokens(prompt, ...)
```

❌ **WRONG:**
```python
# Ignoring conversation history
# Only counting response tokens
```

✅ **CORRECT:**
```python
# Counting TOTAL tokens (prompt + response)
total = prompt_tokens + response_tokens + buffer
assert total <= SAFE_ZONE_TOKEN
```

### Testing Your Code

```python
# Always test with various conversation lengths
test_cases = [
    100,    # Short
    5000,   # Medium
    15000,  # Long
    22000,  # Very long
    22500   # Extreme (edge case)
]

for prompt_tokens in test_cases:
    prompt = "a" * (prompt_tokens * 4)  # Approximate
    max_tokens = calculate_max_response_tokens(prompt, ...)

    total = prompt_tokens + max_tokens + 100
    assert total <= 22800, f"Failed for {prompt_tokens} tokens"
```

### Monitoring in Production

**Log Levels:**
- `INFO`: Normal operation, token allocation
- `WARNING`: Long conversations, approaching limits
- `ERROR`: Critical - conversation too long, needs intervention

**What to Watch:**
```bash
# Grep for warnings
grep "WARNING.*token" backend.log

# Grep for critical errors
grep "ERROR.*CRITICAL.*token" backend.log

# Check token allocation distribution
grep "Token allocation" backend.log | awk '{print $4}' | sort -n
```

### When to Trim Conversation History

Automatically trim when:
1. **Conversation exceeds 18,000 tokens** (proactive)
2. **User receives WARNING log** (reactive)
3. **ERROR log appears** (critical - immediate action required)

Strategies:
- Keep last N messages (sliding window)
- Summarize old messages
- Archive to new conversation

### Quick Checklist

Before deploying code that uses LLM:
- [ ] Uses `calculate_max_response_tokens()` for dynamic limits
- [ ] Passes actual prompt, not placeholder
- [ ] Uses `settings.SAFE_ZONE_TOKEN` constant
- [ ] Has error handling for edge cases
- [ ] Logs token allocation (INFO level)
- [ ] Tests with various conversation lengths
- [ ] Verifies total never exceeds 22,800

### Files to Reference

1. **Implementation:** `backend/app/utils/token_counter.py`
2. **Usage Example:** `backend/app/api/chat.py`
3. **Configuration:** `backend/app/config.py`
4. **Tests:** `backend/tests/test_safe_zone_token_enforcement.py`
5. **Full Guide:** `backend/SAFE_ZONE_TOKEN_FIX_SUMMARY.md`
6. **Visual Guide:** `backend/SAFE_ZONE_TOKEN_VISUAL_GUIDE.md`

### Need Help?

1. Check test suite for examples: `test_safe_zone_token_enforcement.py`
2. Review chat.py for real-world usage
3. Read comprehensive docs: `SAFE_ZONE_TOKEN_FIX_SUMMARY.md`
4. See visual examples: `SAFE_ZONE_TOKEN_VISUAL_GUIDE.md`

### Remember

**SAFE_ZONE_TOKEN is CRITICAL** - it's not a suggestion, it's a hard limit based on extensive testing. Exceeding it causes model failures (hard cliff). Always use dynamic calculation, never fixed values.

**When in doubt:**
- Use `calculate_max_response_tokens()`
- Check the logs
- Run the test suite
- Ask for review

**Status: Production Ready**
