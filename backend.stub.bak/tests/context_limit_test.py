#!/usr/bin/env python3
"""
Context Limit Test for Mistral 24B
Tests within the 32k token context window
"""

import requests
import time
from datetime import datetime

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
        prompt = f"{haystack}\n\nQuestion: What is the content of index {test_idx}? Reply with just the value number."
        expected = str(test_idx * 100)

        print(f"  Testing index {test_idx} ({position})...", end=" ")

        start = time.time()

        try:
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 20
                },
                timeout=30
            )

            elapsed = time.time() - start

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()

                # Check if expected value is in response
                correct = expected in content

                status = "PASS" if correct else "FAIL"
                print(f"{status} ({elapsed:.1f}s) - Got: {content[:30]}")

                results.append({
                    "position": position,
                    "correct": correct,
                    "time": elapsed,
                    "response": content[:50],
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

        time.sleep(2)

    # Calculate accuracy for this size
    if results:
        accuracy = sum(r["correct"] for r in results) / len(results)
        avg_time = sum(r["time"] for r in results) / len(results)
        max_tokens = max(r["tokens"] for r in results) if results else 0
        return accuracy, avg_time, max_tokens

    return 0, 0, 0

def main():
    """Run context limit test"""

    print("="*60)
    print("CONTEXT LIMIT TEST FOR MISTRAL 24B")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Configured context: 32,768 tokens")
    print("="*60)

    # Test sizes based on what we learned
    # ~21 tokens per item, so 1500 items = ~31,500 tokens (near limit)
    test_sizes = [100, 250, 500, 750, 1000, 1100, 1200, 1300, 1400, 1450, 1500]

    results_summary = []
    context_limit_hit = False

    for size in test_sizes:
        print(f"\n[Testing {size:,} items]")
        print("-" * 40)

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

        # Stop if accuracy drops significantly
        if accuracy < 0.5 and accuracy > 0:
            print("\n[WARNING] Accuracy below 50%, stopping tests")
            break

        # Wait between sizes
        if size < test_sizes[-1]:
            print("\nWaiting 10 seconds before next size...")
            time.sleep(10)

    # Final report
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)

    print("\n| Items | Accuracy | Time | Tokens | Status |")
    print("|-------|----------|------|---------|--------|")

    for r in results_summary:
        if r['status'] == "OK":
            print(f"| {r['size']:,} | {r['accuracy']:.0%} | {r['avg_time']:.1f}s | {r['tokens']:,} | OK |")
        else:
            print(f"| {r['size']:,} | - | - | {r['tokens']:,} | EXCEEDED |")

    # Analysis
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)

    # Find maximum reliable size
    max_reliable = 0
    for r in results_summary:
        if r['status'] == "OK" and r['accuracy'] >= 0.95:
            max_reliable = r['size']

    if max_reliable > 0:
        print(f"\nMaximum reliable context: {max_reliable:,} items")
        max_r = next(r for r in results_summary if r['size'] == max_reliable)
        print(f"  - Tokens used: {max_r['tokens']:,}")
        print(f"  - Accuracy: {max_r['accuracy']:.0%}")
        print(f"  - Avg response time: {max_r['avg_time']:.1f}s")

    # Find actual limit
    if context_limit_hit:
        last_working = results_summary[-2] if len(results_summary) > 1 else None
        if last_working and last_working['status'] == "OK":
            print(f"\nActual usable limit: {last_working['size']:,} items")
            print(f"  - Tokens used: {last_working['tokens']:,}")
            print(f"  - Buffer remaining: {32768 - last_working['tokens']:,} tokens")

    # Degradation analysis
    degradation_point = None
    for r in results_summary:
        if r['status'] == "OK" and r['accuracy'] < 0.95:
            degradation_point = r['size']
            print(f"\n[WARNING] Accuracy degradation at {r['size']:,} items ({r['accuracy']:.0%})")
            break

    if not degradation_point and max_reliable > 0:
        print(f"\n[SUCCESS] No degradation observed up to {max_reliable:,} items")

    # Save detailed results
    with open("context_limit_results.md", "w", encoding="utf-8") as f:
        f.write(f"# Mistral 24B Context Limit Test\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model**: mistral-small-24b-Q6_K\n")
        f.write(f"**Configured Context**: 32,768 tokens\n\n")

        f.write("## Results\n\n")
        f.write("| Items | Accuracy | Time | Tokens | Status |\n")
        f.write("|-------|----------|------|---------|--------|\n")

        for r in results_summary:
            if r['status'] == "OK":
                f.write(f"| {r['size']:,} | {r['accuracy']:.0%} | {r['avg_time']:.1f}s | {r['tokens']:,} | OK |\n")
            else:
                f.write(f"| {r['size']:,} | - | - | {r['tokens']:,} | EXCEEDED |\n")

        f.write("\n## Key Findings\n\n")
        if max_reliable > 0:
            f.write(f"- **Maximum Reliable Context**: {max_reliable:,} items ({results_summary[test_sizes.index(max_reliable)]['tokens']:,} tokens)\n")
        if degradation_point:
            f.write(f"- **Degradation Point**: {degradation_point:,} items\n")
        if context_limit_hit:
            f.write(f"- **Context Limit Hit**: At {results_summary[-1]['size']:,} items (needs {results_summary[-1]['tokens']:,} tokens)\n")

    print(f"\nDetailed results saved to: context_limit_results.md")

if __name__ == "__main__":
    main()