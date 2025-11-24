"""
Test TS-003: Send Message and Receive SSE Streaming Response

Integration test for real-time LLM streaming via SSE.
Tests against DEPLOYED production backend + REAL llama.cpp service.

Reference: .claude-bus/planning/Stage1-test-scenarios.json lines 170-229
"""

import requests
import json
import time
from datetime import datetime


def test_ts003_sse_streaming():
    """
    Test TS-003: SSE streaming with real LLM service

    Acceptance Criteria:
    - User message stored in database with role = 'user'
    - SSE connection established (HTTP 200, content-type: text/event-stream)
    - Token events received and displayed progressively
    - Complete event received with message_id and token_count
    - Assistant message stored in database with role = 'assistant'
    - Total response time < 10 seconds for ~100 token response
    - First token latency < 2 seconds
    """

    print("=" * 70)
    print("TEST TS-003: Send Message and Receive SSE Streaming Response")
    print("=" * 70)
    print(f"Test Start Time: {datetime.now().isoformat()}\n")

    # Step 1: Create test project
    print("Step 1: Creating test project...")
    project_response = requests.post(
        "http://localhost:8000/api/projects/create",
        json={
            "name": "SSE Integration Test",
            "description": "Testing real-time LLM streaming with deployed backend"
        }
    )

    if project_response.status_code != 201:
        print(f"[ERROR] FAIL: Failed to create project (HTTP {project_response.status_code})")
        print(f"Response: {project_response.text}")
        return False

    project = project_response.json()
    project_id = project["id"]
    print(f"[OK] Project created: id={project_id}, name='{project['name']}'")

    # Step 2: Create conversation
    print("\nStep 2: Creating conversation...")
    conversation_response = requests.post(
        "http://localhost:8000/api/conversations/create",
        json={
            "project_id": project_id,
            "title": "SSE Streaming Test Conversation"
        }
    )

    if conversation_response.status_code != 201:
        print(f"[ERROR] FAIL: Failed to create conversation (HTTP {conversation_response.status_code})")
        print(f"Response: {conversation_response.text}")
        return False

    conversation = conversation_response.json()
    conversation_id = conversation["id"]
    print(f"[OK] Conversation created: id={conversation_id}, title='{conversation['title']}'")

    # Step 3: Test SSE streaming with real LLM
    print("\nStep 3: Testing SSE streaming with real LLM...")
    print("Message: 'Say hello in exactly 10 words'")

    url = "http://localhost:8000/api/chat/stream"
    data = {
        "conversation_id": conversation_id,
        "message": "Say hello in exactly 10 words"
    }

    tokens_received = []
    start_time = time.time()
    first_token_time = None
    message_id = None
    token_count = None
    completion_time = None

    try:
        response = requests.post(url, json=data, stream=True, timeout=30)

        if response.status_code != 200:
            print(f"[ERROR] FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

        # Verify content-type
        content_type = response.headers.get('content-type', '')
        if 'text/event-stream' not in content_type:
            print(f"[ERROR] FAIL: Wrong content-type: {content_type}")
            print(f"Expected: text/event-stream")
            return False

        print(f"[OK] SSE connection established (HTTP {response.status_code}, content-type: {content_type})")

        # Process SSE stream
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')

                # SSE format: "data: {json}"
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('event')

                        if event_type == 'token':
                            # Extract token from different possible structures
                            token = event_data.get('token')
                            if token is None and 'data' in event_data:
                                token = event_data['data'].get('token', '')
                            if token is None:
                                token = ''

                            tokens_received.append(token)

                            if first_token_time is None:
                                first_token_time = time.time() - start_time
                                print(f"[OK] First token received: {first_token_time:.3f}s (target: < 2s)")

                        elif event_type == 'complete':
                            # Extract completion data
                            if 'data' in event_data:
                                message_id = event_data['data'].get('message_id')
                                token_count = event_data['data'].get('token_count')
                            else:
                                message_id = event_data.get('message_id')
                                token_count = event_data.get('token_count')

                            completion_time = time.time() - start_time
                            print(f"[OK] Complete event received")
                            break

                        elif event_type == 'error':
                            error_msg = event_data.get('error', event_data.get('data', {}).get('error', 'Unknown error'))
                            print(f"[ERROR] FAIL: Error event received: {error_msg}")
                            return False

                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse event: {line_str}")

        # Step 4: Verify acceptance criteria
        print("\n" + "=" * 70)
        print("ACCEPTANCE CRITERIA VALIDATION")
        print("=" * 70)

        criteria_results = []

        # Criterion 1: First token < 2s
        first_token_pass = first_token_time and first_token_time < 2
        criteria_results.append(first_token_pass)
        print(f"  [{'PASS' if first_token_pass else 'FAIL'}] First token < 2s: {first_token_time:.3f}s")

        # Criterion 2: Tokens received
        tokens_pass = len(tokens_received) > 0
        criteria_results.append(tokens_pass)
        print(f"  [{'PASS' if tokens_pass else 'FAIL'}] Tokens received: {len(tokens_received)}")

        # Criterion 3: message_id received
        message_id_pass = message_id is not None
        criteria_results.append(message_id_pass)
        print(f"  [{'PASS' if message_id_pass else 'FAIL'}] message_id received: {message_id}")

        # Criterion 4: token_count received
        token_count_pass = token_count is not None
        criteria_results.append(token_count_pass)
        print(f"  [{'PASS' if token_count_pass else 'FAIL'}] token_count received: {token_count}")

        # Criterion 5: Total response time < 10s
        completion_time_pass = completion_time and completion_time < 10
        criteria_results.append(completion_time_pass)
        print(f"  [{'PASS' if completion_time_pass else 'FAIL'}] Total response time < 10s: {completion_time:.3f}s")

        # Criterion 6: SSE connection established
        sse_pass = True
        criteria_results.append(sse_pass)
        print(f"  [PASS] SSE connection established (text/event-stream)")

        # Step 5: Verify message stored in database
        print("\nStep 5: Verifying messages stored in database...")
        messages_response = requests.get(f"http://localhost:8000/api/messages/{conversation_id}")

        if messages_response.status_code != 200:
            print(f"[ERROR] FAIL: Failed to fetch messages (HTTP {messages_response.status_code})")
            criteria_results.append(False)
        else:
            messages_data = messages_response.json()
            messages = messages_data.get('messages', [])

            # Should have 2 messages: user + assistant
            user_msg = next((m for m in messages if m['role'] == 'user'), None)
            assistant_msg = next((m for m in messages if m['role'] == 'assistant'), None)

            user_msg_pass = user_msg is not None and user_msg['content'] == "Say hello in exactly 10 words"
            assistant_msg_pass = assistant_msg is not None and len(assistant_msg['content']) > 0

            criteria_results.append(user_msg_pass)
            criteria_results.append(assistant_msg_pass)

            print(f"  [{'PASS' if user_msg_pass else 'FAIL'}] User message stored with role='user'")
            print(f"  [{'PASS' if assistant_msg_pass else 'FAIL'}] Assistant message stored with role='assistant'")

            if assistant_msg:
                print(f"\nAssistant Response ({len(assistant_msg['content'])} chars):")
                print(f"  \"{assistant_msg['content']}\"")

        # Reconstruct full response from tokens
        response_text = ''.join(tokens_received)
        print(f"\nStreamed Response Reconstruction ({len(response_text)} chars):")
        print(f"  \"{response_text}\"")

        # Final verdict
        print("\n" + "=" * 70)
        all_passed = all(criteria_results)

        if all_passed:
            print("✅ TEST TS-003: PASSED")
            print(f"Test Duration: {completion_time:.3f}s")
            print(f"Tokens Received: {len(tokens_received)}")
            print(f"First Token Latency: {first_token_time:.3f}s")
            print(f"Average Token Latency: {(completion_time / len(tokens_received) * 1000):.1f}ms" if len(tokens_received) > 0 else "N/A")
        else:
            print("[ERROR] TEST TS-003: FAILED")
            print(f"Failed Criteria: {len([c for c in criteria_results if not c])}/{len(criteria_results)}")

        print("=" * 70)

        return all_passed

    except requests.exceptions.Timeout:
        print(f"[ERROR] FAIL: Request timeout (> 30s)")
        return False
    except Exception as e:
        print(f"[ERROR] FAIL: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_ts003_sse_streaming()
    exit(0 if result else 1)
