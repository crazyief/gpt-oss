"""
Test TS-011: Cancel SSE Stream Mid-Response

Integration test for canceling an active SSE stream.
Tests against DEPLOYED production backend + REAL llama.cpp service.

Reference: .claude-bus/planning/Stage1-test-scenarios.json lines 539-576
"""

import requests
import json
import time
import threading
from datetime import datetime


def test_ts011_cancel_stream():
    """
    Test TS-011: Cancel SSE stream mid-response

    Acceptance Criteria:
    - llama.cpp generation stopped
    - SSE stream closed gracefully
    - Partial response saved (not lost)
    - Response time < 500ms from cancel to stream close
    """

    print("=" * 70)
    print("TEST TS-011: Cancel SSE Stream Mid-Response")
    print("=" * 70)
    print(f"Test Start Time: {datetime.now().isoformat()}\n")

    # Step 1: Create test project
    print("Step 1: Creating test project...")
    project_response = requests.post(
        "http://localhost:8000/api/projects/create",
        json={
            "name": "SSE Cancellation Test",
            "description": "Testing stream cancellation functionality"
        }
    )

    if project_response.status_code != 201:
        print(f"❌ FAIL: Failed to create project (HTTP {project_response.status_code})")
        print(f"Response: {project_response.text}")
        return False

    project = project_response.json()
    project_id = project["id"]
    print(f"✓ Project created: id={project_id}")

    # Step 2: Create conversation
    print("\nStep 2: Creating conversation...")
    conversation_response = requests.post(
        "http://localhost:8000/api/conversations/create",
        json={
            "project_id": project_id,
            "title": "Stream Cancellation Test"
        }
    )

    if conversation_response.status_code != 201:
        print(f"❌ FAIL: Failed to create conversation (HTTP {conversation_response.status_code})")
        print(f"Response: {conversation_response.text}")
        return False

    conversation = conversation_response.json()
    conversation_id = conversation["id"]
    print(f"✓ Conversation created: id={conversation_id}")

    # Step 3: Start SSE stream and cancel mid-response
    print("\nStep 3: Starting SSE stream (will cancel after receiving some tokens)...")
    print("Message: 'Write a detailed 500-word essay about artificial intelligence'")

    url = "http://localhost:8000/api/chat/stream"
    data = {
        "conversation_id": conversation_id,
        "message": "Write a detailed 500-word essay about artificial intelligence"
    }

    tokens_received = []
    session_id = None
    stream_started = False
    cancel_initiated = False
    cancel_start_time = None
    stream_close_time = None

    try:
        response = requests.post(url, json=data, stream=True, timeout=30)

        if response.status_code != 200:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

        print(f"✓ SSE connection established (HTTP {response.status_code})")

        # Process stream and cancel after receiving ~10 tokens
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')

                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('event')

                        if event_type == 'token':
                            # Extract session_id from first token event
                            if session_id is None:
                                if 'data' in event_data:
                                    session_id = event_data['data'].get('session_id') or event_data['data'].get('message_id')
                                else:
                                    session_id = event_data.get('session_id') or event_data.get('message_id')

                            # Extract token
                            token = event_data.get('token')
                            if token is None and 'data' in event_data:
                                token = event_data['data'].get('token', '')
                            if token is None:
                                token = ''

                            tokens_received.append(token)

                            if not stream_started:
                                stream_started = True
                                print(f"✓ First token received, session_id: {session_id}")

                            # Cancel after receiving 10 tokens
                            if len(tokens_received) == 10 and not cancel_initiated:
                                print(f"\n✓ Received 10 tokens, initiating cancellation...")
                                print(f"Partial response so far: {''.join(tokens_received)}")

                                cancel_initiated = True
                                cancel_start_time = time.time()

                                # Send cancel request in separate thread
                                def send_cancel():
                                    try:
                                        if session_id:
                                            cancel_url = f"http://localhost:8000/api/chat/cancel/{session_id}"
                                            cancel_response = requests.post(cancel_url)
                                            print(f"✓ Cancel request sent (HTTP {cancel_response.status_code})")
                                            if cancel_response.status_code == 200:
                                                print(f"✓ Cancel response: {cancel_response.json()}")
                                        else:
                                            print(f"⚠️ Warning: No session_id available for cancellation")
                                    except Exception as e:
                                        print(f"❌ Cancel request failed: {e}")

                                cancel_thread = threading.Thread(target=send_cancel)
                                cancel_thread.daemon = True
                                cancel_thread.start()

                        elif event_type == 'complete':
                            if cancel_initiated:
                                # Stream completed after cancel - this is unexpected
                                print(f"⚠️ Warning: Received 'complete' event after cancel request")
                            stream_close_time = time.time()
                            break

                        elif event_type == 'cancelled':
                            # Stream cancelled successfully
                            stream_close_time = time.time()
                            print(f"✓ Received 'cancelled' event")
                            break

                        elif event_type == 'error':
                            error_msg = event_data.get('error', event_data.get('data', {}).get('error', 'Unknown error'))
                            stream_close_time = time.time()
                            print(f"✓ Received error event (expected after cancel): {error_msg}")
                            break

                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse event: {line_str}")

            # Break if we've been waiting too long after cancel
            if cancel_initiated and cancel_start_time:
                elapsed = time.time() - cancel_start_time
                if elapsed > 2:  # Wait max 2 seconds after cancel
                    stream_close_time = time.time()
                    print(f"✓ Stream closed after {elapsed:.3f}s (timeout)")
                    break

        # Step 4: Verify acceptance criteria
        print("\n" + "=" * 70)
        print("ACCEPTANCE CRITERIA VALIDATION")
        print("=" * 70)

        criteria_results = []

        # Criterion 1: Stream started
        stream_started_pass = stream_started and len(tokens_received) > 0
        criteria_results.append(stream_started_pass)
        print(f"  [{'✓' if stream_started_pass else '✗'}] Stream started: {len(tokens_received)} tokens received before cancel")

        # Criterion 2: Cancel response time < 500ms
        if cancel_start_time and stream_close_time:
            cancel_latency = stream_close_time - cancel_start_time
            cancel_latency_pass = cancel_latency < 0.5
            criteria_results.append(cancel_latency_pass)
            print(f"  [{'✓' if cancel_latency_pass else '✗'}] Cancel latency < 500ms: {cancel_latency*1000:.1f}ms")
        else:
            print(f"  [✗] Cancel latency: Unable to measure (cancel not initiated or stream not closed)")
            criteria_results.append(False)

        # Criterion 3: Stream closed gracefully
        stream_closed_pass = stream_close_time is not None
        criteria_results.append(stream_closed_pass)
        print(f"  [{'✓' if stream_closed_pass else '✗'}] Stream closed gracefully")

        # Step 5: Verify partial message saved to database
        print("\nStep 5: Verifying partial message saved to database...")
        time.sleep(0.5)  # Wait for database write

        messages_response = requests.get(f"http://localhost:8000/api/messages/{conversation_id}")

        if messages_response.status_code != 200:
            print(f"❌ FAIL: Failed to fetch messages (HTTP {messages_response.status_code})")
            criteria_results.append(False)
        else:
            messages_data = messages_response.json()
            messages = messages_data.get('messages', [])

            # Should have 2 messages: user + partial assistant
            user_msg = next((m for m in messages if m['role'] == 'user'), None)
            assistant_msg = next((m for m in messages if m['role'] == 'assistant'), None)

            user_msg_pass = user_msg is not None
            # Partial assistant message should exist (even if incomplete)
            assistant_msg_pass = assistant_msg is not None

            criteria_results.append(user_msg_pass)
            criteria_results.append(assistant_msg_pass)

            print(f"  [{'✓' if user_msg_pass else '✗'}] User message stored")
            print(f"  [{'✓' if assistant_msg_pass else '✗'}] Partial assistant message saved (not lost)")

            if assistant_msg:
                print(f"\nPartial Assistant Response ({len(assistant_msg['content'])} chars):")
                print(f"  \"{assistant_msg['content']}\"")
                print(f"\nTokens received before cancel: {len(tokens_received)}")
                print(f"Tokens in database: {len(assistant_msg['content'].split())}")

        # Final verdict
        print("\n" + "=" * 70)
        all_passed = all(criteria_results)

        if all_passed:
            print("✅ TEST TS-011: PASSED")
            if cancel_start_time and stream_close_time:
                print(f"Cancel Latency: {(stream_close_time - cancel_start_time)*1000:.1f}ms")
            print(f"Tokens Before Cancel: {len(tokens_received)}")
            print(f"Partial Response Saved: Yes")
        else:
            print("❌ TEST TS-011: FAILED")
            print(f"Failed Criteria: {len([c for c in criteria_results if not c])}/{len(criteria_results)}")

        print("=" * 70)

        return all_passed

    except requests.exceptions.Timeout:
        print(f"❌ FAIL: Request timeout (> 30s)")
        return False
    except Exception as e:
        print(f"❌ FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_ts011_cancel_stream()
    exit(0 if result else 1)
