"""
PHI-4-REASONING-PLUS (Q8_0) Context Validation
==============================================
Enhanced 3-Phase Validation with Thermal Protection and Cryptographic Secrets

Model: microsoft_Phi-4-reasoning-plus-Q8_0.gguf
Path: D:\llama_model\microsoft_Phi-4-reasoning-plus-Q8_0.gguf

Features:
- Cryptographically secure random numbers (anti-pattern validation for reasoning models)
- Adaptive thermal throttling with GPU temperature monitoring
- Hybrid progressive testing strategy (dense baseline + sparse exploration)
- Real-time monitoring and alerts
- Automatic cooling breaks
"""

import requests
import secrets
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_NAME = "Phi-4-reasoning-plus-Q8_0"
LLM_API_URL = "http://localhost:8090/completion"

# Thermal Management
THERMAL_CONFIG = {
    "query_delay": 1,              # 1s between each query (optimized)
    "batch_delay": 15,             # 15s after every 10 queries (optimized)
    "phase_delay": 30,            # 30s between Phase 1 and Phase 3 (optimized)
    "context_delay": 60,          # 1 min between context tests (optimized)
    "temp_check_interval": 10,     # Check temp every 10 queries
    "temp_threshold_pause": 78,    # Pause if temp > 78°C
    "temp_threshold_abort": 85,    # Abort if temp > 85°C
}

# Test Configuration
used_secrets: Set[str] = set()
query_count = 0
temp_log = []

# ============================================================================
# CRYPTOGRAPHIC SECRET GENERATION (ANTI-REASONING-MODEL)
# ============================================================================

def generate_secret_for_reasoning_model(item_count: int, position: str, run_number: int) -> str:
    """
    Generate truly unpredictable secret numbers for reasoning models.
    Uses cryptographic random with anti-pattern validation.

    For Phi-4-reasoning-plus, we MUST avoid:
    1. Sequential patterns (123456, 234567)
    2. Repeating digits (111111, 555555)
    3. Mathematical sequences (arithmetic/geometric progressions)
    4. Numbers correlating with item_count or position
    5. Palindromes
    6. Common patterns a reasoning model might deduce
    """
    max_attempts = 1000

    for attempt in range(max_attempts):
        # Use cryptographic random (more secure than random.randint)
        secret = secrets.randbelow(900000) + 100000  # 6 digits: 100000-999999
        secret_str = str(secret)

        # ANTI-PATTERN CHECKS

        # 1. Reject sequential digit patterns (123, 234, 345, etc.)
        has_sequence = any(
            secret_str[i:i+3] in '0123456789' or
            secret_str[i:i+3] in '9876543210'
            for i in range(4)
        )
        if has_sequence:
            continue

        # 2. Reject repeating patterns (must have at least 4 unique digits)
        if len(set(secret_str)) < 4:
            continue

        # 3. Reject correlation with item_count
        if str(item_count) in secret_str or str(item_count)[:3] in secret_str:
            continue

        # 4. Reject position hints
        if position == "first" and (secret_str.startswith("000") or secret_str.startswith("111")):
            continue
        if position == "last" and (secret_str.endswith("999") or secret_str.endswith("000")):
            continue
        if position == "middle" and secret_str in ["500000", "555555"]:
            continue

        # 5. Reject mathematical sequences (arithmetic progression)
        digits = [int(d) for d in secret_str]
        diffs = [digits[i+1] - digits[i] for i in range(5)]
        if len(set(diffs)) == 1:  # All differences are same = arithmetic sequence
            continue

        # 6. Reject geometric patterns
        if all(digits[i] * 2 == digits[i+1] for i in range(5) if digits[i] != 0):
            continue

        # 7. Reject palindromes
        if secret_str == secret_str[::-1]:
            continue

        # 8. Check uniqueness (not used before in this session)
        if secret_str not in used_secrets:
            used_secrets.add(secret_str)
            return secret_str

    # Fallback: force a unique random number
    while True:
        secret = secrets.randbelow(900000) + 100000
        secret_str = str(secret)
        if secret_str not in used_secrets:
            used_secrets.add(secret_str)
            return secret_str

