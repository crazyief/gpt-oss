# BUG REPORT: SSE Streaming Endpoint (/api/chat/stream)

**Bug ID**: BUG-SSE-001
**Severity**: CRITICAL
**Discovered By**: QA-Agent during TS-003 integration testing
**Discovery Date**: 2025-11-18T11:23:00+08:00
**Status**: BLOCKED - TS-003 and TS-011 cannot proceed

---

## Summary

The `/api/chat/stream` endpoint returns HTTP 500 error due to Pydantic validation failure. The backend code is attempting to create a `MessageCreate` object with empty `content` field, violating the minLength=1 constraint.

---

## Error Details

**HTTP Status**: 500 Internal Server Error

**Stack Trace**:
```
File "/app/app/api/chat.py", line 102, in stream_chat
    MessageCreate(
pydantic_core._pydantic_core.ValidationError: 1 validation error for MessageCreate
content
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
```

**API Endpoint**: `POST /api/chat/stream`

**Request Body** (valid according to schema):
```json
{
  "conversation_id": 2,
  "message": "Say hello in exactly 10 words"
}
```

**Expected Behavior**:
- User message should be saved to database with content = "Say hello in exactly 10 words"
- SSE stream should initiate
- Tokens should be streamed from LLM

**Actual Behavior**:
- HTTP 500 error before SSE stream starts
- User message NOT saved to database
- No tokens received

---

## Root Cause Analysis

The backend code at `/app/app/api/chat.py:102` is creating `MessageCreate` with:
- `content=''` (empty string) instead of `content=request.message`

This suggests the code is not correctly mapping the `ChatStreamRequest.message` field to `MessageCreate.content`.

**Likely Code Issue**:
```python
# WRONG (current):
MessageCreate(
    conversation_id=request.conversation_id,
    role="user",
    content=""  # Empty string!
)

# CORRECT (expected):
MessageCreate(
    conversation_id=request.conversation_id,
    role="user",
    content=request.message  # User's message
)
```

---

## Impact

**Blocked Test Scenarios**:
- TS-003: Send message and receive SSE streaming response (CRITICAL)
- TS-011: Cancel SSE stream mid-response (MEDIUM)

**Stage 1 Completion**:
- Cannot achieve 100% test coverage (currently 14/16 = 87.5%)
- Manual approval (Phase 5) blocked until this is fixed

**User Impact**:
- **CHAT FUNCTIONALITY COMPLETELY BROKEN**
- Users cannot send messages
- Frontend UI cannot communicate with LLM
- Core feature non-functional

---

## Reproduction Steps

1. Start backend: `docker-compose up backend`
2. Verify llama.cpp running: `curl http://localhost:8080/health` → `{"status":"ok"}`
3. Create conversation:
   ```bash
   curl -X POST http://localhost:8000/api/conversations/create \
     -H "Content-Type: application/json" \
     -d '{"project_id": 1, "title": "Test"}'
   ```
4. Attempt to send message:
   ```bash
   curl -X POST http://localhost:8000/api/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"conversation_id": 1, "message": "Hello"}'
   ```
5. **Result**: HTTP 500 with Pydantic validation error

---

## Recommended Fix

**Root Cause**: The `MessageCreate` schema has `min_length=1` for the `content` field, but the code at `chat.py:105` tries to create an assistant message placeholder with `content=""` (empty string).

**File 1**: `D:\gpt-oss\backend\app\schemas\message.py`
**Line**: 48-52

**Option A (Recommended)**: Allow empty content for assistant message placeholders
```python
class MessageCreate(BaseModel):
    """
    Schema for creating a new message.

    Used internally by the chat endpoint.
    """
    conversation_id: int = Field(
        ...,
        gt=0,
        description="Conversation ID to add message to"
    )
    role: Literal["user", "assistant"] = Field(
        ...,
        description="Message role"
    )
    content: str = Field(
        ...,
        min_length=0,  # FIX: Change from 1 to 0 to allow empty placeholder
        description="Message content (can be empty for assistant placeholders)"
    )
    parent_message_id: Optional[int] = Field(
        None,
        gt=0,
        description="Parent message ID (for regeneration)"
    )
```

**Option B**: Don't create assistant message placeholder upfront
- Remove lines 97-108 from `chat.py`
- Create assistant message only AFTER first token arrives
- **Trade-off**: More complex streaming logic, but stricter validation

**Testing After Fix**:
1. Restart backend: `docker-compose restart backend`
2. Re-run TS-003 test: `python .claude-bus/test-results/test_ts003_sse_streaming.py`
3. Expected result: Test should PASS with tokens streaming correctly

---

## Verification Checklist

After fix is applied:
- [ ] Backend builds without errors
- [ ] Health endpoint still returns 200
- [ ] User message saved to database with correct content
- [ ] SSE stream initiates successfully
- [ ] Tokens received from LLM
- [ ] Complete event sent with message_id
- [ ] TS-003 test passes (all acceptance criteria met)
- [ ] TS-011 test can proceed

---

## Related Files

**Backend Code**:
- `D:\gpt-oss\backend\app\api\chat.py` (contains bug)
- `D:\gpt-oss\backend\app\schemas\message.py` (MessageCreate schema)
- `D:\gpt-oss\backend\app\schemas\chat.py` (ChatStreamRequest schema)

**Test Files**:
- `D:\gpt-oss\.claude-bus\test-results\test_ts003_sse_streaming.py`
- `D:\gpt-oss\.claude-bus\test-results\test_ts011_cancel_stream.py`

**Logs**:
- `docker logs gpt-oss-backend` (shows full stack trace)

---

## Escalation

**Assigned To**: PM-Architect-Agent (requires code review and deployment approval)

**Priority**: **CRITICAL** - Blocks Stage 1 completion

**Next Steps**:
1. PM-Architect reviews this bug report
2. PM-Architect inspects `backend/app/api/chat.py:102`
3. PM-Architect applies fix
4. Create new git checkpoint after fix
5. Restart backend container
6. QA-Agent re-runs TS-003 and TS-011 tests
7. If tests pass: Proceed to Phase 5 (Manual Approval)

---

**Generated By**: QA-Agent
**Report Date**: 2025-11-18T11:23:00+08:00
**Test Session**: Stage 1 Phase 4 Integration Testing
