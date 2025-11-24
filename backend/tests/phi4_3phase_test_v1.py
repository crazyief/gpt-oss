"""
PHI-4-REASONING-PLUS 3-PHASE CONTEXT VALIDATION - VERSION 1
============================================================

TEST METHOD VERSION: v1.0
CREATED: 2025-11-22
METHODOLOGY: Random Entry IDs (no sequential numbering)

IMPROVEMENTS OVER BASELINE:
- Random 8-character alphanumeric IDs (prevents positional encoding exploitation)
- Token counting with safety margins
- Version tracking in all outputs
- Enhanced result metadata

BASED ON: Super-AI-UltraThink recommendations for test validity
"""

import requests
import random
import time
import subprocess
import json
import re
import string
from typing import Tuple, Optional
from datetime import datetime

# ============================================================================
# TEST METADATA
# ============================================================================

TEST_VERSION = "v1.0"
TEST_METHOD_NAME = "3-Phase Test v1"
METHODOLOGY = "Random Entry IDs"

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_NAME = "Phi-4-reasoning-plus-Q8_0"
LLM_URL = "http://localhost:8090/completion"
CONTEXT_SIZE = 12000  # Will be overridden by command-line argument

# Safety margins based on Super-AI analysis
SAFETY_MARGIN = 0.85  # Use only 85% of context window
OVERHEAD_TOKENS = 150  # System prompt + user wrapper
TOKENS_PER_ITEM = 15  # Estimated tokens per entry

# Thermal Management (Optimized)
THERMAL_CONFIG = {
    "query_delay": 1,              # 1s between each query
    "batch_delay": 15,             # 15s after every 10 queries
    "phase_delay": 30,             # 30s between Phase 1 and Phase 3
    "temp_check_interval": 10,     # Check temp every 10 queries
    "temp_threshold_pause": 78,    # Pause if temp > 78C
    "temp_threshold_abort": 85,    # Abort if temp > 85C
}

# Phase 1: Coarse Discovery
PHASE1_ITEM_RANGE = range(50, 1550, 50)  # 50, 100, 150, ..., 1500
PHASE1_RUNS_PER_ITEM = 3
PHASE1_POSITIONS = ["first", "middle", "last"]

# Tracking
query_count = 0

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_safe_item_count(context_size: int) -> int:
    """Calculate safe maximum item count based on context size.

    Uses 85% safety margin to prevent context overflow.

    Args:
        context_size: Total context window size in tokens

    Returns:
        Safe maximum number of items
    """
    usable_tokens = int(context_size * SAFETY_MARGIN) - OVERHEAD_TOKENS
    return usable_tokens // TOKENS_PER_ITEM