# ============================================================================
# THERMAL MANAGEMENT
# ============================================================================

def get_gpu_temperature() -> int:
    """Query NVIDIA GPU temperature using nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        temps = result.stdout.strip().split('\n')
        # Return max temp if multiple GPUs
        return max(int(t) for t in temps if t.strip())
    except Exception as e:
        print(f"[WARN]  Cannot read GPU temp: {e}")
        return None

def get_gpu_power() -> int:
    """Query NVIDIA GPU power draw in watts."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        powers = result.stdout.strip().split('\n')
        return max(float(p) for p in powers if p.strip())
    except:
        return None

def adaptive_thermal_throttling() -> Tuple[int, str]:
    """
    Automatically pause if GPU gets too hot.
    Returns: (cooling_seconds, status_emoji_message)
    """
    temp = get_gpu_temperature()
    power = get_gpu_power()

    if temp is None:
        return 0, "WHITE UNKNOWN"

    # Log temperature
    temp_log.append({
        "timestamp": datetime.now().isoformat(),
        "temp": temp,
        "power": power,
        "query_count": query_count
    })

    if temp >= THERMAL_CONFIG["temp_threshold_abort"]:
        msg = f"RED CRITICAL: {temp}°C / {power}W - Emergency 5 min cooling"
        print(msg)
        return 300, msg
    elif temp >= THERMAL_CONFIG["temp_threshold_pause"]:
        msg = f"ORANGE HOT: {temp}°C / {power}W - Extended 2 min cooling"
        print(msg)
        return 120, msg
    elif temp >= 75:
        msg = f"YELLOW WARM: {temp}°C / {power}W - Brief 45s cooling"
        print(msg)
        return 45, msg
    else:
        msg = f"GREEN NORMAL: {temp}°C / {power}W"
        return 0, msg

def log_temperature_with_cooling(force_check: bool = False):
    """Check temperature and apply adaptive cooling if needed."""
    global query_count

    if force_check or query_count % THERMAL_CONFIG["temp_check_interval"] == 0:
        cooling_time, status = adaptive_thermal_throttling()
        print(f"    [{datetime.now().strftime('%H:%M:%S')}] Query {query_count} - {status}")

        if cooling_time > 0:
            print(f"    PAUSE  Cooling for {cooling_time}s...")
            time.sleep(cooling_time)
            # Re-check after cooling
            temp = get_gpu_temperature()
            print(f"    OK Resumed - GPU now: {temp}°C")

# ============================================================================
# LLM QUERY EXECUTION
# ============================================================================

def generate_filler_items(n_items: int, secret_number: str, needle_position: str) -> str:
    """
    Generate filler items with the secret number at specified position.

    Args:
        n_items: Total number of items to generate
        secret_number: The 6-digit secret to hide
        needle_position: "first", "middle", or "last"
    """
    items = []
    secret_inserted = False

    for i in range(1, n_items + 1):
        # Determine where to insert secret
        if needle_position == "first" and i == max(1, int(n_items * 0.05)):
            items.append(f"Item {i}: The target code is {secret_number}")
            secret_inserted = True
        elif needle_position == "middle" and i == max(1, int(n_items * 0.50)):
            items.append(f"Item {i}: The target code is {secret_number}")
            secret_inserted = True
        elif needle_position == "last" and i == max(1, int(n_items * 0.95)):
            items.append(f"Item {i}: The target code is {secret_number}")
            secret_inserted = True
        else:
            items.append(f"Item {i}: This is filler item number {i}")

    # Fallback: ensure secret was inserted
    if not secret_inserted:
        if needle_position == "last":
            items[-1] = f"Item {n_items}: The target code is {secret_number}"
        else:
            items[0] = f"Item 1: The target code is {secret_number}"

    return "\n".join(items)

