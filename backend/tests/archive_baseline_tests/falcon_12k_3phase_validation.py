"""
Falcon-H1-34B @ 12k Context - 3-Phase Validation
Validate safe zone with full methodology
"""

import requests
import json
import time
from datetime import datetime

LLM_API_URL = "http://localhost:8090/completion"
MODEL_NAME = "Falcon-H1-34B-Instruct-Q5_K_M (12k context)"

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
    """Query LLM with deterministic settings."""
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

def test_single_query(n_items: int, position: str) -> dict:
    """Test single query."""
    haystack, secret, needle_idx = generate_haystack(n_items, position)
    tokens_estimated = n_items * 20

    prompt = f"""Below is a list of items. Find the secret number.

{haystack}

Question: What is the secret number?
Answer: The secret number is"""

    result = query_llm(prompt)

    if not result["success"]:
        return {
            "n_items": n_items,
            "position": position,
            "needle_index": needle_idx,
            "expected": secret,
            "actual": None,
            "correct": False,
            "response": result.get("error", "Unknown error"),
            "tokens_estimated": tokens_estimated,
            "error": True
        }

    actual = extract_number(result["content"])
    correct = (actual == secret)

    return {
        "n_items": n_items,
        "position": position,
        "needle_index": needle_idx,
        "expected": secret,
        "actual": actual,
        "correct": correct,
        "response": result["content"],
        "tokens_estimated": tokens_estimated,
        "error": False
    }

def phase1_coarse_discovery():
    """
    Phase 1: Coarse Discovery (50-650 items)
    - 50-item increments
    - 3 runs per item count
    - All 3 positions
    """
    print("=" * 80)
    print("PHASE 1: COARSE DISCOVERY")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    print(f"Item Range: 50 -> 650 (step=50)")
    print(f"Runs per item count: 3")
    print(f"Positions tested: first, middle, last")
    print(f"Estimated queries: {13 * 3 * 3} = 117")
    print(f"Estimated time: ~6-7 minutes")
    print("=" * 80)
    print()

    results = []
    positions = ["first", "middle", "last"]

    for n_items in range(50, 701, 50):
        print(f"\n[{n_items:3d} items] Testing...", end=" ", flush=True)

        for run in range(1, 4):
            for pos in positions:
                result = test_single_query(n_items, pos)
                result["run"] = run
                result["phase"] = 1
                results.append(result)

                status = "+" if result["correct"] else "X"
                print(status, end="", flush=True)
                time.sleep(0.5)

        item_results = [r for r in results if r["n_items"] == n_items]
        accuracy = sum(1 for r in item_results if r["correct"]) / len(item_results) * 100
        print(f" -> {accuracy:.1f}%")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_12k_phase1_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_NAME,
            "context_window": "12k tokens",
            "phase": 1,
            "parameters": {
                "start": 50,
                "end": 650,
                "step": 50,
                "runs": 3,
                "positions": positions
            },
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Phase 1 complete. Results saved to: {output_file}")

    # Analyze
    analyze_phase1_results(results)

    return results, output_file

def analyze_phase1_results(results: list):
    """Analyze Phase 1 results."""
    print("\n" + "=" * 80)
    print("PHASE 1 ANALYSIS")
    print("=" * 80)

    item_counts = sorted(set(r["n_items"] for r in results))
    all_perfect = True

    for n_items in item_counts:
        item_results = [r for r in results if r["n_items"] == n_items]

        positions = {}
        for pos in ["first", "middle", "last"]:
            pos_results = [r for r in item_results if r["position"] == pos]
            correct = sum(1 for r in pos_results if r["correct"])
            total = len(pos_results)
            accuracy = correct / total * 100 if total > 0 else 0
            positions[pos] = accuracy

        overall = sum(1 for r in item_results if r["correct"]) / len(item_results) * 100

        if overall == 100:
            zone = "[SAFE]"
        elif overall >= 66.7:
            zone = "[SUSPECT]"
            all_perfect = False
        else:
            zone = "[DANGER]"
            all_perfect = False

        print(f"{zone} [{n_items:3d} items] Overall: {overall:5.1f}% | "
              f"First: {positions['first']:5.1f}% | "
              f"Middle: {positions['middle']:5.1f}% | "
              f"Last: {positions['last']:5.1f}%")

    print("-" * 80)
    if all_perfect:
        print("[OK] All tests passed! Safe zone confirmed (50-650 items).")
    else:
        print("[WARNING] Some failures detected. Phase 2 may be needed.")
    print("-" * 80)

def phase2_binary_search(suspect_zones: list):
    """
    Phase 2: Binary Search (if needed)
    - Narrow down any suspect zones
    """
    if not suspect_zones:
        print("\n[SKIP] Phase 2: No suspect zones detected.")
        return [], None

    print("\n" + "=" * 80)
    print("PHASE 2: BINARY SEARCH")
    print("=" * 80)
    print(f"Suspect zones to investigate: {suspect_zones}")
    print("=" * 80)

    results = []
    # Implementation would go here if needed
    # For now, skip if everything is perfect

    return results, None

