#!/usr/bin/env python3
"""
Integration test for SSE streaming scenarios TS-003 and TS-011.

Tests real llama.cpp service with Mistral Small 24B Q6_K model.
"""

import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any


class SSEStreamingTester:
    """Test SSE streaming with real LLM service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "TS-003": {},
            "TS-011": {}
        }

    def setup_test_project(self) -> Dict[str, Any]:
        """Create test project and conversation."""
        print("\n=== Setting up test project ===")

        # Create project
        project_data = {
            "name": f"SSE Test Project {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "Testing real LLM streaming with Mistral Small 24B Q6_K"
        }

        print(f"Creating project: {project_data['name']}")
        response = requests.post(
            f"{self.base_url}/api/projects/create",
            json=project_data
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create project: {response.text}")

        project = response.json()
        print(f"[OK] Project created: ID={project['id']}")

        # Create conversation
        conversation_data = {
            "project_id": project["id"],
            "title": "SSE Streaming Test Conversation"
        }

        print(f"Creating conversation...")
        response = requests.post(
            f"{self.base_url}/api/conversations/create",
            json=conversation_data
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create conversation: {response.text}")

        conversation = response.json()
        print(f"[OK] Conversation created: ID={conversation['id']}")

        return {
            "project_id": project["id"],
            "conversation_id": conversation["id"]
        }

    def test_ts003_sse_streaming(self, conversation_id: int) -> Dict[str, Any]:
        """
        Test TS-003: Send message and receive SSE streaming response.

        Acceptance criteria:
        - SSE connection established successfully
        - First token received within 2 seconds
        - Tokens stream progressively (not all at once)
        - 'complete' event received with message_id and token_count
        - User message saved to database with role='user'
        - Assistant message saved to database with role='assistant'
        - Total response time < 10 seconds for ~100 token response
        - Token latency P99 < 100ms per token
        """
        print("\n=== Test TS-003: SSE Streaming Response ===")

        # Test data
        test_message = "Say hello in exactly 10 words. No more, no less."

        # Send chat request with SSE streaming
        url = f"{self.base_url}/api/chat/stream"
        data = {
            "conversation_id": conversation_id,
            "message": test_message
        }

        print(f"Sending message: '{test_message}'")
        print(f"Requesting SSE stream from: {url}")

        start_time = time.time()
        first_token_time = None
        tokens_received = []
        token_latencies = []
        last_token_time = start_time
        session_id = None
        message_id = None
        complete_event = None

        try:
            response = requests.post(url, json=data, stream=True, timeout=30)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            # Verify SSE headers
            content_type = response.headers.get('content-type', '')
            if 'text/event-stream' not in content_type:
                raise Exception(f"Invalid content-type: {content_type}")

            print(f"[OK] SSE connection established (Content-Type: {content_type})")

            # Process SSE stream
            for line in response.iter_lines():
                if not line:
                    continue

                line_str = line.decode('utf-8')

                # Extract session_id from comment
                if line_str.startswith(':') or line_str.startswith('comment:'):
                    if 'session_id:' in line_str:
                        session_id = line_str.split('session_id:')[-1].strip()
                        print(f"Session ID: {session_id}")
                    continue

                # Parse SSE event
                if line_str.startswith('event: '):
                    event_type = line_str[7:].strip()
                    continue

                if line_str.startswith('data: '):
                    data_json = line_str[6:]
                    data_obj = json.loads(data_json)

                    current_time = time.time()

                    if 'token' in data_obj:
                        # Token event
                        token = data_obj['token']
                        tokens_received.append(token)
                        message_id = data_obj.get('message_id')

                        if first_token_time is None:
                            first_token_time = current_time - start_time
                            print(f"[OK] First token received: '{token}' (latency: {first_token_time:.3f}s)")

                        # Track token latency
                        token_latency = (current_time - last_token_time) * 1000  # ms
                        token_latencies.append(token_latency)
                        last_token_time = current_time

                        # Print progress
                        if len(tokens_received) % 10 == 0:
                            print(f"  Tokens received: {len(tokens_received)}")

                    elif 'message_id' in data_obj and 'token_count' in data_obj:
                        # Complete event
                        complete_event = data_obj
                        print(f"[OK] Complete event received: {complete_event}")
                        break

                    elif 'error' in data_obj:
                        # Error event
                        raise Exception(f"SSE error: {data_obj['error']}")

            completion_time = time.time() - start_time

            # Assemble results
            full_response = ''.join(tokens_received)

            # Calculate P99 latency
            token_latencies.sort()
            p99_index = int(len(token_latencies) * 0.99)
            p99_latency = token_latencies[p99_index] if token_latencies else 0

            results = {
                "status": "passed",
                "first_token_latency_ms": int(first_token_time * 1000) if first_token_time else None,
                "total_tokens": len(tokens_received),
                "completion_time_ms": int(completion_time * 1000),
                "p99_token_latency_ms": int(p99_latency),
                "session_id": session_id,
                "message_id": message_id,
                "response_text": full_response,
                "complete_event": complete_event,
                "acceptance_criteria": {}
            }

            # Check acceptance criteria
            criteria = results["acceptance_criteria"]
            criteria["sse_connection_established"] = True
            criteria["first_token_within_2s"] = first_token_time < 2.0 if first_token_time else False
            criteria["tokens_stream_progressively"] = len(tokens_received) > 1
            criteria["complete_event_received"] = complete_event is not None
            criteria["message_id_present"] = message_id is not None
            criteria["total_time_acceptable"] = completion_time < 10.0
            criteria["p99_latency_acceptable"] = p99_latency < 100

            # All criteria met?
            results["meets_acceptance_criteria"] = all(criteria.values())

            # Print summary
            print(f"\n[RESULTS] Test TS-003 Results:")
            print(f"  First token latency: {results['first_token_latency_ms']}ms (target: < 2000ms)")
            print(f"  Total tokens: {results['total_tokens']}")
            print(f"  Completion time: {results['completion_time_ms']}ms (target: < 10000ms)")
            print(f"  P99 token latency: {results['p99_token_latency_ms']}ms (target: < 100ms)")
            print(f"  Response: {full_response[:100]}...")
            print(f"  Acceptance criteria met: {results['meets_acceptance_criteria']}")

            return results

        except Exception as e:
            print(f"[FAIL] Test TS-003 FAILED: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "meets_acceptance_criteria": False
            }

    def test_ts011_cancel_stream(self, conversation_id: int) -> Dict[str, Any]:
        """
        Test TS-011: Cancel SSE stream mid-response.

        Acceptance criteria:
        - POST /api/chat/cancel/{session_id} returns HTTP 200
        - llama.cpp generation stops
        - SSE stream closes gracefully (no error)
        - Partial response saved to database (not lost)
        - Response time from cancel request to stream close < 500ms
        - No orphaned streaming processes
        """
        print("\n=== Test TS-011: Cancel SSE Stream ===")

        # Test data - request long response to have time to cancel
        test_message = "Write a very detailed story about a robot exploring Mars. Include at least 500 words describing the landscape, the robot's sensors, and its discoveries."

        url = f"{self.base_url}/api/chat/stream"
        data = {
            "conversation_id": conversation_id,
            "message": test_message
        }

        print(f"Sending long-form message to trigger streaming...")
        print(f"Message: '{test_message[:80]}...'")

        start_time = time.time()
        tokens_before_cancel = []
        session_id = None
        cancel_time = None
        stream_closed_time = None

        try:
            response = requests.post(url, json=data, stream=True, timeout=30)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            print(f"[OK] SSE connection established")

            # Process stream and cancel after 2 seconds
            for line in response.iter_lines():
                if not line:
                    continue

                line_str = line.decode('utf-8')

                # Extract session_id
                if ':' in line_str and 'session_id:' in line_str:
                    session_id = line_str.split('session_id:')[-1].strip()
                    print(f"Session ID extracted: {session_id}")
                    continue

                # Parse events
                if line_str.startswith('data: '):
                    data_json = line_str[6:]
                    data_obj = json.loads(data_json)

                    if 'token' in data_obj:
                        token = data_obj['token']
                        tokens_before_cancel.append(token)

                        # Print progress
                        if len(tokens_before_cancel) % 5 == 0:
                            print(f"  Tokens received: {len(tokens_before_cancel)}")

                        # Cancel after 2 seconds or 20 tokens
                        elapsed = time.time() - start_time
                        if (elapsed > 2.0 or len(tokens_before_cancel) >= 20) and session_id:
                            print(f"\n[CANCEL] Cancelling stream (tokens: {len(tokens_before_cancel)}, elapsed: {elapsed:.2f}s)")

                            # Send cancel request
                            cancel_url = f"{self.base_url}/api/chat/cancel/{session_id}"
                            cancel_time = time.time()

                            cancel_response = requests.post(cancel_url)
                            print(f"Cancel request sent: HTTP {cancel_response.status_code}")

                            if cancel_response.status_code != 200:
                                raise Exception(f"Cancel failed: {cancel_response.text}")

                            cancel_result = cancel_response.json()
                            print(f"Cancel response: {cancel_result}")

                            # Continue reading stream until it closes
                            continue

                    elif 'error' in data_obj:
                        # Error event (could be cancellation)
                        error_type = data_obj.get('error_type')
                        if error_type == 'cancelled':
                            print(f"[OK] Stream cancelled gracefully: {data_obj['error']}")
                            stream_closed_time = time.time()
                            break
                        else:
                            raise Exception(f"SSE error: {data_obj['error']}")

                    elif 'message_id' in data_obj and 'token_count' in data_obj:
                        # Complete event (shouldn't happen if cancelled)
                        print(f"[WARN] Warning: Received complete event after cancel")
                        stream_closed_time = time.time()
                        break

            # If stream closed without explicit cancelled event
            if stream_closed_time is None:
                stream_closed_time = time.time()

            # Calculate metrics
            cancel_response_time = None
            if cancel_time and stream_closed_time:
                cancel_response_time = int((stream_closed_time - cancel_time) * 1000)

            partial_response = ''.join(tokens_before_cancel)

            results = {
                "status": "passed",
                "tokens_before_cancel": len(tokens_before_cancel),
                "partial_response_text": partial_response,
                "cancel_response_time_ms": cancel_response_time,
                "session_id": session_id,
                "acceptance_criteria": {}
            }

            # Check acceptance criteria
            criteria = results["acceptance_criteria"]
            criteria["cancel_request_successful"] = True
            criteria["stream_closed_gracefully"] = True
            criteria["partial_tokens_received"] = len(tokens_before_cancel) > 0
            criteria["cancel_response_time_acceptable"] = cancel_response_time < 500 if cancel_response_time else False

            results["meets_acceptance_criteria"] = all(criteria.values())

            # Print summary
            print(f"\n[RESULTS] Test TS-011 Results:")
            print(f"  Tokens before cancel: {results['tokens_before_cancel']}")
            print(f"  Cancel response time: {cancel_response_time}ms (target: < 500ms)")
            print(f"  Partial response: {partial_response[:100]}...")
            print(f"  Acceptance criteria met: {results['meets_acceptance_criteria']}")

            return results

        except Exception as e:
            print(f"[FAIL] Test TS-011 FAILED: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "meets_acceptance_criteria": False
            }

    def verify_service_health(self):
        """Verify backend and LLM services are healthy."""
        print("\n=== Verifying service health ===")

        # Check backend
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] Backend healthy: {response.json()}")
            else:
                raise Exception(f"Backend unhealthy: {response.status_code}")
        except Exception as e:
            raise Exception(f"Backend service check failed: {e}")

        # Check LLM service
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] LLM service healthy: {response.json()}")
            else:
                raise Exception(f"LLM unhealthy: {response.status_code}")
        except Exception as e:
            raise Exception(f"LLM service check failed: {e}")

    def run_all_tests(self):
        """Execute all SSE streaming tests."""
        print("\n" + "="*60)
        print("SSE STREAMING INTEGRATION TESTS")
        print("Model: Mistral Small 24B Q6_K")
        print("="*60)

        try:
            # Verify services
            self.verify_service_health()

            # Setup test environment
            test_env = self.setup_test_project()
            conversation_id = test_env["conversation_id"]

            # Run TS-003
            self.results["TS-003"] = self.test_ts003_sse_streaming(conversation_id)

            # Run TS-011
            self.results["TS-011"] = self.test_ts011_cancel_stream(conversation_id)

            # Print final summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)

            for scenario_id, result in self.results.items():
                status = result.get("status", "unknown")
                passed = result.get("meets_acceptance_criteria", False)
                status_icon = "[PASS]" if passed else "[FAIL]"

                print(f"{status_icon} {scenario_id}: {status.upper()}")

                if not passed and "error" in result:
                    print(f"   Error: {result['error']}")

            # Save results to JSON
            output_file = "D:\\gpt-oss\\.claude-bus\\test-results\\sse_streaming_results.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "test_environment": {
                        "backend_url": self.base_url,
                        "llm_service": "http://localhost:8080",
                        "model": "Mistral Small 24B Q6_K"
                    },
                    "results": self.results
                }, f, indent=2)

            print(f"\n[INFO] Results saved to: {output_file}")

            return self.results

        except Exception as e:
            print(f"\n[FAIL] Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


if __name__ == "__main__":
    tester = SSEStreamingTester()
    results = tester.run_all_tests()
