"""
End-to-End Workflow Test
Tests complete user journey: Project → Conversation → Message → SSE Streaming → Database Persistence
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

class E2ETestRunner:
    def __init__(self):
        self.results = {
            "steps_executed": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "errors": [],
            "timings": {},
            "data_created": {}
        }

    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")

    def run_test(self, step_name, test_func):
        """Execute a test step and track results"""
        self.results["steps_executed"] += 1
        self.log(f"Step {self.results['steps_executed']}: {step_name}")

        start = time.time()
        try:
            test_func()
            elapsed = (time.time() - start) * 1000
            self.results["steps_passed"] += 1
            self.results["timings"][step_name] = elapsed
            self.log(f"✓ PASSED ({elapsed:.2f}ms)", "SUCCESS")
            return True
        except Exception as e:
            self.results["steps_failed"] += 1
            self.results["errors"].append({
                "step": step_name,
                "error": str(e)
            })
            self.log(f"✗ FAILED: {str(e)}", "ERROR")
            return False

    def test_create_project(self):
        """Step 1: Create project via API"""
        response = requests.post(
            f"{BASE_URL}/api/projects/create",
            json={
                "name": "E2E Test Project",
                "description": "End-to-end testing workflow"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Response missing 'id' field"
        assert data["name"] == "E2E Test Project", "Project name mismatch"

        self.results["data_created"]["project_id"] = data["id"]
        self.log(f"  Created project ID: {data['id']}")

    def test_create_conversation(self):
        """Step 2: Create conversation"""
        project_id = self.results["data_created"]["project_id"]
        response = requests.post(
            f"{BASE_URL}/api/conversations/create",
            json={
                "project_id": project_id,
                "title": "E2E Chat Test"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Response missing 'id' field"
        assert data["title"] == "E2E Chat Test", "Conversation title mismatch"

        self.results["data_created"]["conversation_id"] = data["id"]
        self.log(f"  Created conversation ID: {data['id']}")

    def test_send_message_with_streaming(self):
        """Step 3: Send message with SSE streaming"""
        conversation_id = self.results["data_created"]["conversation_id"]

        response = requests.post(
            f"{BASE_URL}/api/chat/stream",
            json={
                "conversation_id": conversation_id,
                "message": "Say hello in exactly 5 words"
            },
            stream=True,
            timeout=30
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/event-stream" in response.headers.get("content-type", ""), \
            "Expected SSE content-type"

        tokens = []
        first_token_time = None
        stream_start = time.time()
        user_message_id = None
        assistant_message_id = None

        for line in response.iter_lines():
            if line and line.startswith(b'data: '):
                event_data = json.loads(line[6:])
                event_type = event_data.get('event')

                if event_type == 'start':
                    user_message_id = event_data.get('user_message_id')
                    assistant_message_id = event_data.get('assistant_message_id')
                    self.log(f"  Stream started: user_msg={user_message_id}, asst_msg={assistant_message_id}")

                elif event_type == 'token':
                    token = event_data.get('token', '')
                    tokens.append(token)
                    if first_token_time is None:
                        first_token_time = (time.time() - stream_start) * 1000
                        self.log(f"  First token received: {first_token_time:.2f}ms")

                elif event_type == 'complete':
                    total_time = (time.time() - stream_start) * 1000
                    full_response = ''.join(tokens)
                    self.log(f"  Stream complete: {len(tokens)} tokens in {total_time:.2f}ms")
                    self.log(f"  Response: {full_response}")
                    break

        assert first_token_time is not None, "No tokens received"
        assert first_token_time < 5000, f"First token too slow: {first_token_time}ms (expected < 5000ms)"
        assert len(tokens) > 0, "No tokens received"
        assert user_message_id is not None, "Missing user_message_id"
        assert assistant_message_id is not None, "Missing assistant_message_id"

        self.results["timings"]["first_token_latency_ms"] = first_token_time
        self.results["timings"]["total_stream_time_ms"] = total_time
        self.results["data_created"]["user_message_id"] = user_message_id
        self.results["data_created"]["assistant_message_id"] = assistant_message_id
        self.results["data_created"]["response_text"] = ''.join(tokens)

    def test_verify_database_persistence(self):
        """Step 4: Verify messages saved to database"""
        conversation_id = self.results["data_created"]["conversation_id"]

        response = requests.get(
            f"{BASE_URL}/api/messages/list",
            params={"conversation_id": conversation_id}
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "messages" in data, "Response missing 'messages' field"

        messages = data["messages"]
        assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"

        # Verify user message
        user_msg = messages[0]
        assert user_msg["role"] == "user", "First message should be user role"
        assert user_msg["content"] == "Say hello in exactly 5 words", "User message content mismatch"

        # Verify assistant message
        asst_msg = messages[1]
        assert asst_msg["role"] == "assistant", "Second message should be assistant role"
        assert len(asst_msg["content"]) > 0, "Assistant message is empty"

        self.log(f"  Verified {len(messages)} messages in database")
        self.log(f"  User: {user_msg['content']}")
        self.log(f"  Assistant: {asst_msg['content']}")

    def test_cors_headers(self):
        """Step 5: Verify CORS headers present"""
        response = requests.options(
            f"{BASE_URL}/api/projects/create",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        # CORS preflight should return 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        headers = response.headers
        assert "access-control-allow-origin" in headers, "Missing CORS origin header"
        assert "access-control-allow-methods" in headers, "Missing CORS methods header"

        self.log(f"  CORS Origin: {headers.get('access-control-allow-origin')}")
        self.log(f"  CORS Methods: {headers.get('access-control-allow-methods')}")

    def run_all(self):
        """Execute all E2E tests"""
        print("\n" + "="*60)
        print("E2E WORKFLOW TEST SUITE")
        print("="*60 + "\n")

        tests = [
            ("Create Project", self.test_create_project),
            ("Create Conversation", self.test_create_conversation),
            ("Send Message with SSE Streaming", self.test_send_message_with_streaming),
            ("Verify Database Persistence", self.test_verify_database_persistence),
            ("Verify CORS Headers", self.test_cors_headers)
        ]

        for step_name, test_func in tests:
            if not self.run_test(step_name, test_func):
                # Stop on first failure
                break

        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Steps Executed: {self.results['steps_executed']}")
        print(f"Steps Passed:   {self.results['steps_passed']}")
        print(f"Steps Failed:   {self.results['steps_failed']}")

        if self.results["steps_failed"] > 0:
            print("\nERRORS:")
            for error in self.results["errors"]:
                print(f"  - {error['step']}: {error['error']}")

        if "first_token_latency_ms" in self.results["timings"]:
            print(f"\nPERFORMANCE:")
            print(f"  First Token:  {self.results['timings']['first_token_latency_ms']:.2f}ms")
            print(f"  Total Stream: {self.results['timings']['total_stream_time_ms']:.2f}ms")

        print("="*60 + "\n")

        # Save results to JSON
        with open('/d/gpt-oss/.claude-bus/test-results/e2e-results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        return self.results["steps_failed"] == 0

if __name__ == "__main__":
    runner = E2ETestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
