#!/usr/bin/env python3
"""
Context Limit Test for GPT-OSS 20B
Testing real-world context handling with 131k configuration
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
                timeout=120  # Longer timeout for very large contexts
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

        time.sleep(3)  # Longer wait between tests

    # Calculate accuracy for this size
    if results:
        accuracy = sum(r["correct"] for r in results) / len(results)
        avg_time = sum(r["time"] for r in results) / len(results)
        max_tokens = max(r["tokens"] for r in results) if results else 0
        return accuracy, avg_time, max_tokens

    return 0, 0, 0

def main():
    """Run comprehensive context limit test for GPT-OSS 20B"""

    print("="*70)
    print("CONTEXT LIMIT TEST FOR GPT-OSS 20B")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Model: gpt-oss-20b-F16.gguf")
    print("Configured context: 131,072 tokens")
    print("Quantization: F16 (high quality)")
    print("="*70)

    # Test sizes - going MUCH higher for 131k context
    # Starting conservative, then pushing to limits
    # ~22 tokens per item, so 6000 items = ~132k tokens (should hit limit)
    test_sizes = [
        100, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500,
        5000, 5250, 5500, 5750, 6000, 6100, 6200, 6300, 6400, 6500
    ]

    results_summary = []
    context_limit_hit = False

    for size in test_sizes:
        print(f"\n[Testing {size:,} items]")
        estimated_tokens = size * 22  # Rough estimate
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

        # Stop if accuracy drops significantly
        if accuracy < 0.5 and accuracy > 0:
            print("\n[WARNING] Accuracy below 50%, but continuing to find true limit...")
            # Continue anyway to find the real limit

        # Progressive wait times
        if size < 2000:
            wait_time = 5
        elif size < 4000:
            wait_time = 10
        else:
            wait_time = 15

        if size < test_sizes[-1] and not context_limit_hit:
            print(f"\nWaiting {wait_time} seconds before next size...")
            time.sleep(wait_time)

    # Final report
    print("\n" + "="*70)
    print("GPT-OSS 20B - FINAL RESULTS")
    print("="*70)

    print("\n| Items | Accuracy | Time | Tokens | Status |")
    print("|-------|----------|------|---------|--------|")

    for r in results_summary:
        if r['status'] == "OK":
            print(f"| {r['size']:,} | {r['accuracy']:.0%} | {r['avg_time']:.1f}s | {r['tokens']:,} | OK |")
        else:
            print(f"| {r['size']:,} | - | - | {r['tokens']:,} | EXCEEDED |")

    # Analysis
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)

    # Find maximum reliable size
    max_reliable = 0
    for r in results_summary:
        if r['status'] == "OK" and r['accuracy'] >= 0.95:
            max_reliable = r['size']

    if max_reliable > 0:
        max_r = next(r for r in results_summary if r['size'] == max_reliable)
        print(f"\nMaximum reliable context: {max_reliable:,} items")
        print(f"  - Tokens used: {max_r['tokens']:,}")
        print(f"  - Context utilization: {max_r['tokens']/131072:.1%} of 131k")
        print(f"  - Accuracy: {max_r['accuracy']:.0%}")
        print(f"  - Avg response time: {max_r['avg_time']:.1f}s")

    # Find actual limit
    if context_limit_hit:
        last_working = results_summary[-2] if len(results_summary) > 1 else None
        if last_working and last_working['status'] == "OK":
            print(f"\nActual usable limit: {last_working['size']:,} items")
            print(f"  - Tokens used: {last_working['tokens']:,}")
            print(f"  - Context utilization: {last_working['tokens']/131072:.1%}")
            print(f"  - Buffer remaining: {131072 - last_working['tokens']:,} tokens")

    # Degradation analysis
    degradation_point = None
    for r in results_summary:
        if r['status'] == "OK" and r['accuracy'] < 0.95:
            degradation_point = r['size']
            print(f"\n[WARNING] First accuracy degradation at {r['size']:,} items ({r['accuracy']:.0%})")
            break

    if not degradation_point and max_reliable > 0:
        print(f"\n[SUCCESS] No degradation observed up to {max_reliable:,} items!")

    # 3-Model Comparison
    print("\n" + "="*70)
    print("3-MODEL COMPARISON (RTX 5090)")
    print("="*70)

    print("\n| Model | Config | Actual | Items | Tokens | Speed |")
    print("|-------|--------|--------|-------|--------|-------|")
    print("| Mistral 24B Q6_K | 32k | 32k | 1,400 | 31,710 | 0.6s |")
    print("| Gemma 3 27B | 131k | 24k* | 1,500 | 21,928 | 1.5s |")

    if max_reliable > 0:
        print(f"| GPT-OSS 20B | 131k | 131k | {max_reliable:,} | {max_r['tokens']:,} | {max_r['avg_time']:.1f}s |")

        print("\n*Gemma limited by VRAM on RTX 5090")

        print(f"\nGPT-OSS Advantages:")
        print(f"  vs Mistral: {max_reliable/1400:.1f}x more items, {max_r['tokens']/31710:.1f}x more tokens")
        print(f"  vs Gemma:   {max_reliable/1500:.1f}x more items, {max_r['tokens']/21928:.1f}x more tokens")

    # Save results
    with open("gpt_oss_20b_context_results.md", "w", encoding="utf-8") as f:
        f.write(f"# GPT-OSS 20B Context Limit Test\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model**: gpt-oss-20b-F16.gguf\n")
        f.write(f"**Configured Context**: 131,072 tokens\n")
        f.write(f"**Hardware**: RTX 5090 (32GB VRAM)\n\n")

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
            f.write(f"- **Maximum Reliable Context**: {max_reliable:,} items ({max_r['tokens']:,} tokens)\n")
            f.write(f"- **Context Utilization**: {max_r['tokens']/131072:.1%} of 131k\n")
        if degradation_point:
            f.write(f"- **First Degradation**: {degradation_point:,} items\n")
        if context_limit_hit:
            f.write(f"- **Hard Limit**: {results_summary[-1]['size']:,} items (needs {results_summary[-1]['tokens']:,} tokens)\n")

        f.write("\n## 3-Model Comparison\n\n")
        f.write("| Model | Context Config | Actual on 5090 | Max Items | Max Tokens | Advantage |\n")
        f.write("|-------|---------------|----------------|-----------|------------|----------|\n")
        f.write("| Mistral 24B Q6_K | 32k | 32k | 1,400 | 31,710 | Baseline |\n")
        f.write("| Gemma 3 27B | 131k | 24k (limited) | 1,500 | 21,928 | 1.1x items |\n")
        if max_reliable > 0:
            f.write(f"| GPT-OSS 20B | 131k | 131k (full) | {max_reliable:,} | {max_r['tokens']:,} | {max_reliable/1400:.1f}x items |\n")

    print(f"\nDetailed results saved to: gpt_oss_20b_context_results.md")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()