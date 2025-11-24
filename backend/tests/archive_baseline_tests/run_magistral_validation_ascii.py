#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Magistral-Small-2506 Scientific Validation Test
Automatically runs 5 iterations for suspicious test points
"""

import requests
import time
from datetime import datetime
import sys

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_position(num_items, position_name, index):
    """Test a single position"""
    items = []
    for i in range(1, num_items + 1):
        items.append(f"index {i}: The value for item {i} is {i*100}")
    haystack = "\n".join(items)

    prompt = f"{haystack}\n\nQuestion: What is the content of index {index}? Reply with just the value number."
    expected = str(index * 100)

    try:
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 20
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            correct = expected in content
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return correct, content, tokens
        else:
            return False, f"HTTP {response.status_code}", 0

    except Exception as e:
        return False, f"Error: {str(e)[:30]}", 0


def test_context_size_multi_run(num_items, num_runs=5):
    """Test with multiple runs to check consistency"""

    print(f"\n{'='*70}")
    print(f"[TESTING] {num_items} ITEMS ({num_runs} RUNS)")
    print('='*70)

    test_positions = [
        (1, "first"),
        (num_items // 2, "middle"),
        (num_items, "last")
    ]

    position_results = {}

    for test_idx, position in test_positions:
        print(f"\n  [POSITION] {position.upper()} (index {test_idx})")
        print(f"  {'-'*60}")

        results = []

        for run in range(1, num_runs + 1):
            print(f"\n    [RUN {run}/{num_runs}] {'-'*50}")
            print(f"    Testing index {test_idx}...", end=" ")

            correct, content, tokens = test_position(num_items, position, test_idx)

            results.append({
                "run": run,
                "correct": correct,
                "content": content,
                "tokens": tokens
            })

            status = "[PASS]" if correct else "[FAIL]"
            print(f"{status}")
            print(f"    Answer: {content[:50]}")
            print(f"    Tokens: {tokens:,}")

            if run < num_runs:  # Don't wait after last run
                print(f"\n    [WAIT] Resting 15 seconds before next run...")
                for i in range(15, 0, -1):
                    print(f"    [WAIT] {i:2d} seconds remaining...", end="\r")
                    time.sleep(1)
                print()  # New line after countdown

        # Calculate statistics
        correct_count = sum(r["correct"] for r in results)
        accuracy = correct_count / num_runs
        avg_tokens = sum(r["tokens"] for r in results) / num_runs if any(r["tokens"] > 0 for r in results) else 0

        position_results[position] = {
            "accuracy": accuracy,
            "correct_count": correct_count,
            "total_runs": num_runs,
            "avg_tokens": avg_tokens,
            "results": results
        }

        # Interpret results
        if accuracy == 1.0:
            consistency = "[OK] STABLE (always correct)"
        elif accuracy == 0.0:
            consistency = "[FAIL] STABLE FAILURE (always wrong)"
        elif accuracy >= 0.8:
            consistency = "[WARN] MOSTLY CORRECT (occasional failure)"
        elif accuracy >= 0.4:
            consistency = "[WARN] INCONSISTENT (random)"
        else:
            consistency = "[FAIL] MOSTLY WRONG (occasional success)"

        print(f"\n    [RESULT] {position.upper()}: {accuracy:.0%} ({correct_count}/{num_runs}) - {consistency}")

    # Overall accuracy
    overall_correct = sum(pos["correct_count"] for pos in position_results.values())
    overall_total = sum(pos["total_runs"] for pos in position_results.values())
    overall_accuracy = overall_correct / overall_total

    print(f"\n  {'='*60}")
    print(f"  [OVERALL] Accuracy: {overall_accuracy:.0%} ({overall_correct}/{overall_total})")
    print(f"  [OVERALL] Average Tokens: {position_results['middle']['avg_tokens']:.0f}")
    print(f"  {'='*60}")

    return position_results, overall_accuracy


def main():
    print("="*70)
    print("[TEST] MAGISTRAL-SMALL-2506 SCIENTIFIC VALIDATION TEST")
    print(f"[TIME] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    print("\n[PLAN] TEST PLAN:")
    print("   - 750 items  (Previously 67% - verify consistency)")
    print("   - 1250 items (Previously 67% - verify consistency)")
    print("   - 1400 items (Previously 67% - verify consistency)")
    print("\n   Each test: 5 runs x 3 positions = 15 total queries")
    print("   Total: 45 queries across all test sizes")
    print("   Estimated time: ~1.5-2 hours\n")

    magistral_tests = {
        750: "Previously 67% - verify if consistent",
        1250: "Previously 67% - verify if consistent",
        1400: "Previously 67% - verify if consistent"
    }

    all_results = {}
    test_num = 1
    total_tests = len(magistral_tests)

    for num_items, description in magistral_tests.items():
        print(f"\n{'+'+'='*68+'+'}")
        print(f"| [TEST {test_num}/{total_tests}] {num_items} ITEMS{' '*(68-len(f'[TEST {test_num}/{total_tests}] {num_items} ITEMS')-4)}|")
        print(f"| [NOTE] {description}{' '*(68-len(f'[NOTE] {description}')-4)}|")
        print(f"{'+'+'='*68+'+'}")

        position_results, overall_accuracy = test_context_size_multi_run(num_items, num_runs=5)

        all_results[num_items] = {
            "position_results": position_results,
            "overall_accuracy": overall_accuracy,
            "description": description
        }

        test_num += 1

        # Wait between test sizes (but not after last test)
        if num_items != list(magistral_tests.keys())[-1]:
            print("\n" + "[WAIT] "*35)
            print("[WAIT] Switching to next test size...")
            print("[WAIT] Resting 15 seconds before next test...")
            print("[WAIT] "*35)
            for i in range(15, 0, -1):
                print(f"[WAIT] {i:2d} seconds remaining...", end="\r")
                time.sleep(1)
            print("\n")

    # Final Summary
    print("\n" + "+" + "="*68 + "+")
    print("|" + " [SUMMARY] FINAL RESULTS ".center(68) + "|")
    print("+" + "="*68 + "+")

    print(f"\n[MODEL] Magistral-Small-2506_Q8_0")
    print(f"[TIME] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("+" + "-"*68 + "+")
    print("| Items | Overall  | First | Middle | Last  | Consistency      |")
    print("+" + "-"*68 + "+")

    for num_items, data in all_results.items():
        pos_results = data["position_results"]
        overall_acc = data["overall_accuracy"]

        # Determine consistency
        middle_acc = pos_results["middle"]["accuracy"]
        if middle_acc == 1.0 or middle_acc == 0.0:
            consistency = "Stable"
        elif middle_acc >= 0.8:
            consistency = "Mostly OK"
        elif middle_acc >= 0.4:
            consistency = "Random"
        else:
            consistency = "Mostly Fail"

        print(f"| {num_items:5d} | {overall_acc:6.0%}   | {pos_results['first']['accuracy']:5.0%} | {pos_results['middle']['accuracy']:6.0%} | {pos_results['last']['accuracy']:5.0%} | {consistency:16s} |")

    print("+" + "-"*68 + "+")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"magistral_validation_results_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Magistral-Small-2506 Scientific Validation Results\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Purpose**: Verify suspicious 67% accuracy points with 5-run testing\n\n")

        f.write("## Summary\n\n")
        f.write("| Items | Overall | First | Middle | Last | Consistency |\n")
        f.write("|-------|---------|-------|--------|------|-------------|\n")

        for num_items, data in all_results.items():
            pos_results = data["position_results"]
            middle_acc = pos_results["middle"]["accuracy"]

            if middle_acc == 1.0 or middle_acc == 0.0:
                consistency = "Stable"
            elif middle_acc >= 0.8:
                consistency = "Mostly OK"
            elif middle_acc >= 0.4:
                consistency = "Random"
            else:
                consistency = "Mostly Fail"

            f.write(f"| {num_items} | {data['overall_accuracy']:.0%} | ")
            f.write(f"{pos_results['first']['accuracy']:.0%} | ")
            f.write(f"{pos_results['middle']['accuracy']:.0%} | ")
            f.write(f"{pos_results['last']['accuracy']:.0%} | ")
            f.write(f"{consistency} |\n")

        f.write("\n## Detailed Results\n\n")

        for num_items, data in all_results.items():
            f.write(f"### {num_items} Items\n\n")
            f.write(f"**Test Reason**: {data['description']}\n\n")

            for position, pos_data in data["position_results"].items():
                f.write(f"**{position.upper()} Position**:\n")
                f.write(f"- Accuracy: {pos_data['accuracy']:.0%} ({pos_data['correct_count']}/{pos_data['total_runs']})\n")
                f.write(f"- Avg Tokens: {pos_data['avg_tokens']:.0f}\n")
                f.write(f"- Results: ")

                for r in pos_data["results"]:
                    status = "[OK]" if r["correct"] else "[X]"
                    f.write(f"{status} ")

                f.write("\n\n")

        f.write("\n## Recommendations\n\n")

        for num_items, data in all_results.items():
            pos_results = data["position_results"]
            middle_acc = pos_results["middle"]["accuracy"]

            if middle_acc == 1.0:
                f.write(f"- **{num_items} items**: Update to 100% (was 67%, now consistently correct)\n")
            elif middle_acc == 0.0:
                f.write(f"- **{num_items} items**: Update to 0% (was 67%, now consistently fails)\n")
            elif middle_acc >= 0.8:
                f.write(f"- **{num_items} items**: Update to {middle_acc:.0%} (mostly reliable, occasional failure)\n")
            elif middle_acc >= 0.4:
                f.write(f"- **{num_items} items**: Keep at 67% (truly inconsistent/random)\n")
            else:
                f.write(f"- **{num_items} items**: Update to {middle_acc:.0%} (mostly fails)\n")

    print(f"\n[SAVE] Results saved to: {filename}")

    # Recommendations
    print("\n" + "+" + "="*68 + "+")
    print("|" + " [RECOMMENDATIONS] ".center(68) + "|")
    print("+" + "="*68 + "+\n")

    for num_items, data in all_results.items():
        pos_results = data["position_results"]
        middle_acc = pos_results["middle"]["accuracy"]

        if middle_acc == 1.0:
            print(f"[OK] {num_items} items: Update to 100% (was 67%, now stable)")
        elif middle_acc == 0.0:
            print(f"[FAIL] {num_items} items: Update to 0% (was 67%, consistent failure)")
        elif middle_acc >= 0.8:
            print(f"[WARN] {num_items} items: Update to {middle_acc:.0%} (mostly reliable)")
        elif middle_acc >= 0.4:
            print(f"[WARN] {num_items} items: Keep 67% (truly inconsistent)")
        else:
            print(f"[FAIL] {num_items} items: Update to {middle_acc:.0%} (mostly fails)")

    print("\n" + "="*70)
    print("[OK] TEST COMPLETED!")
    print("="*70)


if __name__ == "__main__":
    main()
