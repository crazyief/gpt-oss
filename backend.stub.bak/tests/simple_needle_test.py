#!/usr/bin/env python3
"""
Simple Needle-in-Haystack Test for Mistral 24B
Tests context window handling with indexed items
"""

import requests
import time
import json
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
        prompt = f"{haystack}\n\nQuestion: What is the content of index {test_idx}? Reply with just the value after 'is'."
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
                    "response": content[:50]
                })

                # Calculate approximate tokens
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                if tokens_used:
                    print(f"    Tokens used: {tokens_used:,}")

            else:
                print(f"ERROR - HTTP {response.status_code}")
                error_msg = response.text[:200]
                print(f"    Error: {error_msg}")

        except Exception as e:
            print(f"ERROR - {str(e)[:50]}")

        # Small delay between requests
        time.sleep(2)

    # Calculate accuracy for this size
    if results:
        accuracy = sum(r["correct"] for r in results) / len(results)
        avg_time = sum(r["time"] for r in results) / len(results)
        return accuracy, avg_time

    return 0, 0

def main():
    """Run progressive context tests"""

    print("="*60)
    print("NEEDLE-IN-HAYSTACK CONTEXT TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Test sizes - starting smaller to ensure it works
    test_sizes = [100, 500, 1000, 2000, 3000, 4000, 5000, 7500, 10000, 12500, 15000]

    results_summary = []

    for size in test_sizes:
        print(f"\n[Testing {size:,} items]")
        print("-" * 40)

        accuracy, avg_time = test_context_size(size)

        results_summary.append({
            "size": size,
            "accuracy": accuracy,
            "avg_time": avg_time
        })

        print(f"Summary: {accuracy:.0%} accuracy, {avg_time:.1f}s average")

        # Stop if accuracy drops below 50%
        if accuracy < 0.5:
            print("\n[WARNING] Accuracy below 50%, stopping tests")
            break

        # Wait between different sizes
        print("\nWaiting 10 seconds before next size...")
        time.sleep(10)

    # Final report
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)

    report = []
    report.append("| Items | Accuracy | Avg Time |")
    report.append("|-------|----------|----------|")

    for r in results_summary:
        report.append(f"| {r['size']:,} | {r['accuracy']:.0%} | {r['avg_time']:.1f}s |")

    print("\n".join(report))

    # Find degradation point
    for r in results_summary:
        if r['accuracy'] < 0.95:
            print(f"\n[WARNING] Degradation point: {r['size']:,} items (accuracy dropped to {r['accuracy']:.0%})")
            break
    else:
        if results_summary:
            print(f"\n[PASS] All tested sizes up to {results_summary[-1]['size']:,} items maintained >95% accuracy")

    # Save results
    with open("needle_test_results.md", "w", encoding="utf-8") as f:
        f.write(f"# Needle-in-Haystack Test Results\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Results\n\n")
        f.write("\n".join(report))

        for r in results_summary:
            if r['accuracy'] < 0.95:
                f.write(f"\n\n**Degradation Point**: {r['size']:,} items")
                break

    print(f"\nResults saved to: needle_test_results.md")

if __name__ == "__main__":
    main()