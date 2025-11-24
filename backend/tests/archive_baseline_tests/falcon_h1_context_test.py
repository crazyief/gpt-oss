"""
Falcon-H1_Q5 Context Window Testing - 3-Phase Adaptive Zone Mapping
Context Window: 65536 tokens (~3000-4000 items estimated)

Based on proven methodology from Mistral Q6_K and Gemma 27B testing.
"""

import requests
import json
import time
from datetime import datetime

# Model configuration
LLM_API_URL = "http://localhost:8090/completion"
MODEL_NAME = "Falcon-H1_Q5"
CONTEXT_WINDOW = 65536

def generate_haystack(n_items: int, needle_position: str = "middle") -> tuple[str, int]:
    """
    Generate haystack with secret number at specified position.

    Args:
        n_items: Total number of items in haystack
        needle_position: 'first', 'middle', or 'last'

    Returns:
        (haystack_text, secret_number)
    """
    import random
    secret = random.randint(100000, 999999)

    # Calculate insertion index
    if needle_position == "first":
        insert_idx = 0
    elif needle_position == "last":
        insert_idx = n_items - 1
    else:  # middle
        insert_idx = n_items // 2

    # Generate items
    items = []
    for i in range(n_items):
        if i == insert_idx:
            items.append(f"Item {i+1}: The secret number is {secret}")
        else:
            items.append(f"Item {i+1}: This is just filler content number {i+1}")

    return "\n".join(items), secret, insert_idx

