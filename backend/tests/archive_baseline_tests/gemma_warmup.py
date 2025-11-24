"""
Gemma Model Warm-up Script
Extended warm-up for larger 27B model
"""
import requests
import time

LLM_API_URL = "http://localhost:8090/completion"

def warmup_query(query_num: int, prompt: str):
    """Send a single warm-up query."""
    print(f"Warm-up {query_num}: ", end="", flush=True)

    max_retries = 5
    for attempt in range(max_retries):
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
                print(f"[OK] Response: {content}")
                return True
            else:
                if attempt < max_retries - 1:
                    print(f"[HTTP {response.status_code}] Retry {attempt+1}...", end=" ", flush=True)
                    time.sleep(10)
                else:
                    print(f"[FAIL] HTTP {response.status_code}")
                    return False

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[ERROR] Retry {attempt+1}...", end=" ", flush=True)
                time.sleep(10)
            else:
                print(f"[FAIL] {str(e)}")
                return False

    return False

def main():
    print("=" * 60)
    print("GEMMA-3-27B WARM-UP")
    print("=" * 60)

    # Query 1
    warmup_query(1, "What is 2 + 2? Answer:")
    time.sleep(20)

    # Query 2
    warmup_query(2, "What color is the sky? Answer:")
    time.sleep(20)

    # Query 3 - Needle test format
    warmup_query(3, "Below is a list of items. Find the secret number.\n\nItem 1: The secret number is 123456\n\nQuestion: What is the secret number?\nAnswer: The secret number is")

    print("=" * 60)
    print("[OK] Warm-up complete. Model is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
