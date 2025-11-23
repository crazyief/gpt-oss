# BUG-001 Fix Report: Follow-up Messages Return Empty Responses

**Status**: FIXED
**Severity**: CRITICAL (Stage 1 blocker)
**Fixed by**: Backend-Agent
**Date**: 2025-11-23

## Problem Summary

Users could send first message successfully, but all follow-up messages in the same conversation returned empty responses. The SSE stream completed in ~70-700ms with 0 tokens generated.

### Symptoms
- First message: Works perfectly, LLM generates normal response
- Follow-up message: Completes in <1s with empty content
- SSE stream: Returns 200 status (no network errors)
- Database: Assistant message has empty content field
- No console errors or exceptions

## Root Cause Analysis

### Issue 1: Empty Assistant Message in History

**File**: `backend/app/services/message_service.py`

The `get_conversation_history()` function retrieved ALL messages including the current assistant message placeholder (which has `content=""`). This empty assistant message was being included in the conversation history sent to the LLM.

**Impact**: LLM received conversation history with empty "Assistant: " entries, confusing the model.

### Issue 2: Missing "Assistant:" Prompt Suffix

**File**: `backend/app/services/llm_service.py`

The `build_chat_prompt()` function formatted conversation history but did NOT append "Assistant:" at the end when the last message was from the user.

**Impact**: The prompt ended with:
```
User: What is IEC 62443?
Assistant: [response]
User: Can you list the key parts?
```

Without the trailing "Assistant:", the LLM didn't know it should generate a response. The LLM saw this as an incomplete conversation and stopped generating (returning empty output).

### Issue 3: Duplicate User Message

**File**: `backend/app/api/chat.py`

The code was appending the current user message to the history even though it was already in the database (created in `initiate_stream`).

**Impact**: LLM received duplicate user messages in the prompt, further confusing the context.

## Fix Implementation

### Fix 1: Filter Empty Messages + Exclude Current Assistant

**File**: `backend/app/services/message_service.py`

```python
@staticmethod
def get_conversation_history(
    db: Session,
    conversation_id: int,
    max_messages: int = 10,
    exclude_message_id: Optional[int] = None  # NEW PARAMETER
) -> list[dict]:
    # Build query - exclude specified message if provided
    where_conditions = [Message.conversation_id == conversation_id]
    if exclude_message_id is not None:
        where_conditions.append(Message.id != exclude_message_id)  # EXCLUDE PLACEHOLDER

    # ... query logic ...

    # Filter out empty content messages
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
        if msg.content and msg.content.strip()  # FILTER EMPTY
    ]
```

### Fix 2: Add "Assistant:" Prompt Suffix

**File**: `backend/app/services/llm_service.py`

```python
def build_chat_prompt(self, messages: list[dict]) -> str:
    # Format each message
    formatted = []
    for msg in messages:
        role = msg["role"].capitalize()
        content = msg["content"]
        formatted.append(f"{role}: {content}")

    prompt = "\n\n".join(formatted)

    # CRITICAL FIX: Add "Assistant:" prompt if last message was from user
    if messages and messages[-1]["role"] == "user":
        prompt += "\n\nAssistant:"  # Signal LLM to generate response

    return prompt
```

### Fix 3: Remove Duplicate User Message

**File**: `backend/app/api/chat.py`

```python
# Get conversation history (user message already in DB)
history = MessageService.get_conversation_history(
    db,
    conversation_id,
    max_messages=10,
    exclude_message_id=assistant_message_id  # Exclude current placeholder
)

# REMOVED: history.append({"role": "user", "content": user_message})
# User message is already in database, no need to append

# Build prompt from history
prompt = llm_service.build_chat_prompt(history)
```

### Fix 4: Add Diagnostic Logging

**File**: `backend/app/api/chat.py`

```python
logger.info(
    f"Building LLM prompt for conversation {conversation_id}: "
    f"{len(history)} messages in history, "
    f"assistant_message_id={assistant_message_id}"
)
logger.debug(f"Conversation history: {history}")
logger.debug(f"Full prompt (first 500 chars): {prompt[:500]}")
```

## Testing

### Test Script

Created `test_follow_up_messages.py` that:
1. Creates new conversation
2. Sends first message and verifies response
3. Sends follow-up message and verifies response (was broken)
4. Checks database to confirm content is saved

### Test Results

```
[PASS] TEST PASSED: BUG-001 IS FIXED!

Summary:
  - First message worked: 474 chars
  - Follow-up message worked: 1456 chars
  - Database content verified: All messages have content
```

**Before Fix**:
- First message: 465 chars (PASS)
- Follow-up message: 0 chars in 73ms (FAIL)

**After Fix**:
- First message: 474 chars (PASS)
- Follow-up message: 1456 chars in 5084ms (PASS)

## Files Changed

1. `backend/app/services/message_service.py`
   - Added `exclude_message_id` parameter to `get_conversation_history()`
   - Added filter to exclude messages with empty content
   - Added documentation explaining why exclusion is needed

2. `backend/app/services/llm_service.py`
   - Modified `build_chat_prompt()` to append "Assistant:" when last message is from user
   - Added comprehensive documentation explaining prompt format requirements

3. `backend/app/api/chat.py`
   - Removed duplicate user message append (already in DB)
   - Pass `assistant_message_id` to exclude current placeholder from history
   - Added debug logging for conversation context

4. `test_follow_up_messages.py` (NEW)
   - Automated test to verify follow-up messages work correctly
   - Validates both streaming and database persistence

## Verification Checklist

- [x] First message still works (no regression)
- [x] Follow-up messages receive non-empty LLM responses
- [x] Database shows content for all assistant messages
- [x] SSE streaming continues to work properly
- [x] Messages persist correctly after streaming
- [x] No performance degradation
- [x] Logging provides visibility into conversation context

## Impact

**Severity**: CRITICAL - Blocking Stage 1 approval

**User Impact**:
- Users can now have multi-turn conversations
- Follow-up questions receive proper LLM responses
- Conversation history is maintained correctly

**Technical Impact**:
- Conversation context pipeline now properly excludes empty placeholder messages
- LLM prompt format correctly signals when assistant should respond
- No duplicate messages in conversation history

## Next Steps

1. Run full integration test suite (TS-003 through TS-011)
2. Verify no regressions in other test cases
3. Update QA-Agent to re-test all scenarios
4. Ready for Stage 1 final approval

## Lessons Learned

1. **Prompt engineering matters**: LLMs need explicit signals (like "Assistant:") to know when to generate
2. **Database timing**: Messages created before streaming must be excluded from history
3. **Empty content filtering**: Placeholder messages with `content=""` should never be sent to LLM
4. **Logging is essential**: Debug logs revealed the exact prompt being sent, making diagnosis possible

## Related Issues

- Bug 3 (fixed in commit f982f5c): Messages disappearing after streaming
- This fix does NOT reintroduce Bug 3 - streaming content merge still works correctly
