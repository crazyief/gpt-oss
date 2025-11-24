#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemma Context Limit Finder
Binary search to find exact context limit between 250 (works) and 750 (fails)
"""

import requests
import time
from datetime import datetime
import sys

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_single_query(num_items):
    """Test a single query to check if context is accepted"""
    items = []
    for i in range(1, num_items + 1):
        items.append(f"index {i}: The value for item {i} is {i*100}")
    haystack = "\n".join(items)

    prompt = f"{haystack}\n\nQuestion: What is the content of index 1? Reply with just the value number."

    try:
        response = requests.post(
            "http://localhost:8090/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 20
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return True, tokens, "Success"
        elif response.status_code == 400:
            return False, 0, "HTTP 400 - Context limit exceeded"
        else:
            return False, 0, f"HTTP {response.status_code}"

    except Exception as e:
        return False, 0, f"Error: {str(e)[:50]}"


def main():
    print("="*70)
    print("[TEST] GEMMA 27B CONTEXT LIMIT FINDER")
    print(f"[TIME] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    print("\n[PLAN] Find exact context limit between 250 (works) and 750 (fails)")
    print("   Testing increments: 300, 350, 400, 450, 500, 550, 600, 650, 700")
    print("   Single query per size (fast detection)")
    print("   Estimated time: ~5-10 minutes\n")

    test_sizes = [300, 350, 400, 450, 500, 550, 600, 650, 700]
    results = {}

    for num_items in test_sizes:
        print(f"\n{'='*70}")
        print(f"[TESTING] {num_items} ITEMS")
        print('='*70)

        success, tokens, message = test_single_query(num_items)

        results[num_items] = {
            "success": success,
            "tokens": tokens,
            "message": message
        }

        if success:
            print(f"  ✅ [SUCCESS] {num_items} items works ({tokens:,} tokens)")
        else:
            print(f"  ❌ [FAILED] {num_items} items: {message}")

        # Small rest between tests
        if num_items != test_sizes[-1]:
            print("\n  [WAIT] Resting 5 seconds...")
            time.sleep(5)

    # Find the breaking point
    print("\n" + "+" + "="*68 + "+")
    print("|" + " [SUMMARY] CONTEXT LIMIT ANALYSIS ".center(68) + "|")
    print("+" + "="*68 + "+\n")

    print(f"[MODEL] Gemma 27B")
    print(f"[TIME] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("+" + "-"*68 + "+")
    print("| Items | Tokens  | Status           |")
    print("+" + "-"*68 + "+")

    last_working = 250  # We know 250 works
    first_failing = 750  # We know 750 fails

    for num_items in sorted(results.keys()):
        data = results[num_items]
        status = "✅ Works" if data["success"] else f"❌ {data['message']}"
        tokens_str = f"{data['tokens']:,}" if data['tokens'] > 0 else "N/A"

        print(f"| {num_items:5d} | {tokens_str:7s} | {status:16s} |")

        if data["success"]:
            last_working = num_items
        elif first_failing > num_items:
            first_failing = num_items

    print("+" + "-"*68 + "+")

    print(f"\n[RESULT] CONTEXT LIMIT:")
    print(f"  ✅ Last working size: {last_working} items ({results.get(last_working, {}).get('tokens', 'N/A')} tokens)")
    print(f"  ❌ First failing size: {first_failing} items")
    print(f"\n  📊 Estimated hard limit: ~{(last_working + first_failing) // 2} items")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"gemma_limit_analysis_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Gemma 27B Context Limit Analysis\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Purpose**: Find exact context limit between 250 (works) and 750 (fails)\n\n")

        f.write("## Results\n\n")
        f.write("| Items | Tokens | Status |\n")
        f.write("|-------|--------|--------|\n")

        for num_items in sorted(results.keys()):
            data = results[num_items]
            status = "✅ Works" if data["success"] else f"❌ Failed"
            tokens_str = f"{data['tokens']:,}" if data['tokens'] > 0 else "N/A"
            f.write(f"| {num_items} | {tokens_str} | {status} |\n")

        f.write(f"\n## Conclusion\n\n")
        f.write(f"- **Last working size**: {last_working} items ({results.get(last_working, {}).get('tokens', 'N/A')} tokens)\n")
        f.write(f"- **First failing size**: {first_failing} items\n")
        f.write(f"- **Estimated hard limit**: ~{(last_working + first_failing) // 2} items\n\n")
        f.write("This is a hard configuration limit (HTTP 400), not an accuracy degradation.\n")

    print(f"\n[SAVE] Results saved to: {filename}")

    print("\n" + "="*70)
    print("[OK] LIMIT ANALYSIS COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    main()
