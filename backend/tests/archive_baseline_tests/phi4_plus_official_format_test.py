"""
Phi-4-reasoning-plus Needle Test - Official ChatML Format
Based on Ultra-AI agent recommendation and official Microsoft documentation
"""

import requests
import random
import time
import subprocess
from typing import Tuple, Optional
from datetime import datetime
import json
import re

# Configuration
LLM_URL = "http://localhost:8090/completion"
CONTEXT_SIZE = 12000

def get_gpu_stats() -> Tuple[Optional[float], Optional[float], Optional[int], Optional[int], Optional[float]]:
    """Query GPU temperature, power, and VRAM usage.

    Returns:
        (temp_c, power_w, vram_used_mb, vram_total_mb, vram_percent)
    """
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=temperature.gpu,power.draw,memory.used,memory.total',
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
        print(f"[WARN] GPU stats query failed: {e}")

    return None, None, None, None, None

def generate_secret() -> str:
    """Generate 6-digit cryptographic secret."""
    return str(random.randint(100000, 999999))

def build_context(n_items: int, secret_position: str) -> Tuple[str, str]:
    """Build haystack context with hidden secret.

    Args:
        n_items: Total number of items in context
        secret_position: 'first', 'middle', or 'last'

    Returns:
        (context_text, secret_number)
    """
    secret = generate_secret()
    items = []

    for i in range(n_items):
        if secret_position == 'first' and i == 0:
            items.append(f"Item {i+1}: The target code is {secret}.")
        elif secret_position == 'middle' and i == n_items // 2:
            items.append(f"Item {i+1}: The target code is {secret}.")
        elif secret_position == 'last' and i == n_items - 1:
            items.append(f"Item {i+1}: The target code is {secret}.")
        else:
            items.append(f"Item {i+1}: This is a standard entry with no special information.")

    context = "\n".join(items)
    return context, secret

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

def query_phi4(context: str, secret: str) -> Tuple[str, float, bool]:
    """Query Phi-4-reasoning-plus using official ChatML format.

    Args:
        context: Haystack text with embedded secret
        secret: Expected 6-digit number

    Returns:
        (extracted_answer, elapsed_seconds, success)
    """
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
        "stop": ["<|im_end|>", "\n\nUser:", "\n\nItem"]
    }

    start_time = time.time()

    try:
        response = requests.post(LLM_URL, json=payload, timeout=120)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}: {response.text[:200]}")
            return "", elapsed, False

        data = response.json()
        raw_response = data.get("content", "")

        # Extract answer using robust multi-method extraction
        extracted = extract_answer_robust(raw_response)

        success = (extracted == secret)

        # Debug output
        print(f"[DEBUG] Raw response: {raw_response[:300]}")
        print(f"[DEBUG] Extracted: {extracted}, Expected: {secret}, Match: {success}")

        return extracted, elapsed, success

    except requests.Timeout:
        elapsed = time.time() - start_time
        print(f"[ERROR] Timeout after {elapsed:.1f}s")
        return "", elapsed, False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[ERROR] Exception: {e}")
        return "", elapsed, False

def quick_validation_test():
    """Run quick 50-item validation test to verify format works."""
    print("=" * 80)
    print("PHI-4-REASONING-PLUS QUICK VALIDATION TEST")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Context Size: {CONTEXT_SIZE} tokens")
    print(f"Endpoint: {LLM_URL}")
    print(f"Format: Official ChatML with <|im_sep|>")
    print("=" * 80)

    # Get initial GPU stats
    temp, power, vram_used, vram_total, vram_percent = get_gpu_stats()
    if temp:
        print(f"\n[GPU] Initial: {temp}°C / {power:.1f}W / VRAM: {vram_used}MB/{vram_total}MB ({vram_percent:.1f}%)")

    print("\n[TEST] Running 3 tests (50 items, 3 positions)...\n")

    results = []
    positions = ["first", "middle", "last"]

    for i, position in enumerate(positions, 1):
        print(f"Test {i}/3 - Position: {position}")

        # Build context
        context, secret = build_context(50, position)

        # Query model
        answer, elapsed, success = query_phi4(context, secret)

        # Record result
        result = {
            "test": i,
            "position": position,
            "n_items": 50,
            "secret": secret,
            "answer": answer,
            "success": success,
            "elapsed": elapsed
        }
        results.append(result)

        # Status indicator
        status = "PASS" if success else "FAIL"
        print(f"  {status} - {elapsed:.2f}s - Expected: {secret}, Got: {answer}\n")

        # GPU stats
        temp, power, vram_used, vram_total, vram_percent = get_gpu_stats()
        if temp:
            print(f"  [GPU] {temp}°C / {power:.1f}W / VRAM: {vram_used}MB ({vram_percent:.1f}%)\n")

        # Brief delay between tests
        if i < len(positions):
            time.sleep(5)

    # Summary
    print("=" * 80)
    print("VALIDATION TEST COMPLETE")
    print("=" * 80)

    success_count = sum(1 for r in results if r["success"])
    accuracy = (success_count / len(results) * 100) if results else 0

    print(f"\nResults: {success_count}/{len(results)} passed ({accuracy:.1f}% accuracy)")

    for r in results:
        status = "[PASS]" if r["success"] else "[FAIL]"
        print(f"  {status} Test {r['test']} ({r['position']:6s}): {r['answer']} vs {r['secret']}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"phi4_plus_quick_validation_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Return success flag
    return accuracy >= 66.7  # At least 2/3 tests must pass

if __name__ == "__main__":
    success = quick_validation_test()

    if success:
        print("\n[PASS] VALIDATION PASSED - Ready for full 12k context testing")
        exit(0)
    else:
        print("\n[FAIL] VALIDATION FAILED - Need further debugging")
        exit(1)
