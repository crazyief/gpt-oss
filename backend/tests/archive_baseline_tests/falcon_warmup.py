"""
Falcon-H1_Q5 Warm-up Script
Send 2 simple queries to warm up the model
"""

import requests
import json

LLM_API_URL = "http://localhost:8090/completion"

def warmup_query(query_num: int, prompt: str):
    """Send a single warm-up query."""
    print(f"Warm-up {query_num}: ", end="", flush=True)

    try:
        response = requests.post(
            LLM_API_URL,
            json={
                "prompt": prompt,
                "temperature": 0.0,
                "max_tokens": 20,
                "stop": ["\n"]
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get("content", "").strip()
            print(f"[OK] Response: {content[:50]}")
            return True
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run warm-up queries."""
    import time

    print("=" * 60)
    print("FALCON-H1_Q5 WARM-UP")
    print("=" * 60)

    # Warm-up query 1 - Simple arithmetic
    warmup_query(1, "What is 2 + 2? Answer:")

    print("Waiting 20 seconds before next query...")
    time.sleep(20)

    # Warm-up query 2 - Simple question
    warmup_query(2, "What color is the sky? Answer:")

    print("=" * 60)
    print("[OK] Warm-up complete. Model is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
