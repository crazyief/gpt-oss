"""
Falcon-H1_Q5 13k Context Validation Test
Validate safe zone performance with 13k context configuration
"""

import requests
import json
import time
from datetime import datetime

LLM_API_URL = "http://localhost:8090/completion"

def generate_haystack(n_items: int, needle_position: str = "middle") -> tuple[str, int]:
    """Generate haystack with secret number."""
    import random
    secret = random.randint(100000, 999999)

    if needle_position == "first":
        insert_idx = 0
    elif needle_position == "last":
        insert_idx = n_items - 1
    else:
        insert_idx = n_items // 2

    items = []
    for i in range(n_items):
        if i == insert_idx:
            items.append(f"Item {i+1}: The secret number is {secret}")
        else:
            items.append(f"Item {i+1}: This is just filler content number {i+1}")

    return "\n".join(items), secret, insert_idx

def query_llm(prompt: str) -> dict:
    """Query LLM."""
    try:
        response = requests.post(
            LLM_API_URL,
            json={
                "prompt": prompt,
                "temperature": 0.0,
                "max_tokens": 50,
                "stop": ["\n", "Question:", "User:"]
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return {"content": result.get("content", "").strip(), "success": True}
        else:
            return {"content": "", "success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"content": "", "success": False, "error": str(e)}

def extract_number(text: str) -> int:
    """Extract 6-digit number."""
    import re
    numbers = re.findall(r'\b\d{6}\b', text)
    return int(numbers[0]) if numbers else None

def test_item_count(n_items: int, runs: int = 5):
    """Test specific item count multiple times."""
    print(f"\n[{n_items:3d} items] Testing {runs} runs: ", end="", flush=True)

    results = []
    for run in range(runs):
        for pos in ["first", "middle", "last"]:
            haystack, secret, needle_idx = generate_haystack(n_items, pos)

            prompt = f"""Below is a list of items. Find the secret number.

{haystack}

Question: What is the secret number?
Answer: The secret number is"""

            result = query_llm(prompt)

            if result["success"]:
                actual = extract_number(result["content"])
                correct = (actual == secret)
            else:
                correct = False

            results.append(correct)
            status = "+" if correct else "X"
            print(status, end="", flush=True)
            time.sleep(0.3)

    accuracy = sum(results) / len(results) * 100
    print(f" -> {accuracy:.1f}%")

    return accuracy

def main():
    """Run validation test."""
    print("=" * 80)
    print("FALCON-H1_Q5 13K CONTEXT VALIDATION TEST")
    print("=" * 80)
    print(f"Endpoint: {LLM_API_URL}")
    print(f"Context: 13k tokens (~650 items)")
    print(f"Test: Safe zone validation (50-650 items)")
    print("=" * 80)

    # Test safe zone boundaries
    test_points = [50, 200, 400, 600, 650]

    results = {}
    for n_items in test_points:
        accuracy = test_item_count(n_items, runs=5)
        results[n_items] = accuracy

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    all_perfect = all(acc == 100.0 for acc in results.values())

    for items, acc in results.items():
        status = "[OK]" if acc == 100.0 else "[FAIL]"
        print(f"{status} {items:3d} items: {acc:5.1f}% accuracy")

    print("-" * 80)
    if all_perfect:
        print("[SUCCESS] All tests passed! 13k context is stable in safe zone.")
    else:
        print("[WARNING] Some tests failed. Review configuration.")
    print("=" * 80)

if __name__ == "__main__":
    main()