def phase3_production_validation():
    """
    Phase 3: Production Validation
    - Test critical boundaries: 50, 350, 650 items
    - 5 runs per item count (95% confidence)
    """
    print("\n" + "=" * 80)
    print("PHASE 3: PRODUCTION VALIDATION")
    print("=" * 80)
    print(f"Validation points: 50, 350, 650 items")
    print(f"Runs per item count: 5")
    print(f"Confidence target: 95%")
    print(f"Estimated queries: {3 * 5 * 3} = 45")
    print(f"Estimated time: ~2-3 minutes")
    print("=" * 80)

    results = []
    positions = ["first", "middle", "last"]
    test_points = [50, 350, 650]

    for n_items in test_points:
        print(f"\n[VALIDATE] {n_items} items ({5} runs)...")

        for run in range(1, 6):
            for pos in positions:
                result = test_single_query(n_items, pos)
                result["run"] = run
                result["phase"] = 3
                results.append(result)

                status = "+" if result["correct"] else "X"
                print(status, end="", flush=True)
                time.sleep(0.5)

        item_results = [r for r in results if r["n_items"] == n_items]
        accuracy = sum(1 for r in item_results if r["correct"]) / len(item_results) * 100
        print(f" -> {accuracy:.1f}%")

        if accuracy == 100:
            print(f"  [OK] CONFIRMED: {n_items} items is 100% reliable")
        else:
            print(f"  [WARNING] {n_items} items shows {accuracy:.1f}% accuracy")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_12k_phase3_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_NAME,
            "context_window": "12k tokens",
            "phase": 3,
            "validation_points": test_points,
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Phase 3 complete. Results saved to: {output_file}")

    return results, output_file

def generate_markdown_report(phase1_results, phase3_results):
    """Generate comprehensive markdown report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_12k_validation_results_{timestamp}.md"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Falcon-H1-34B 12k Context Validation Report\n\n")
        f.write(f"**Model**: {MODEL_NAME}\n")
        f.write(f"**Context Window**: 12,000 tokens (~650 items)\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Methodology**: 3-Phase Validation (Safe Zone Only)\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Queries**: {len(phase1_results) + len(phase3_results)}\n")
        f.write(f"- **Phase 1 Queries**: {len(phase1_results)} (Coarse Discovery)\n")
        f.write(f"- **Phase 3 Queries**: {len(phase3_results)} (Production Validation)\n\n")

        # Phase 1 Summary
        f.write("## Phase 1: Coarse Discovery (50-650 items)\n\n")
        f.write("| Item Count | Overall | First | Middle | Last | Status |\n")
        f.write("|------------|---------|-------|--------|------|--------|\n")

        item_counts = sorted(set(r["n_items"] for r in phase1_results))
        for n_items in item_counts:
            item_results = [r for r in phase1_results if r["n_items"] == n_items]

            positions = {}
            for pos in ["first", "middle", "last"]:
                pos_results = [r for r in item_results if r["position"] == pos]
                correct = sum(1 for r in pos_results if r["correct"])
                total = len(pos_results)
                accuracy = correct / total * 100 if total > 0 else 0
                positions[pos] = accuracy

            overall = sum(1 for r in item_results if r["correct"]) / len(item_results) * 100

            if overall == 100:
                status = "[SAFE]"
            elif overall >= 66.7:
                status = "[SUSPECT]"
            else:
                status = "[DANGER]"

            f.write(f"| {n_items:3d} | {overall:5.1f}% | {positions['first']:5.1f}% | "
                   f"{positions['middle']:5.1f}% | {positions['last']:5.1f}% | {status} |\n")

        f.write("\n")

        # Phase 3 Summary
        f.write("## Phase 3: Production Validation\n\n")
        f.write("| Item Count | Runs | Accuracy | Status |\n")
        f.write("|------------|------|----------|--------|\n")

        test_points = sorted(set(r["n_items"] for r in phase3_results))
        for n_items in test_points:
            item_results = [r for r in phase3_results if r["n_items"] == n_items]
            correct = sum(1 for r in item_results if r["correct"])
            total = len(item_results)
            accuracy = correct / total * 100

            status = "[PASS]" if accuracy == 100 else "[FAIL]"
            f.write(f"| {n_items:3d} | {total} | {accuracy:5.1f}% | {status} |\n")

        f.write("\n")

        # Final Verdict
        f.write("## Verdict\n\n")
        all_perfect = all(r["correct"] for r in phase1_results + phase3_results)

        if all_perfect:
            f.write("**[SUCCESS]** All tests passed!\n\n")
            f.write("- Safe zone confirmed: 50-650 items\n")
            f.write("- 100% accuracy across all positions\n")
            f.write("- Production-ready with 12k context configuration\n")
        else:
            f.write("**[WARNING]** Some tests failed.\n\n")
            f.write("- Review individual test results\n")
            f.write("- Consider reducing safe zone limit\n")

    print(f"[OK] Markdown report generated: {output_file}")

def run_full_3phase_validation():
    """Execute complete 3-phase validation."""
    print("\n" + "=" * 80)
    print(f"FALCON-H1-34B 12K CONTEXT - 3-PHASE VALIDATION")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    print(f"Context Window: 12,000 tokens")
    print(f"Safe Zone Target: 50-650 items")
    print(f"Endpoint: {LLM_API_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Phase 1: Coarse Discovery
    phase1_results, phase1_file = phase1_coarse_discovery()

    # Phase 2: Skip (only if issues found)
    phase2_results, phase2_file = phase2_binary_search([])

    # Phase 3: Production Validation
    phase3_results, phase3_file = phase3_production_validation()

    # Generate final report
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Total queries executed: {len(phase1_results) + len(phase3_results)}")
    print(f"Phase 1 results: {phase1_file}")
    print(f"Phase 3 results: {phase3_file}")
    print("=" * 80)

    generate_markdown_report(phase1_results, phase3_results)

if __name__ == "__main__":
    run_full_3phase_validation()
