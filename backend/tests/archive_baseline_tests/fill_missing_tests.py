#!/usr/bin/env python3
"""
Fill Missing Test Points & Retest Suspicious Points

Purpose:
1. Test Mistral at 1250 items (missing data point)
2. Re-test suspicious 67% accuracy points (5 runs each)
3. Determine if 67% is "unstable" or "consistent failure"
"""

import requests
import time
from datetime import datetime
from collections import Counter

def test_position(num_items, position_name, index):
    """Test a single position"""
    # Generate haystack
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

    print(f"\n{'='*60}")
    print(f"Testing {num_items} items ({num_runs} runs)")
    print('='*60)

    # Test positions
    test_positions = [
        (1, "first"),
        (num_items // 2, "middle"),
        (num_items, "last")
    ]

    position_results = {}

    for test_idx, position in test_positions:
        print(f"\n  Position: {position} (index {test_idx})")
        print(f"  {'='*50}")

        results = []

        for run in range(1, num_runs + 1):
            print(f"\n    {'🔄 RUN ' + str(run) + '/' + str(num_runs):=^50}")
            print(f"    Testing...", end=" ")

            correct, content, tokens = test_position(num_items, position, test_idx)

            results.append({
                "run": run,
                "correct": correct,
                "content": content,
                "tokens": tokens
            })

            status = "✅" if correct else "❌"
            print(f"{status} Got: {content[:30]}")

            time.sleep(15)  # Delay between runs (15 seconds for GPU cooldown)

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
            consistency = "✅ STABLE (always correct)"
        elif accuracy == 0.0:
            consistency = "❌ STABLE FAILURE (always wrong)"
        elif accuracy >= 0.8:
            consistency = "⚠️ MOSTLY CORRECT (occasional failure)"
        elif accuracy >= 0.4:
            consistency = "⚠️ INCONSISTENT (random)"
        else:
            consistency = "❌ MOSTLY WRONG (occasional success)"

        print(f"    {position.upper()}: {accuracy:.0%} ({correct_count}/{num_runs}) - {consistency}")

    # Overall accuracy
    overall_correct = sum(pos["correct_count"] for pos in position_results.values())
    overall_total = sum(pos["total_runs"] for pos in position_results.values())
    overall_accuracy = overall_correct / overall_total

    print(f"\n  OVERALL: {overall_accuracy:.0%} ({overall_correct}/{overall_total})")
    print(f"  Avg Tokens: {position_results['middle']['avg_tokens']:.0f}")

    return position_results, overall_accuracy


def main():
    print("="*60)
    print("FILL MISSING TESTS & RETEST SUSPICIOUS POINTS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print("\nTest Plan:")
    print("1. Mistral missing point: 1250 items (5 runs)")
    print("2. Mistral suspicious points: 500, 750, 1200 items (5 runs each)")
    print("3. Magistral suspicious points: 750, 1250 items (5 runs each)")

    # Configuration
    mistral_tests = {
        1250: "Missing data point",
        500: "Previously 67% - verify if consistent",
        750: "Previously 67% - verify if consistent",
        1200: "Previously 67% - verify if consistent"
    }

    magistral_tests = {
        750: "Previously 67% - verify if consistent",
        1250: "Previously 67% - verify if consistent",
        1400: "Previously 67% - verify if consistent"
    }

    # Ask user which model to test
    print("\nWhich model is currently running on localhost:8080?")
    print("1. Mistral 24B Q6_K")
    print("2. Magistral-Small-2506")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("\n🔍 Testing Mistral 24B Q6_K...")
        tests_to_run = mistral_tests
        model_name = "Mistral-24B"
    elif choice == "2":
        print("\n🔍 Testing Magistral-Small-2506...")
        tests_to_run = magistral_tests
        model_name = "Magistral-2506"
    else:
        print("Invalid choice. Exiting.")
        return

    # Run tests
    all_results = {}

    for num_items, description in tests_to_run.items():
        print(f"\n{'='*60}")
        print(f"Test: {num_items} items")
        print(f"Reason: {description}")
        print('='*60)

        position_results, overall_accuracy = test_context_size_multi_run(num_items, num_runs=5)

        all_results[num_items] = {
            "position_results": position_results,
            "overall_accuracy": overall_accuracy,
            "description": description
        }

        print("\n" + "⏸️ "*30)
        print("⏸️  Waiting 15 seconds before next test size...")
        print("⏸️ "*30)
        for i in range(15, 0, -1):
            print(f"⏸️  {i} seconds remaining...", end="\r")
            time.sleep(1)
        print("\n")

    # Final Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    print(f"\nModel: {model_name}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("| Items | Overall Accuracy | Middle Position | Consistency |")
    print("|-------|-----------------|----------------|-------------|")

    for num_items, data in all_results.items():
        overall_acc = data["overall_accuracy"]
        middle_acc = data["position_results"]["middle"]["accuracy"]

        # Determine consistency
        if middle_acc == 1.0 or middle_acc == 0.0:
            consistency = "Stable"
        elif middle_acc >= 0.8:
            consistency = "Mostly OK"
        elif middle_acc >= 0.4:
            consistency = "Random"
        else:
            consistency = "Mostly Fail"

        print(f"| {num_items} | {overall_acc:.0%} ({data['position_results']['first']['correct_count']+data['position_results']['middle']['correct_count']+data['position_results']['last']['correct_count']}/15) | {middle_acc:.0%} ({data['position_results']['middle']['correct_count']}/5) | {consistency} |")

    # Save results
    filename = f"{model_name.lower()}_retest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {model_name} Re-test Results\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Purpose**: Fill missing data points and verify suspicious 67% accuracy points\n\n")

        f.write("## Summary\n\n")
        f.write("| Items | Overall Accuracy | First | Middle | Last | Notes |\n")
        f.write("|-------|-----------------|-------|--------|------|-------|\n")

        for num_items, data in all_results.items():
            pos_results = data["position_results"]
            f.write(f"| {num_items} | {data['overall_accuracy']:.0%} | ")
            f.write(f"{pos_results['first']['accuracy']:.0%} | ")
            f.write(f"{pos_results['middle']['accuracy']:.0%} | ")
            f.write(f"{pos_results['last']['accuracy']:.0%} | ")
            f.write(f"{data['description']} |\n")

        f.write("\n## Detailed Results\n\n")

        for num_items, data in all_results.items():
            f.write(f"### {num_items} Items\n\n")
            f.write(f"**Purpose**: {data['description']}\n\n")

            for position, pos_data in data["position_results"].items():
                f.write(f"**{position.upper()} Position**:\n")
                f.write(f"- Accuracy: {pos_data['accuracy']:.0%} ({pos_data['correct_count']}/{pos_data['total_runs']})\n")
                f.write(f"- Results: ")

                for r in pos_data["results"]:
                    status = "✅" if r["correct"] else "❌"
                    f.write(f"{status} ")

                f.write("\n\n")

    print(f"\nResults saved to: {filename}")

    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)

    for num_items, data in all_results.items():
        middle_acc = data["position_results"]["middle"]["accuracy"]

        if middle_acc == 1.0:
            print(f"\n✅ {num_items} items: Update to 100% (was 67%, now stable)")
        elif middle_acc == 0.0:
            print(f"\n❌ {num_items} items: Update to 0% (was 67%, consistent failure)")
        elif middle_acc >= 0.8:
            print(f"\n⚠️ {num_items} items: Update to {middle_acc:.0%} (mostly reliable)")
        elif middle_acc >= 0.4:
            print(f"\n⚠️ {num_items} items: Keep 67% (truly inconsistent)")
        else:
            print(f"\n❌ {num_items} items: Update to {middle_acc:.0%} (mostly fails)")


if __name__ == "__main__":
    main()