def generate_entry_id() -> str:
    """Generate random 8-character alphanumeric entry ID.

    Format: XXXXXXXX (uppercase letters + digits)
    Example: X7K9M2P4

    Returns:
        8-character random ID
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ============================================================================
# GPU MONITORING
# ============================================================================

def get_gpu_stats() -> Tuple[Optional[float], Optional[float], Optional[int], Optional[int], Optional[float]]:
    """Query GPU temperature, power, and VRAM usage.

    Returns:
        (temp_c, power_w, vram_used_mb, vram_total_mb, vram_percent)
    """
    try:
        result = subprocess.run(
            ['nvidia-smi', '--id=1', '--query-gpu=temperature.gpu,power.draw,memory.used,memory.total',
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if lines and lines[0].strip():
            parts = lines[0].strip().split(',')
            if len(parts) >= 4:
                temp = float(parts[0].strip())
                power = float(parts[1].strip())
                vram_used = int(parts[2].strip())
                vram_total = int(parts[3].strip())
                vram_percent = (vram_used / vram_total * 100) if vram_total > 0 else 0
                return temp, power, vram_used, vram_total, vram_percent
    except Exception as e:
        pass

    return None, None, None, None, None

def adaptive_thermal_throttling():
    """Check GPU temp and apply cooling if needed."""
    global query_count

    if query_count % THERMAL_CONFIG["temp_check_interval"] != 0:
        return

    temp, power, vram_used, vram_total, vram_percent = get_gpu_stats()

    if temp is None:
        return

    timestamp = datetime.now().strftime('%H:%M:%S')

    if temp >= THERMAL_CONFIG["temp_threshold_abort"]:
        status = f"RED CRITICAL: {temp}C / {power:.1f}W / VRAM: {vram_used}MB ({vram_percent:.1f}%)"
        print(f"    [{timestamp}] Query {query_count} - {status}")
        print("    PAUSE Emergency 5 min cooling...")
        time.sleep(300)
    elif temp >= THERMAL_CONFIG["temp_threshold_pause"]:
        status = f"ORANGE HOT: {temp}C / {power:.1f}W / VRAM: {vram_used}MB ({vram_percent:.1f}%)"
        print(f"    [{timestamp}] Query {query_count} - {status}")
        print("    PAUSE  Extended 2 min cooling...")
        time.sleep(120)
    elif temp >= 75:
        status = f"YELLOW WARM: {temp}C / {power:.1f}W / VRAM: {vram_used}MB ({vram_percent:.1f}%)"
        print(f"    [{timestamp}] Query {query_count} - {status}")
        print("    PAUSE  Brief 45s cooling...")
        time.sleep(45)
    else:
        status = f"GREEN NORMAL: {temp}C / {power:.1f}W / VRAM: {vram_used}MB ({vram_percent:.1f}%)"
        print(f"    [{timestamp}] Query {query_count} - {status}")

# ============================================================================
# SECRET GENERATION
# ============================================================================

def generate_secret() -> str:
    """Generate 6-digit cryptographic secret."""
    return str(random.randint(100000, 999999))

# ============================================================================
# CONTEXT BUILDING (v1: Random Entry IDs)
# ============================================================================

def build_context(n_items: int, secret_position: str) -> Tuple[str, str, list]:
    """Build haystack context with hidden secret using random entry IDs.

    Args:
        n_items: Total number of items in context
        secret_position: 'first', 'middle', or 'last'

    Returns:
        (context_text, secret_number, list_of_entry_ids)
    """
    secret = generate_secret()
    items = []
    entry_ids = []

    for i in range(n_items):
        entry_id = generate_entry_id()
        entry_ids.append(entry_id)

        if secret_position == 'first' and i == 0:
            items.append(f"Entry-{entry_id}: The target code is {secret}.")
        elif secret_position == 'middle' and i == n_items // 2:
            items.append(f"Entry-{entry_id}: The target code is {secret}.")
        elif secret_position == 'last' and i == n_items - 1:
            items.append(f"Entry-{entry_id}: The target code is {secret}.")
        else:
            items.append(f"Entry-{entry_id}: This is a standard entry with no special information.")

    context = "\n".join(items)
    return context, secret, entry_ids

# ============================================================================
# ANSWER EXTRACTION
# ============================================================================

def extract_answer_robust(response_text: str) -> str:
    """Extract 6-digit number from Phi-4 response with multiple fallback methods.

    Methods:
    1. Look for "Final answer:" pattern
    2. Skip <think> block and find number after it
    3. Fallback to any 6-digit number in response

    Args:
        response_text: Raw response from model

    Returns:
        Extracted 6-digit number or empty string
    """
    if not response_text:
        return ""

    # Method 1: Look for "Final answer:" pattern
    match = re.search(r'Final answer:\s*(\d{6})', response_text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Method 2: Skip <think> block and find number after </think>
    think_end = response_text.find('</think>')
    if think_end != -1:
        after_think = response_text[think_end + 8:]
        match = re.search(r'\b(\d{6})\b', after_think)
        if match:
            return match.group(1)

    # Method 3: Fallback - find ANY 6-digit number
    match = re.search(r'\b(\d{6})\b', response_text)
    if match:
        return match.group(1)

    return ""

# ============================================================================
# LLM QUERY
# ============================================================================

def query_phi4(context: str, secret: str) -> Tuple[str, float, bool]:
    """Query Phi-4-reasoning-plus using official ChatML format.

    Args:
        context: Haystack text with embedded secret
        secret: Expected 6-digit number

    Returns:
        (extracted_answer, elapsed_seconds, success)
    """
    global query_count
    query_count += 1

    # Official Phi-4-reasoning-plus ChatML format with <|im_sep|>
    prompt = f"""<|im_start|>system<|im_sep|>You are Phi, a language model trained by Microsoft. For this task, you need to find and extract specific information from the provided context.

Please structure your response into two sections:
<think>
Brief analysis of where you found the information
</think>
Final answer: [the extracted value only]<|im_end|>
<|im_start|>user<|im_sep|>Find the 6-digit target code in the following context and return it in the format specified:

{context}

