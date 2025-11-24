#!/usr/bin/env python3
"""
Reproducibility Test: Check if temperature=0 gives consistent results
"""

import requests
import time

def test_reproducibility(num_items, num_runs=5):
    """Test same query multiple times with temperature=0"""

    # Generate haystack
    items = []
    for i in range(1, num_items + 1):
        items.append(f"index {i}: The value for item {i} is {i*100}")
    haystack = "\n".join(items)

    # Test middle position
    test_idx = num_items // 2
    prompt = f"{haystack}\n\nQuestion: What is the content of index {test_idx}? Reply with just the value number."
    expected = str(test_idx * 100)

    print(f"\nTesting {num_items} items, middle position (index {test_idx})")
    print(f"Expected answer: {expected}")
    print(f"Running {num_runs} times with temperature=0...\n")

    results = []

    for run in range(1, num_runs + 1):
        print(f"Run {run}/{num_runs}...", end=" ")

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

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                correct = expected in content

                results.append({
                    "run": run,
                    "answer": content,
                    "correct": correct
                })

                status = "✅ PASS" if correct else "❌ FAIL"
                print(f"{status} - Got: {content}")
            else:
                print(f"❌ HTTP {response.status_code}")
                results.append({"run": run, "answer": "ERROR", "correct": False})

        except Exception as e:
            print(f"❌ ERROR: {str(e)[:50]}")
            results.append({"run": run, "answer": "EXCEPTION", "correct": False})

        # Small delay between runs
        time.sleep(2)

    # Analysis
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)

    # Check if all answers are identical
    answers = [r["answer"] for r in results]
    unique_answers = set(answers)

    if len(unique_answers) == 1:
        print("✅ DETERMINISTIC: All runs returned identical answer")
        print(f"   Answer: {answers[0]}")
    else:
        print("⚠️ NON-DETERMINISTIC: Different answers across runs!")
        print(f"   Unique answers: {unique_answers}")

    # Check accuracy consistency
    accuracy = sum(r["correct"] for r in results) / len(results)
    print(f"\nAccuracy: {accuracy:.0%} ({sum(r['correct'] for r in results)}/{len(results)} runs correct)")

    if accuracy == 1.0:
        print("✅ STABLE: 100% accuracy across all runs")
    elif accuracy == 0.0:
        print("❌ UNSTABLE: 0% accuracy across all runs")
    else:
        print(f"⚠️ INCONSISTENT: Only {accuracy:.0%} runs were correct")

    return results, accuracy


if __name__ == "__main__":
    print("="*60)
    print("REPRODUCIBILITY TEST FOR MAGISTRAL-SMALL-2506")
    print("Testing if temperature=0 gives consistent results")
    print("="*60)

    # Test at a known "failure point"
    test_sizes = [750, 1000, 1250]

    all_results = {}

    for size in test_sizes:
        results, accuracy = test_reproducibility(size, num_runs=5)
        all_results[size] = {"results": results, "accuracy": accuracy}

        print("\nWaiting 10 seconds before next test...")
        time.sleep(10)

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    for size, data in all_results.items():
        accuracy = data["accuracy"]
        status = "✅" if accuracy == 1.0 else "⚠️" if accuracy >= 0.6 else "❌"
        print(f"{status} {size} items: {accuracy:.0%} accuracy across 5 runs")

    print("\nConclusion:")
    if all(data["accuracy"] in [0.0, 1.0] for data in all_results.values()):
        print("✅ Model is DETERMINISTIC (temperature=0 works)")
        print("   → Single test run is sufficient")
    else:
        print("⚠️ Model shows RANDOMNESS despite temperature=0")
        print("   → Multiple runs recommended for accurate statistics")
