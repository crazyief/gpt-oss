#!/usr/bin/env python3
"""
Fixed Context Test for GPT-OSS 20B
Handles the model's special output format with channels
"""

import requests
import time
import re
from datetime import datetime

def extract_final_content(response_text):
    """Extract the final channel content from GPT-OSS response"""
    # Pattern to extract content after <|channel|>final<|message|>
    pattern = r'<\|channel\|>final<\|message\|>(.*?)(?:<\|end\|>|$)'
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: try to extract any number from the response
    numbers = re.findall(r'\d+', response_text)
    if numbers:
        return numbers[-1]  # Return the last number found

    return response_text.strip()

def test_context_size(num_items):
    """Test with a specific number of indexed items"""

    # Generate indexed list
    items = []
    for i in range(1, num_items + 1):
        items.append(f"index {i}: The value for item {i} is {i*100}")

    haystack = "\n".join(items)

    # Test retrieving first, middle and last items
    test_positions = [
        (1, "first"),
        (num_items // 2, "middle"),
        (num_items, "last")
    ]

    results = []

    for test_idx, position in test_positions:
        # More explicit prompt for GPT-OSS
        prompt = f"""{haystack}

Based on the list above, what is the value for index {test_idx}?
Answer with only the number, nothing else."""

        expected = str(test_idx * 100)

        print(f"  Testing index {test_idx} ({position})...", end=" ")

        start = time.time()

        try:
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Answer questions precisely based on the given data."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,
                    "max_tokens": 50
                },
                timeout=120
            )

            elapsed = time.time() - start

            if response.status_code == 200:
                result = response.json()
                raw_content = result["choices"][0]["message"]["content"]
                content = extract_final_content(raw_content)

                # Check if expected value is in response
                correct = expected in content or expected == content

                status = "PASS" if correct else "FAIL"
                print(f"{status} ({elapsed:.1f}s) - Got: {content[:50]}")

                results.append({
                    "position": position,
                    "correct": correct,
                    "time": elapsed,
                    "response": content[:100],
                    "tokens": result.get("usage", {}).get("total_tokens", 0)
                })

            elif response.status_code == 400:
                error = response.json().get("error", {})
                if "exceed_context_size" in error.get("type", ""):
                    n_prompt = error.get("n_prompt_tokens", 0)
                    n_ctx = error.get("n_ctx", 0)
                    print(f"CONTEXT EXCEEDED - Needs {n_prompt:,} tokens, limit is {n_ctx:,}")
                    return None, None, n_prompt
                else:
                    print(f"ERROR - HTTP 400: {error.get('message', 'Unknown')}")
            else:
                print(f"ERROR - HTTP {response.status_code}")

        except Exception as e:
            print(f"ERROR - {str(e)[:50]}")

        time.sleep(3)

    # Calculate accuracy for this size
    if results:
        accuracy = sum(r["correct"] for r in results) / len(results)
        avg_time = sum(r["time"] for r in results) / len(results)
        max_tokens = max(r["tokens"] for r in results) if results else 0
        return accuracy, avg_time, max_tokens

    return 0, 0, 0

def main():
    """Run fixed context test for GPT-OSS 20B"""

    print("="*70)
    print("GPT-OSS 20B CONTEXT TEST (FIXED)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Model: gpt-oss-20b-F16.gguf")
    print("Configured context: 131,072 tokens")
    print("="*70)

    # More conservative test sizes first to validate the fix works
    test_sizes = [
        10, 50, 100, 250, 500, 750, 1000, 1250, 1500, 2000,
        2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000
    ]

    results_summary = []
    context_limit_hit = False
    max_reliable = 0

    for size in test_sizes:
        print(f"\n[Testing {size:,} items]")
        estimated_tokens = size * 22
        print(f"Estimated tokens: ~{estimated_tokens:,}")
        print("-" * 50)

        result = test_context_size(size)

        if result[0] is None:  # Context exceeded
            tokens_needed = result[2]
            results_summary.append({
                "size": size,
                "accuracy": 0,
                "avg_time": 0,
                "tokens": tokens_needed,
                "status": "EXCEEDED"
            })
            print(f"Context limit exceeded! Needs ~{tokens_needed:,} tokens")
            context_limit_hit = True
            break
        else:
            accuracy, avg_time, max_tokens = result
            results_summary.append({
                "size": size,
                "accuracy": accuracy,
                "avg_time": avg_time,
                "tokens": max_tokens,
                "status": "OK"
            })
            print(f"Summary: {accuracy:.0%} accuracy, {avg_time:.1f}s avg, {max_tokens:,} tokens")

            # Track maximum reliable size
            if accuracy >= 0.95:
                max_reliable = size

            # Stop if accuracy is consistently terrible
            if size >= 500 and accuracy == 0:
                consecutive_zeros = sum(1 for r in results_summary[-3:] if r['accuracy'] == 0)
                if consecutive_zeros >= 3:
                    print("\n[STOPPING] Model consistently failing, ending test")
                    break

        # Progressive wait
        wait_time = 5 if size < 1000 else (10 if size < 3000 else 15)
        if size < test_sizes[-1] and not context_limit_hit:
            print(f"\nWaiting {wait_time} seconds...")
            time.sleep(wait_time)

    # Final report
    print("\n" + "="*70)
    print("FINAL RESULTS - GPT-OSS 20B")
    print("="*70)

    print("\n| Items | Accuracy | Time | Tokens | Status |")
    print("|-------|----------|------|---------|--------|")

    for r in results_summary[:20]:  # Limit output
        if r['status'] == "OK":
            print(f"| {r['size']:,} | {r['accuracy']:.0%} | {r['avg_time']:.1f}s | {r['tokens']:,} | OK |")

    # Analysis
    print("\n" + "="*70)
    print("3-MODEL FINAL COMPARISON (RTX 5090)")
    print("="*70)

    print("\n| Model | Config | Working | Max Items | Max Tokens | Speed | Notes |")
    print("|-------|--------|---------|-----------|------------|-------|-------|")
    print("| Mistral 24B | 32k | 32k | 1,400 | 31,710 | 0.6s | Stable |")
    print("| Gemma 3 27B | 131k | 24k | 1,500 | 21,928 | 1.5s | VRAM limited |")

    if max_reliable > 0:
        max_r = next((r for r in results_summary if r['size'] == max_reliable), None)
        if max_r:
            print(f"| GPT-OSS 20B | 131k | {max_r['tokens']//1000}k | {max_reliable:,} | {max_r['tokens']:,} | {max_r['avg_time']:.1f}s | Special format |")
    else:
        print("| GPT-OSS 20B | 131k | ? | Failed | - | - | Format issues |")

    print("\n[ISSUE] GPT-OSS 20B uses special output format with channel markers")
    print("Output pattern: <|channel|>analysis<|message|>...<|channel|>final<|message|>...")

if __name__ == "__main__":
    main()