def extract_answer_robust(response_text: str, secret_number: str) -> Tuple[bool, str]:
    """Extract 6-digit number from Phi-4 response with multiple fallback methods."""
    import re
    
    if not response_text:
        return False, ""
    
    # Method 1: Look for "Final answer:" pattern
    match = re.search(r'Final answer:\s*(\d{6})', response_text, re.IGNORECASE)
    if match:
        answer = match.group(1)
        return (answer == secret_number), answer
    
    # Method 2: Skip <think> block and find number after </think>
    think_end = response_text.find('</think>')
    if think_end != -1:
        after_think = response_text[think_end + 8:]
        match = re.search(r'(\d{6})', after_think)
        if match:
            answer = match.group(1)
            return (answer == secret_number), answer
    
    # Method 3: Fallback - find ANY 6-digit number
    match = re.search(r'(\d{6})', response_text)
    if match:
        answer = match.group(1)
        return (answer == secret_number), answer
    
    return False, ""

def query_llm(n_items: int, secret_number: str, needle_position: str,
              timeout: int = 120) -> Tuple[bool, str, float]:
    """Query using official Phi-4-reasoning-plus ChatML format."""
    global query_count
    query_count += 1
    
    # Generate context
    context = generate_filler_items(n_items, secret_number, needle_position)
    
    # Official ChatML format with <|im_sep|> separators
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
    
    start_time = time.time()
    
    try:
        response = requests.post(
            LLM_API_URL,
            json={{
                "prompt": prompt,
                "n_predict": 200,
                "temperature": 0.1,
                "top_p": 0.95,
                "stop": ["<|im_end|>", "

User:", "

Item"]
            }},
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", "").strip()
            
            # Extract using robust multi-method extraction
            success, answer = extract_answer_robust(content, secret_number)
            return success, answer, elapsed
        else:
            return False, "", elapsed
            
    except requests.Timeout:
        elapsed = time.time() - start_time
        return False, "[TIMEOUT]", elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        return False, f"[ERROR: {{str(e)}}]", elapsed

# ============================================================================
# PHASE 1: COARSE DISCOVERY
# ============================================================================

def phase1_coarse_discovery(context_size: int, start_items: int = 50,
                            max_items: int = 2000, step: int = 50) -> List[Dict]:
    """
    Phase 1: Discover approximate safe zone boundaries.

    Args:
        context_size: Context window size (e.g., 12000)
        start_items: Starting item count (default: 50)
        max_items: Maximum items to test (default: 2000)
        step: Increment step (default: 50)
    """
    print("\n" + "="*80)
    print("PHASE 1: COARSE DISCOVERY")
    print("="*80)
    print(f"Model: {MODEL_NAME} ({context_size//1000}k context)")
    print(f"Item Range: {start_items} → {max_items} (step={step})")
    print(f"Runs per item count: 3")
    print(f"Positions tested: first, middle, last")
    print("="*80)

    results = []
    consecutive_failures = 0

    for n_items in range(start_items, max_items + 1, step):
        print(f"\n[{n_items:4d} items] Testing...", end=" ", flush=True)

        run_results = []

        for run in range(1, 4):  # 3 runs
            for position in ["first", "middle", "last"]:
                # Generate unique secret for this query
                secret = generate_secret_for_reasoning_model(n_items, position, run)

                # Execute query
                success, answer, elapsed = query_llm(n_items, secret, position)

                run_results.append({
                    "n_items": n_items,
                    "run": run,
                    "position": position,
                    "secret": secret,
                    "answer": answer,
                    "success": success,
                    "elapsed": elapsed
                })

                # Visual progress
                print("+" if success else "-", end="", flush=True)

                # Thermal management
                log_temperature_with_cooling()

                # Query delay
                time.sleep(THERMAL_CONFIG["query_delay"])

        # Calculate accuracy for this item count
        successes = sum(1 for r in run_results if r["success"])
        accuracy = successes / len(run_results)

        print(f" -> {accuracy*100:.1f}%")

        results.extend(run_results)

        # Early stopping: 3 consecutive complete failures
        if accuracy == 0:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                print(f"\n[WARN]  Stopping: 3 consecutive failures detected")
                break
        else:
            consecutive_failures = 0

        # Batch cooling delay (every 10 queries)
        if n_items % (step * 2) == 0:
            print(f"    CYCLE Batch cooling: {THERMAL_CONFIG['batch_delay']}s")
            time.sleep(THERMAL_CONFIG["batch_delay"])

    print("\n" + "="*80)
    print(f"Phase 1 Complete - Tested {len(results)} queries")
    print("="*80)

    # Phase delay before Phase 3
    print(f"\nPAUSE  Cooling {THERMAL_CONFIG['phase_delay']}s before Phase 3...")
    time.sleep(THERMAL_CONFIG["phase_delay"])

    return results

# ============================================================================
# PHASE 3: PRODUCTION VALIDATION
# ============================================================================

def phase3_production_validation(context_size: int, test_points: List[int]) -> List[Dict]:
    """
    Phase 3: High-confidence validation of critical boundaries.
    Tests 3 boundaries with 5 runs each for 95% confidence.
    """
    print("\n" + "="*80)
    print("PHASE 3: PRODUCTION VALIDATION")
    print("="*80)
    print(f"Model: {MODEL_NAME} ({context_size//1000}k context)")
    print(f"Test Points: {test_points}")
    print(f"Runs per point: 5")
    print(f"Positions tested: first, middle, last")
    print(f"Confidence: 95% (5 runs)")
    print("="*80)

    results = []

    for n_items in test_points:
        print(f"\n[{n_items:4d} items] Production validation (5 runs × 3 positions)...")

        for run in range(1, 6):  # 5 runs for 95% confidence
            print(f"  Run {run}/5: ", end="", flush=True)

            for position in ["first", "middle", "last"]:
                secret = generate_secret_for_reasoning_model(n_items, position, run)
                success, answer, elapsed = query_llm(n_items, secret, position)

                results.append({
                    "n_items": n_items,
                    "run": run,
                    "position": position,
                    "secret": secret,
                    "answer": answer,
                    "success": success,
                    "elapsed": elapsed
                })

                print("+" if success else "-", end="", flush=True)

                # Thermal management
                log_temperature_with_cooling()

                # Query delay
                time.sleep(THERMAL_CONFIG["query_delay"])

            print()  # Newline after each run

        # Summary for this test point
        point_results = [r for r in results if r["n_items"] == n_items]
        accuracy = sum(1 for r in point_results if r["success"]) / len(point_results)
        print(f"  → {n_items} items: {accuracy*100:.1f}% accuracy")

    print("\n" + "="*80)
    print(f"Phase 3 Complete - Tested {len(results)} queries")
    print("="*80)

    return results

# ============================================================================
# RESULT ANALYSIS
# ============================================================================

def analyze_results(phase1_results: List[Dict], phase3_results: List[Dict],
                    context_size: int) -> Dict:
    """Analyze results and determine safe zone."""

    # Find safe zone from Phase 1
    item_counts = sorted(set(r["n_items"] for r in phase1_results))

    safe_zone_end = 0
    for n_items in item_counts:
        item_results = [r for r in phase1_results if r["n_items"] == n_items]
        accuracy = sum(1 for r in item_results if r["success"]) / len(item_results)

        if accuracy == 1.0:
            safe_zone_end = n_items
        else:
            break

    # Phase 3 validation
    phase3_summary = {}
    for n_items in sorted(set(r["n_items"] for r in phase3_results)):
        item_results = [r for r in phase3_results if r["n_items"] == n_items]
        accuracy = sum(1 for r in item_results if r["success"]) / len(item_results)
        phase3_summary[n_items] = accuracy

    return {
        "model": MODEL_NAME,
        "context_size": context_size,
        "safe_zone_end": safe_zone_end,
        "phase1_queries": len(phase1_results),
        "phase3_queries": len(phase3_results),
        "phase3_summary": phase3_summary,
        "total_queries": len(phase1_results) + len(phase3_results),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_adaptive_validation(context_size: int):
    """Run complete adaptive validation for a given context size."""

    print("\n" + "="*80)
    print(f"PHI-4-REASONING-PLUS ADAPTIVE VALIDATION - {context_size//1000}K CONTEXT")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL_NAME}")
    print(f"Context Window: {context_size:,} tokens")
    print(f"Endpoint: {LLM_API_URL}")
    print("="*80)

    # Check GPU temperature before starting
    print("\n[TEMP] Pre-test thermal check...")
    log_temperature_with_cooling(force_check=True)

    start_time = time.time()

    # Determine test range based on context size
    # Predicted: context_size / 10 as rough estimate
    max_items = min(context_size // 8, 2000)

    # Phase 1: Coarse Discovery
    phase1_results = phase1_coarse_discovery(
        context_size=context_size,
        start_items=50,
        max_items=max_items,
        step=50
    )

    # IMMEDIATE SAVE: Write Phase 1 results right after completion
    timestamp_p1 = datetime.now().strftime("%Y%m%d_%H%M%S")
    phase1_file = f"phi4_plus_{context_size//1000}k_phase1_{timestamp_p1}.json"
    with open(phase1_file, 'w') as f:
        json.dump(phase1_results, f, indent=2)

    safe_zone = max([r["n_items"] for r in phase1_results if r["success"]], default=50)
    print(f"\n[PROGRESS] Phase 1 COMPLETE - Safe zone: {safe_zone} items")
    print(f"[PROGRESS] Results saved to: {phase1_file}")
    print(f"[PROGRESS] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Determine Phase 3 test points
    test_points = [
        50,  # Lower bound
        safe_zone // 2,  # Mid-point
        safe_zone  # Upper bound
    ]

    # Phase 3: Production Validation
    phase3_results = phase3_production_validation(context_size, test_points)

    # IMMEDIATE SAVE: Write Phase 3 results right after completion
    timestamp_p3 = datetime.now().strftime("%Y%m%d_%H%M%S")
    phase3_file = f"phi4_plus_{context_size//1000}k_phase3_{timestamp_p3}.json"
    with open(phase3_file, 'w') as f:
        json.dump(phase3_results, f, indent=2)

    phase3_accuracy = sum(1 for r in phase3_results if r["success"]) / len(phase3_results) if phase3_results else 0
    print(f"\n[PROGRESS] Phase 3 COMPLETE - Accuracy: {phase3_accuracy*100:.1f}%")
    print(f"[PROGRESS] Results saved to: {phase3_file}")
    print(f"[PROGRESS] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Analyze results
    summary = analyze_results(phase1_results, phase3_results, context_size)

    elapsed = time.time() - start_time

    # Save final results (Phase 1 & 3 already saved immediately after each phase)
    # These final saves create matching timestamps for thermal + report files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Final Phase 1 save (for complete set with matching timestamp)
    phase1_file_final = f"phi4_plus_{context_size//1000}k_phase1_{timestamp}.json"
    with open(phase1_file_final, 'w') as f:
        json.dump(phase1_results, f, indent=2)

    # Final Phase 3 save (for complete set with matching timestamp)
    phase3_file_final = f"phi4_plus_{context_size//1000}k_phase3_{timestamp}.json"
    with open(phase3_file_final, 'w') as f:
        json.dump(phase3_results, f, indent=2)

    # Save thermal log
    thermal_file = f"phi4_plus_{context_size//1000}k_thermal_{timestamp}.json"
    with open(thermal_file, 'w') as f:
        json.dump(temp_log, f, indent=2)

    # Generate markdown report
    report_file = f"phi4_plus_{context_size//1000}k_validation_results_{timestamp}.md"
    generate_markdown_report(summary, phase1_results, phase3_results, elapsed, report_file)

    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print(f"Safe Zone: {summary['safe_zone_end']} items")
    print(f"Total Queries: {summary['total_queries']}")
    print(f"Elapsed Time: {elapsed/60:.1f} minutes")
    print(f"\nResults saved:")
    print(f"  - {phase1_file}")
    print(f"  - {phase3_file}")
    print(f"  - {thermal_file}")
    print(f"  - {report_file}")
    print("="*80)

    # Context cooling delay
    print(f"\nPAUSE  Context transition cooling: {THERMAL_CONFIG['context_delay']}s")
    time.sleep(THERMAL_CONFIG['context_delay'])

    return summary

def generate_markdown_report(summary: Dict, phase1_results: List[Dict],
                            phase3_results: List[Dict], elapsed: float, filename: str):
    """Generate detailed markdown report."""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {MODEL_NAME} - {summary['context_size']//1000}k Context Validation\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Model:** {MODEL_NAME}\n")
        f.write(f"- **Model File:** microsoft_Phi-4-reasoning-plus-Q8_0.gguf\n")
        f.write(f"- **Context Window:** {summary['context_size']:,} tokens\n")
        f.write(f"- **Safe Zone:** {summary['safe_zone_end']} items (100% accuracy)\n")
        f.write(f"- **Total Queries:** {summary['total_queries']}\n")
        f.write(f"- **Test Duration:** {elapsed/60:.1f} minutes\n\n")

        f.write("## Phase 1: Coarse Discovery\n\n")
        f.write("| Items | Accuracy | Details |\n")
        f.write("|-------|----------|----------|\n")

        item_counts = sorted(set(r["n_items"] for r in phase1_results))
        for n_items in item_counts:
            item_results = [r for r in phase1_results if r["n_items"] == n_items]
            accuracy = sum(1 for r in item_results if r["success"]) / len(item_results)
            f.write(f"| {n_items:4d} | {accuracy*100:5.1f}% | {sum(1 for r in item_results if r['success'])}/{len(item_results)} |\n")

        f.write("\n## Phase 3: Production Validation (95% Confidence)\n\n")
        f.write("| Items | Accuracy | Position Breakdown |\n")
        f.write("|-------|----------|--------------------|\n")

        for n_items in sorted(summary['phase3_summary'].keys()):
            accuracy = summary['phase3_summary'][n_items]
            item_results = [r for r in phase3_results if r["n_items"] == n_items]

            pos_breakdown = {}
            for pos in ["first", "middle", "last"]:
                pos_results = [r for r in item_results if r["position"] == pos]
                pos_acc = sum(1 for r in pos_results if r["success"]) / len(pos_results)
                pos_breakdown[pos] = pos_acc

            breakdown_str = f"F:{pos_breakdown['first']*100:.0f}% M:{pos_breakdown['middle']*100:.0f}% L:{pos_breakdown['last']*100:.0f}%"
            f.write(f"| {n_items:4d} | {accuracy*100:5.1f}% | {breakdown_str} |\n")

        f.write("\n## Thermal Performance\n\n")
        if temp_log:
            max_temp = max(t["temp"] for t in temp_log if t["temp"])
            avg_temp = sum(t["temp"] for t in temp_log if t["temp"]) / len([t for t in temp_log if t["temp"]])
            f.write(f"- **Max Temperature:** {max_temp}°C\n")
            f.write(f"- **Avg Temperature:** {avg_temp:.1f}°C\n")
            f.write(f"- **Thermal Events:** {len([t for t in temp_log if t['temp'] > 78])} warnings\n\n")

        f.write("## Conclusion\n\n")
        f.write(f"The {MODEL_NAME} model reliably handles up to **{summary['safe_zone_end']} items** ")
        f.write(f"at {summary['context_size']//1000}k context window with 100% accuracy across all needle positions.\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python phi4_plus_adaptive_validation.py <context_size>")
        print("Example: python phi4_plus_adaptive_validation.py 12000")
        sys.exit(1)

    context_size = int(sys.argv[1])
    run_adaptive_validation(context_size)