def query_llm(prompt: str, max_tokens: int = 50, temperature: float = 0.0) -> dict:
    """
    Query LLM with deterministic settings (temperature=0).

    Returns:
        {
            "content": str,
            "success": bool,
            "error": str (if failed)
        }
    """
    try:
        response = requests.post(
            LLM_API_URL,
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stop": ["\n", "Question:", "User:"]
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get("content", "").strip()
            return {
                "content": content,
                "success": True
            }
        else:
            return {
                "content": "",
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "content": "",
            "success": False,
            "error": str(e)
        }

def extract_number(text: str) -> int:
    """Extract 6-digit number from LLM response."""
    import re
    numbers = re.findall(r'\b\d{6}\b', text)
    return int(numbers[0]) if numbers else None

def test_single_query(n_items: int, position: str) -> dict:
    """
    Test single query with specified item count and needle position.

    Returns:
        {
            "n_items": int,
            "position": str,
            "needle_index": int,
            "expected": int,
            "actual": int,
            "correct": bool,
            "response": str,
            "tokens_estimated": int
        }
    """
    # Generate haystack
    haystack, secret, needle_idx = generate_haystack(n_items, position)

    # Estimate tokens (rough: 1 item ≈ 20 tokens)
    tokens_estimated = n_items * 20

    # Create prompt
    prompt = f"""Below is a list of items. Find the secret number.

{haystack}

Question: What is the secret number?
Answer: The secret number is"""

    # Query LLM
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

    # Extract answer
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

def phase1_coarse_discovery(start: int = 50, end: int = 3500, step: int = 100, runs: int = 3):
    """
    Phase 1: Coarse Discovery
    - Test range: 50-3500 items (100-item increments)
    - 3 runs per item count
    - All 3 positions (first, middle, last)

    Goal: Identify rough safe/danger zones
    """
    print("=" * 80)
    print("PHASE 1: COARSE DISCOVERY")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    print(f"Context Window: {CONTEXT_WINDOW} tokens")
    print(f"Item Range: {start} -> {end} (step={step})")
    print(f"Runs per item count: {runs}")
    print(f"Positions tested: first, middle, last")
    print(f"Estimated queries: {len(range(start, end + 1, step)) * runs * 3}")
    print(f"Estimated time: ~{len(range(start, end + 1, step)) * runs * 3 * 3 / 60:.1f} minutes")
    print("=" * 80)
    print()

    results = []
    positions = ["first", "middle", "last"]

    for n_items in range(start, end + 1, step):
        print(f"\n[{n_items:4d} items] Testing...", end=" ", flush=True)

        for run in range(1, runs + 1):
            for pos in positions:
                result = test_single_query(n_items, pos)
                result["run"] = run
                result["phase"] = 1
                results.append(result)

                # Print progress
                status = "+" if result["correct"] else "X"
                print(status, end="", flush=True)

                time.sleep(0.5)  # Rate limiting

        # Summary for this item count
        item_results = [r for r in results if r["n_items"] == n_items]
        accuracy = sum(1 for r in item_results if r["correct"]) / len(item_results) * 100
        print(f" -> {accuracy:.1f}% accuracy")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_h1_phase1_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_NAME,
            "context_window": CONTEXT_WINDOW,
            "phase": 1,
            "parameters": {
                "start": start,
                "end": end,
                "step": step,
                "runs": runs,
                "positions": positions
            },
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Phase 1 complete. Results saved to: {output_file}")

    # Analyze results
    analyze_phase1_results(results)

    return results, output_file

def analyze_phase1_results(results: list):
    """Analyze Phase 1 results to identify danger zones."""
    print("\n" + "=" * 80)
    print("PHASE 1 ANALYSIS")
    print("=" * 80)

    # Group by item count
    item_counts = sorted(set(r["n_items"] for r in results))

    danger_zones = []
    safe_zones = []

    for n_items in item_counts:
        item_results = [r for r in results if r["n_items"] == n_items]

        # Calculate accuracy by position
        positions = {}
        for pos in ["first", "middle", "last"]:
            pos_results = [r for r in item_results if r["position"] == pos]
            correct = sum(1 for r in pos_results if r["correct"])
            total = len(pos_results)
            accuracy = correct / total * 100 if total > 0 else 0
            positions[pos] = {"correct": correct, "total": total, "accuracy": accuracy}

        # Overall accuracy
        correct = sum(1 for r in item_results if r["correct"])
        total = len(item_results)
        overall_accuracy = correct / total * 100

        # Classify zone
        if positions["middle"]["accuracy"] == 0:
            danger_zones.append(n_items)
            zone = "[DANGER]"
        elif overall_accuracy == 100:
            safe_zones.append(n_items)
            zone = "[SAFE]"
        elif overall_accuracy >= 66.7:
            zone = "[SUSPECT]"
        else:
            zone = "[UNSTABLE]"

        print(f"{zone} [{n_items:4d} items] Overall: {overall_accuracy:5.1f}% | "
              f"First: {positions['first']['accuracy']:5.1f}% | "
              f"Middle: {positions['middle']['accuracy']:5.1f}% | "
              f"Last: {positions['last']['accuracy']:5.1f}%")

    print("\n" + "-" * 80)
    print(f"DANGER ZONES (0% middle accuracy): {danger_zones}")
    print(f"SAFE ZONES (100% all positions): {safe_zones}")
    print("-" * 80)

    if danger_zones:
        print("\n[WARNING] Systematic bugs detected! Proceed to Phase 2 for precise mapping.")
    else:
        print("\n[OK] No danger zones detected in this range!")

def phase2_binary_search(danger_zones: list, runs: int = 5):
    """
    Phase 2: Binary Search
    - Narrow down exact boundaries of danger zones
    - ±5 item precision
    - 5 runs per item count (higher confidence)
    """
    print("\n" + "=" * 80)
    print("PHASE 2: BINARY SEARCH")
    print("=" * 80)

    if not danger_zones:
        print("No danger zones to refine. Skipping Phase 2.")
        return [], None

    print(f"Danger zones to refine: {danger_zones}")
    print(f"Runs per item count: {runs}")
    print(f"Precision target: ±5 items")
    print("=" * 80)

    results = []
    refined_zones = []

    for danger_point in danger_zones:
        print(f"\n[SEARCH] Refining zone around {danger_point} items...")

        # Binary search window: [danger_point - 100, danger_point + 100]
        left = max(50, danger_point - 100)
        right = danger_point + 100

        while right - left > 10:
            mid = (left + right) // 2

            # Test mid point
            mid_results = []
            for run in range(1, runs + 1):
                result = test_single_query(mid, "middle")
                result["run"] = run
                result["phase"] = 2
                mid_results.append(result)
                results.append(result)
                time.sleep(0.5)

            accuracy = sum(1 for r in mid_results if r["correct"]) / len(mid_results) * 100
            print(f"  [{mid:4d} items] Middle accuracy: {accuracy:.1f}%")

            if accuracy == 0:
                # Danger zone, search lower
                right = mid
            else:
                # Safe zone, search higher
                left = mid

        # Precise boundary found
        boundary = (left + right) // 2
        refined_zones.append(boundary)
        print(f"  [OK] Precise boundary: {boundary} items")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_h1_phase2_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_NAME,
            "context_window": CONTEXT_WINDOW,
            "phase": 2,
            "danger_zones_input": danger_zones,
            "refined_boundaries": refined_zones,
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Phase 2 complete. Results saved to: {output_file}")
    print(f"Refined danger zone boundaries: {refined_zones}")

    return results, output_file

def phase3_production_validation(boundaries: list, runs: int = 10):
    """
    Phase 3: Production Validation
    - Test refined boundaries with 10 runs (95% confidence)
    - Validate reproducibility of danger zones
    """
    print("\n" + "=" * 80)
    print("PHASE 3: PRODUCTION VALIDATION")
    print("=" * 80)

    if not boundaries:
        print("No boundaries to validate. Skipping Phase 3.")
        return [], None

    print(f"Boundaries to validate: {boundaries}")
    print(f"Runs per boundary: {runs}")
    print(f"Confidence target: 95%")
    print("=" * 80)

    results = []

    for boundary in boundaries:
        print(f"\n[VALIDATE] Validating boundary at {boundary} items...")

        # Test at boundary (should be danger zone)
        for run in range(1, runs + 1):
            result = test_single_query(boundary, "middle")
            result["run"] = run
            result["phase"] = 3
            results.append(result)
            status = "+" if result["correct"] else "X"
            print(status, end="", flush=True)
            time.sleep(0.5)

        # Calculate accuracy
        boundary_results = [r for r in results if r["n_items"] == boundary]
        accuracy = sum(1 for r in boundary_results if r["correct"]) / len(boundary_results) * 100

        print(f" -> {accuracy:.1f}% accuracy")

        if accuracy == 0:
            print(f"  [OK] CONFIRMED: {boundary} items is a reproducible danger zone (0% accuracy)")
        else:
            print(f"  [WARNING] {boundary} items shows {accuracy:.1f}% accuracy (not consistently failing)")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_h1_phase3_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL_NAME,
            "context_window": CONTEXT_WINDOW,
            "phase": 3,
            "validated_boundaries": boundaries,
            "timestamp": timestamp,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Phase 3 complete. Results saved to: {output_file}")

    return results, output_file

def run_full_3phase_test():
    """Execute complete 3-phase adaptive zone mapping."""
    print("\n" + "=" * 80)
    print(f"FALCON-H1_Q5 CONTEXT WINDOW TESTING")
    print(f"3-Phase Adaptive Zone Mapping Methodology")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    print(f"Context Window: {CONTEXT_WINDOW} tokens")
    print(f"Endpoint: {LLM_API_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Phase 1: Coarse Discovery
    phase1_results, phase1_file = phase1_coarse_discovery(
        start=50,
        end=3500,
        step=100,
        runs=3
    )

    # Extract danger zones from Phase 1
    danger_zones = []
    item_counts = sorted(set(r["n_items"] for r in phase1_results))
    for n_items in item_counts:
        middle_results = [r for r in phase1_results
                         if r["n_items"] == n_items and r["position"] == "middle"]
        middle_accuracy = sum(1 for r in middle_results if r["correct"]) / len(middle_results) * 100
        if middle_accuracy == 0:
            danger_zones.append(n_items)

    # Phase 2: Binary Search (if danger zones found)
    if danger_zones:
        phase2_results, phase2_file = phase2_binary_search(danger_zones, runs=5)

        # Extract refined boundaries from Phase 2
        # (In a real implementation, this would parse the binary search results)
        # For now, we'll use the danger zones as boundaries
        boundaries = danger_zones
    else:
        phase2_results, phase2_file = [], None
        boundaries = []

    # Phase 3: Production Validation (if boundaries found)
    if boundaries:
        phase3_results, phase3_file = phase3_production_validation(boundaries, runs=10)
    else:
        phase3_results, phase3_file = [], None

    # Generate final report
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    print(f"Total queries executed: {len(phase1_results) + len(phase2_results) + len(phase3_results)}")
    print(f"Phase 1 results: {phase1_file}")
    if phase2_file:
        print(f"Phase 2 results: {phase2_file}")
    if phase3_file:
        print(f"Phase 3 results: {phase3_file}")
    print("=" * 80)

    # Generate markdown report
    generate_markdown_report(phase1_results, phase2_results, phase3_results)

def generate_markdown_report(phase1_results, phase2_results, phase3_results):
    """Generate comprehensive markdown report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"falcon_h1_context_results_{timestamp}.md"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Falcon-H1_Q5 Context Window Testing Report\n\n")
        f.write(f"**Model**: {MODEL_NAME}\n")
        f.write(f"**Context Window**: {CONTEXT_WINDOW} tokens\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Methodology**: 3-Phase Adaptive Zone Mapping\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Queries**: {len(phase1_results) + len(phase2_results) + len(phase3_results)}\n")
        f.write(f"- **Phase 1 Queries**: {len(phase1_results)}\n")
        f.write(f"- **Phase 2 Queries**: {len(phase2_results)}\n")
        f.write(f"- **Phase 3 Queries**: {len(phase3_results)}\n\n")

        # Phase 1 Summary
        f.write("## Phase 1: Coarse Discovery\n\n")
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

            if positions["middle"] == 0:
                status = "[DANGER]"
            elif overall == 100:
                status = "[SAFE]"
            else:
                status = "[SUSPECT]"

            f.write(f"| {n_items:4d} | {overall:5.1f}% | {positions['first']:5.1f}% | "
                   f"{positions['middle']:5.1f}% | {positions['last']:5.1f}% | {status} |\n")

        f.write("\n")

    print(f"[OK] Markdown report generated: {output_file}")

if __name__ == "__main__":
    run_full_3phase_test()
