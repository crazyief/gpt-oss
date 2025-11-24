"""
Test script to verify BUG-001 fix: Follow-up messages should return non-empty responses.

This script:
1. Creates a new conversation
2. Sends first message and verifies response
3. Sends follow-up message and verifies response (THIS WAS BROKEN)
4. Checks database to confirm content is saved
"""

import httpx
import asyncio
import json
import sqlite3
from datetime import datetime


async def test_follow_up_messages():
    """Test that follow-up messages receive proper LLM responses."""

    base_url = "http://localhost:8000"

    print("=" * 80)
    print("BUG-001 Fix Verification Test")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create a new conversation
        print("\n[1] Creating new conversation...")
        resp = await client.post(
            f"{base_url}/api/conversations/create",
            json={"title": "BUG-001 Fix Test", "project_id": None}
        )
        if resp.status_code not in (200, 201):
            print(f"Failed to create conversation: {resp.status_code} - {resp.text}")
            assert False
        conversation = resp.json()
        conversation_id = conversation["id"]
        print(f"[OK] Created conversation ID: {conversation_id}")

        # Step 2: Send first message
        print("\n[2] Sending first message...")
        first_message = "What is IEC 62443?"
        resp = await client.post(
            f"{base_url}/api/chat/stream",
            json={"conversation_id": conversation_id, "message": first_message}
        )
        if resp.status_code != 200:
            print(f"Failed to initiate stream: {resp.status_code} - {resp.text}")
            assert False
        session_data = resp.json()
        session_id = session_data["session_id"]
        first_assistant_id = session_data["message_id"]
        print(f"[OK] Initiated stream, session_id: {session_id}")
        print(f"  Assistant message ID: {first_assistant_id}")

        # Step 3: Consume first SSE stream
        print("\n[3] Consuming first message stream...")
        first_response_tokens = []
        async with client.stream("GET", f"{base_url}/api/chat/stream/{session_id}") as stream:
            async for line in stream.aiter_lines():
                if not line:
                    continue
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    continue
                if line.startswith("data:"):
                    data_json = line.split(":", 1)[1].strip()
                    data = json.loads(data_json)
                    if event_type == "token":
                        first_response_tokens.append(data["token"])
                    elif event_type == "complete":
                        print(f"[OK] First message complete: {data['token_count']} tokens, {data['completion_time_ms']}ms")
                        break

        first_response = "".join(first_response_tokens)
        print(f"  First response length: {len(first_response)} chars")
        print(f"  Preview: {first_response[:100]}...")

        # Verify first response is not empty
        assert len(first_response) > 10, f"First response is too short or empty: '{first_response}'"
        print("[OK] First message response is valid")

        # Step 4: Send follow-up message (THIS WAS THE BUG!)
        print("\n[4] Sending follow-up message...")
        follow_up_message = "Can you list the key parts of this standard?"
        resp = await client.post(
            f"{base_url}/api/chat/stream",
            json={"conversation_id": conversation_id, "message": follow_up_message}
        )
        if resp.status_code != 200:
            print(f"Failed to initiate follow-up stream: {resp.status_code} - {resp.text}")
            assert False
        session_data = resp.json()
        session_id = session_data["session_id"]
        follow_up_assistant_id = session_data["message_id"]
        print(f"[OK] Initiated follow-up stream, session_id: {session_id}")
        print(f"  Assistant message ID: {follow_up_assistant_id}")

        # Step 5: Consume follow-up SSE stream
        print("\n[5] Consuming follow-up message stream...")
        follow_up_tokens = []
        async with client.stream("GET", f"{base_url}/api/chat/stream/{session_id}") as stream:
            async for line in stream.aiter_lines():
                if not line:
                    continue
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    continue
                if line.startswith("data:"):
                    data_json = line.split(":", 1)[1].strip()
                    data = json.loads(data_json)
                    if event_type == "token":
                        follow_up_tokens.append(data["token"])
                    elif event_type == "complete":
                        print(f"[OK] Follow-up complete: {data['token_count']} tokens, {data['completion_time_ms']}ms")
                        break
                    elif event_type == "error":
                        print(f"[X] ERROR: {data}")
                        assert False, f"Stream error: {data}"

        follow_up_response = "".join(follow_up_tokens)
        print(f"  Follow-up response length: {len(follow_up_response)} chars")
        print(f"  Preview: {follow_up_response[:100]}...")

        # CRITICAL: Verify follow-up response is not empty (this was the bug)
        assert len(follow_up_response) > 10, f"[FAIL] BUG NOT FIXED: Follow-up response is empty or too short: '{follow_up_response}'"
        print("[OK] Follow-up message response is valid (BUG FIXED!)")

        # Step 6: Verify database content
        print("\n[6] Verifying database content...")
        conn = sqlite3.connect("data/gpt_oss.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, length(content) as content_len, substr(content, 1, 60) as preview "
            "FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,)
        )
        rows = cursor.fetchall()
        print("\n  Database messages:")
        for row in rows:
            msg_id, role, content_len, preview = row
            print(f"    ID={msg_id:3d} | {role:9s} | len={content_len:4d} | {preview}")
        conn.close()

        # Verify all messages have content
        for row in rows:
            msg_id, role, content_len, preview = row
            if role == "assistant":
                assert content_len > 0, f"[FAIL] Assistant message {msg_id} has empty content in database!"

        print("\n[OK] All database messages have content")

    print("\n" + "=" * 80)
    print("[PASS] TEST PASSED: BUG-001 IS FIXED!")
    print("=" * 80)
    print("\nSummary:")
    print(f"  - First message worked: {len(first_response)} chars")
    print(f"  - Follow-up message worked: {len(follow_up_response)} chars")
    print(f"  - Database content verified: All messages have content")
    print("\nFix details:")
    print("  - Modified: backend/app/services/message_service.py")
    print("    - Added exclude_message_id parameter to get_conversation_history()")
    print("    - Added filter to exclude empty content messages")
    print("  - Modified: backend/app/api/chat.py")
    print("    - Pass assistant_message_id to exclude current placeholder")
    print("    - Added debug logging for conversation context")


if __name__ == "__main__":
    asyncio.run(test_follow_up_messages())
