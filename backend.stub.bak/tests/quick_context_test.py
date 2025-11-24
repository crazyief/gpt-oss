#!/usr/bin/env python3
"""
Quick Context Test for Mistral 24B
Simplified version for rapid testing and validation
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path

# Configuration
LLM_URL = "http://localhost:8080/v1/chat/completions"
OUTPUT_FILE = Path("quick_test_results.md")

def generate_simple_haystack(size: int) -> str:
    """Generate simple indexed list"""
    items = []
    for i in range(1, size + 1):
        # Simple, predictable pattern
        items.append(f"index {i:04d}: Item number {i} has value {i*100}")
    return "\n".join(items)

def run_quick_test(sizes=[1000, 5000, 10000, 15000]):
    """Run quick needle-in-haystack test"""
    results = []

    print("Quick Context Test Starting...")
    print("="*50)

    for size in sizes:
        print(f"\nTesting {size} items...")

        # Generate haystack
        haystack = generate_simple_haystack(size)

        # Create queries for different positions
        test_indices = [1, size//2, size]

        for idx in test_indices:
            prompt = f"{haystack}\n\nWhat is the content of index {idx:04d}? Reply with just the content after the colon."
            expected = f"Item number {idx} has value {idx*100}"

            # Time the request
            start = time.time()

            try:
                response = requests.post(
                    LLM_URL,
                    json={
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0,
                        "max_tokens": 50,
                        "stop": ["\n"]
                    },
                    timeout=30
                )

                elapsed = time.time() - start

                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"].strip()

                    # Check accuracy
                    correct = expected.lower() in content.lower() or content.lower() in expected.lower()

                    result = {
                        "size": size,
                        "index": idx,
                        "position": "start" if idx == 1 else ("end" if idx == size else "middle"),
                        "correct": correct,
                        "time": elapsed,
                        "response": content[:50],
                        "expected": expected
                    }

                    results.append(result)

                    status = "✓" if correct else "✗"
                    print(f"  Index {idx:4d} ({result['position']:6s}): {status} ({elapsed:.1f}s)")

                else:
                    print(f"  Index {idx:4d}: Failed - HTTP {response.status_code}")

            except Exception as e:
                print(f"  Index {idx:4d}: Error - {str(e)[:50]}")

            # Brief pause between tests
            time.sleep(2)

        # Summary for this size
        size_results = [r for r in results if r['size'] == size]
        if size_results:
            accuracy = sum(r['correct'] for r in size_results) / len(size_results)
            avg_time = sum(r['time'] for r in size_results) / len(size_results)
            print(f"  Summary: {accuracy:.0%} accurate, {avg_time:.1f}s avg")

    # Generate report
    report = f"""# Quick Context Test Results
**Model**: mistral-small-24b-Q6_K
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary
"""

    # Add results table
    report += "\n| Size | Position | Index | Correct | Time(s) |\n"
    report += "|------|----------|-------|---------|----------|\n"

    for r in results:
        correct = "✓" if r['correct'] else "✗"
        report += f"| {r['size']:,} | {r['position']} | {r['index']} | {correct} | {r['time']:.1f} |\n"

    # Calculate overall metrics
    if results:
        overall_accuracy = sum(r['correct'] for r in results) / len(results)
        report += f"\n**Overall Accuracy**: {overall_accuracy:.1%}\n"

        # Find degradation point
        for size in sizes:
            size_results = [r for r in results if r['size'] == size]
            if size_results:
                acc = sum(r['correct'] for r in size_results) / len(size_results)
                if acc < 0.95:
                    report += f"**Degradation Point**: {size:,} items (accuracy: {acc:.1%})\n"
                    break

    # Save report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n{'='*50}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Overall accuracy: {overall_accuracy:.1%}")

    return results

if __name__ == "__main__":
    # Run with default sizes or customize
    import sys

    if len(sys.argv) > 1:
        # Custom sizes from command line
        sizes = [int(x) for x in sys.argv[1:]]
        print(f"Running with custom sizes: {sizes}")
        run_quick_test(sizes)
    else:
        # Default progressive test
        run_quick_test()