What is the 6-digit target code?<|im_end|>
<|im_start|>assistant<|im_sep|>"""

    payload = {
        "prompt": prompt,
        "n_predict": 200,
        "temperature": 0.1,
        "top_p": 0.95,
        "stop": ["<|im_end|>", "\n\nUser:", "\n\nEntry"]
    }

    start_time = time.time()

    try:
        response = requests.post(LLM_URL, json=payload, timeout=120)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            return "", elapsed, False

        data = response.json()
        raw_response = data.get("content", "")

        # Extract answer using robust multi-method extraction
        extracted = extract_answer_robust(raw_response)

        success = (extracted == secret)

        return extracted, elapsed, success

    except requests.Timeout:
        elapsed = time.time() - start_time
        return "", elapsed, False
    except Exception as e:
        elapsed = time.time() - start_time
        return "", elapsed, False

# ============================================================================
# PHASE 1: COARSE DISCOVERY
# ============================================================================

def run_phase1():
    """Phase 1: Coarse discovery to find safe zone."""
    print("\n" + "=" * 80)
    print("PHASE 1: COARSE DISCOVERY")
    print("=" * 80)
    print(f"Test Version: {TEST_VERSION}")
    print(f"Methodology: {METHODOLOGY}")
    print(f"Model: {MODEL_NAME} ({CONTEXT_SIZE//1000}k context)")
    print(f"Item Range: {PHASE1_ITEM_RANGE.start} -> {PHASE1_ITEM_RANGE.stop} (step={PHASE1_ITEM_RANGE.step})")
    print(f"Runs per item count: {PHASE1_RUNS_PER_ITEM}")
    print(f"Positions tested: {', '.join(PHASE1_POSITIONS)}")
    print(f"Safe item limit: {calculate_safe_item_count(CONTEXT_SIZE)} items (85% safety margin)")
    print("=" * 80)

    results = []
    consecutive_failures = 0

    # Pre-test thermal check
    print("\n[TEMP] Pre-test thermal check...")
    adaptive_thermal_throttling()

    for n_items in PHASE1_ITEM_RANGE:
        print(f"\n[{n_items:4d} items] Testing... ", end='', flush=True)

        item_results = []

        for run in range(1, PHASE1_RUNS_PER_ITEM + 1):
            for position in PHASE1_POSITIONS:
                # Build context and query
                context, secret, entry_ids = build_context(n_items, position)
                answer, elapsed, success = query_phi4(context, secret)

                # Record result with version metadata
                item_results.append({
                    "test_version": TEST_VERSION,
                    "methodology": METHODOLOGY,
                    "n_items": n_items,
                    "run": run,
                    "position": position,
                    "secret": secret,
                    "answer": answer,
                    "success": success,
                    "elapsed": elapsed,
                    "entry_id_sample": entry_ids[0] if entry_ids else None  # First ID as sample
                })

                # Progress indicator
                print("-" if success else "X", end='', flush=True)

                # Thermal management
                adaptive_thermal_throttling()

                # Brief delay
                time.sleep(THERMAL_CONFIG["query_delay"])

            # Batch cooling
            if query_count % 10 == 0:
                print(f"\n    CYCLE  Batch cooling: {THERMAL_CONFIG['batch_delay']}s\n")
                time.sleep(THERMAL_CONFIG["batch_delay"])

        results.extend(item_results)

        # Calculate accuracy for this item count
        successes = sum(1 for r in item_results if r["success"])
        accuracy = (successes / len(item_results) * 100) if item_results else 0
        print(f" -> {accuracy:.1f}%")

        # Check for consecutive failures (early stopping)
        if accuracy == 0:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                print(f"\n[WARN]  Stopping: 3 consecutive failures detected")
                break
        else:
            consecutive_failures = 0

    print("\n" + "=" * 80)
    print(f"Phase 1 Complete - Tested {len(results)} queries")
    print("=" * 80)

    # IMMEDIATE SAVE with progress logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    phase1_file = f"phi4_{CONTEXT_SIZE//1000}k_v1_phase1_{timestamp}.json"

    with open(phase1_file, 'w') as f:
        json.dump({
            "test_version": TEST_VERSION,
            "test_method": TEST_METHOD_NAME,
            "methodology": METHODOLOGY,
            "context_size": CONTEXT_SIZE,
            "timestamp": timestamp,
            "results": results
        }, f, indent=2)

    safe_zone = max([r["n_items"] for r in results if r["success"]], default=50)

    print(f"\n[PROGRESS] Phase 1 COMPLETE - Safe zone: {safe_zone} items")
    print(f"[PROGRESS] Results saved to: {phase1_file}")
    print(f"[PROGRESS] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return results, safe_zone

# ============================================================================
# PHASE 3: PRODUCTION VALIDATION
# ============================================================================

def run_phase3(safe_zone: int):
    """Phase 3: Production validation with 95% confidence."""
    print("\n\n" + "=" * 80)
    print("PHASE 3: PRODUCTION VALIDATION")
    print("=" * 80)
    print(f"Test Version: {TEST_VERSION}")
    print(f"Methodology: {METHODOLOGY}")
    print(f"Model: {MODEL_NAME} ({CONTEXT_SIZE//1000}k context)")

    # Test points: [safe_zone, safe_zone//2, safe_zone]
    test_points = [safe_zone, safe_zone // 2, safe_zone]
    print(f"Test Points: {test_points}")
    print("Runs per point: 5")
    print("Positions tested: first, middle, last")
    print("Confidence: 95% (5 runs)")
    print("=" * 80)

    results = []

    # Phase delay
    print(f"\nPAUSE   Cooling {THERMAL_CONFIG['phase_delay']}s before Phase 3...")
    time.sleep(THERMAL_CONFIG["phase_delay"])

    for n_items in test_points:
        print(f"\n[{n_items:4d} items] Production validation (5 runs x 3 positions)...")

        item_results = []

        for run in range(1, 6):
            print(f"  Run {run}/5: ", end='', flush=True)

            for position in PHASE1_POSITIONS:
                # Build context and query
                context, secret, entry_ids = build_context(n_items, position)
                answer, elapsed, success = query_phi4(context, secret)

                # Record result with version metadata
                item_results.append({
                    "test_version": TEST_VERSION,
                    "methodology": METHODOLOGY,
                    "n_items": n_items,
                    "run": run,
                    "position": position,
                    "secret": secret,
                    "answer": answer,
                    "success": success,
                    "elapsed": elapsed,
                    "entry_id_sample": entry_ids[0] if entry_ids else None
                })

                # Progress indicator
                print("-" if success else "X", end='', flush=True)

                # Thermal management
                adaptive_thermal_throttling()

                # Brief delay
                time.sleep(THERMAL_CONFIG["query_delay"])

            print()

        results.extend(item_results)

        # Calculate accuracy for this item count
        successes = sum(1 for r in item_results if r["success"])
        accuracy = (successes / len(item_results) * 100) if item_results else 0
        print(f"  -> {n_items} items: {accuracy:.1f}% accuracy\n")

    print("=" * 80)
    print(f"Phase 3 Complete - Tested {len(results)} queries")
    print("=" * 80)

    # IMMEDIATE SAVE with progress logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    phase3_file = f"phi4_{CONTEXT_SIZE//1000}k_v1_phase3_{timestamp}.json"

    with open(phase3_file, 'w') as f:
        json.dump({
            "test_version": TEST_VERSION,
            "test_method": TEST_METHOD_NAME,
            "methodology": METHODOLOGY,
            "context_size": CONTEXT_SIZE,
            "timestamp": timestamp,
            "results": results
        }, f, indent=2)

    # Calculate overall accuracy
    successes = sum(1 for r in results if r["success"])
    accuracy = (successes / len(results) * 100) if results else 0

    print(f"\n[PROGRESS] Phase 3 COMPLETE - Accuracy: {accuracy:.1f}%")
    print(f"[PROGRESS] Results saved to: {phase3_file}")
    print(f"[PROGRESS] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete 3-phase validation."""
    global CONTEXT_SIZE

    # Allow context size override from command line
    import sys
    if len(sys.argv) > 1:
        CONTEXT_SIZE = int(sys.argv[1])

    start_time = time.time()

    print("=" * 80)
    print(f"{TEST_METHOD_NAME.upper()} - {CONTEXT_SIZE//1000}K CONTEXT")
    print("=" * 80)
    print(f"Test Version: {TEST_VERSION}")
    print(f"Methodology: {METHODOLOGY}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL_NAME}")
    print(f"Context Window: {CONTEXT_SIZE:,} tokens")
    print(f"Safe Item Limit: {calculate_safe_item_count(CONTEXT_SIZE)} items (85% margin)")
    print(f"Endpoint: {LLM_URL}")
    print("=" * 80)

    # Phase 1: Coarse Discovery
    phase1_results, safe_zone = run_phase1()

    # Phase 3: Production Validation
    phase3_results = run_phase3(safe_zone)

    # Summary
    elapsed_minutes = (time.time() - start_time) / 60

    print("\n\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Test Version: {TEST_VERSION}")
    print(f"Methodology: {METHODOLOGY}")
    print(f"Safe Zone: {safe_zone} items")
    print(f"Total Queries: {query_count}")
    print(f"Elapsed Time: {elapsed_minutes:.1f} minutes")
    print("=" * 80)

if __name__ == "__main__":
    main()
