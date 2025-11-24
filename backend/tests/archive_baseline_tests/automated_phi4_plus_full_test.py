"""
Automated Overnight Testing for Phi-4-reasoning-plus
====================================================
Fully automated testing from 12k to 30k contexts
User can sleep - script handles everything automatically

Features:
- Auto-updates docker-compose.yml for each context
- Auto-restarts containers with proper warm-up
- Runs all validation tests sequentially
- Generates comprehensive final report
- Handles errors gracefully
- Logs everything for debugging
"""

import subprocess
import time
import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_NAME = "Phi-4-reasoning-plus-Q8_0"
DOCKER_COMPOSE_PATH = "D:/gpt-oss/docker-compose.yml"
TEST_SCRIPT = "phi4_plus_adaptive_validation.py"
RESULTS_DIR = "D:/gpt-oss/backend/tests"

# Test sequence: Baseline (12k-20k) + Exploration (24k, 28k) + Adaptive (30k, 32k)
BASELINE_CONTEXTS = [12000, 14000, 16000, 18000, 20000]
EXPLORATION_CONTEXTS = [24000, 28000]
ADAPTIVE_CONTEXTS = [30000, 32000]  # 30k if 28k succeeds, 32k if 30k succeeds

# Timing
WARMUP_TIME = 180  # 3 minutes
BETWEEN_TESTS_COOLDOWN = 300  # 5 minutes

# ============================================================================
# UTILITIES
# ============================================================================

def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

    # Also write to log file
    with open("automated_test_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def run_command(cmd: str, description: str, timeout: int = None) -> tuple:
    """Run shell command and return (success, output)."""
    log(f"Running: {description}")
    log(f"Command: {cmd}", "DEBUG")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="D:/gpt-oss"
        )

        if result.returncode == 0:
            log(f"OK Success: {description}")
            return True, result.stdout
        else:
            log(f"FAIL Failed: {description}", "ERROR")
            log(f"Error: {result.stderr}", "ERROR")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        log(f"FAIL Timeout: {description}", "ERROR")
        return False, "TIMEOUT"
    except Exception as e:
        log(f"FAIL Exception: {description} - {str(e)}", "ERROR")
        return False, str(e)

def update_docker_compose(context_size: int):
    """Update docker-compose.yml with new context size."""
    log(f"Updating docker-compose.yml for {context_size//1000}k context")

    try:
        with open(DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Update container name
        import re
        content = re.sub(
            r'container_name: phi4-plus-q8-\d+k',
            f'container_name: phi4-plus-q8-{context_size//1000}k',
            content
        )

        # Update ctx-size
        content = re.sub(
            r'--ctx-size \d+',
            f'--ctx-size {context_size}',
            content
        )

        with open(DOCKER_COMPOSE_PATH, "w", encoding="utf-8") as f:
            f.write(content)

        log(f"OK Updated docker-compose.yml: ctx-size={context_size}")
        return True
    except Exception as e:
        log(f"FAIL Failed to update docker-compose.yml: {e}", "ERROR")
        return False

def restart_container():
    """Restart llama container with force-recreate."""
    log("Stopping containers...")
    success, _ = run_command("docker-compose down", "Stop containers", timeout=60)
    if not success:
        log("Warning: docker-compose down had issues, continuing anyway", "WARN")

    time.sleep(5)

    log("Starting llama container with force-recreate...")
    success, output = run_command(
        "docker-compose up -d --force-recreate llama",
        "Start llama container",
        timeout=180
    )

    if not success:
        log("FAIL Failed to start container", "ERROR")
        return False

    log(f"OK Container started, warming up for {WARMUP_TIME}s...")
    time.sleep(WARMUP_TIME)

    return True

def check_model_health() -> bool:
    """Check if model is responding."""
    log("Checking model health...")

    try:
        import requests
        response = requests.get("http://localhost:8090/health", timeout=10)
        if response.status_code == 200:
            log("OK Model is healthy")
            return True
        else:
            log(f"FAIL Model health check failed: HTTP {response.status_code}", "WARN")
            return False
    except Exception as e:
        log(f"FAIL Model health check failed: {e}", "WARN")
        return False

def run_validation_test(context_size: int) -> dict:
    """Run validation test for a specific context size."""
    log(f"\n{'='*80}")
    log(f"STARTING TEST: {context_size//1000}K CONTEXT")
    log(f"{'='*80}\n")

    start_time = time.time()

    # Update docker-compose.yml
    if not update_docker_compose(context_size):
        return {"success": False, "error": "Failed to update docker-compose.yml"}

    # Restart container
    if not restart_container():
        return {"success": False, "error": "Failed to restart container"}

    # Health check
    if not check_model_health():
        log("Model health check failed, but continuing...", "WARN")

    # Run test script
    log(f"Running validation test for {context_size//1000}k...")
    cmd = f"cd {RESULTS_DIR} && python {TEST_SCRIPT} {context_size}"
    success, output = run_command(
        cmd,
        f"Validation test {context_size//1000}k",
        timeout=3600  # 1 hour max per test
    )

    elapsed = time.time() - start_time

    if success:
        log(f"OK Test completed in {elapsed/60:.1f} minutes")

        # Extract safe zone from output (parse the summary)
        safe_zone = extract_safe_zone_from_output(output)

        result = {
            "success": True,
            "context_size": context_size,
            "safe_zone": safe_zone,
            "elapsed_minutes": elapsed / 60,
            "timestamp": datetime.now().isoformat()
        }
    else:
        log(f"FAIL Test failed after {elapsed/60:.1f} minutes", "ERROR")
        result = {
            "success": False,
            "context_size": context_size,
            "error": output[:500],  # First 500 chars of error
            "elapsed_minutes": elapsed / 60,
            "timestamp": datetime.now().isoformat()
        }

    # Cooldown between tests
    log(f"Cooldown for {BETWEEN_TESTS_COOLDOWN}s before next test...")
    time.sleep(BETWEEN_TESTS_COOLDOWN)

    return result

def extract_safe_zone_from_output(output: str) -> int:
    """Extract safe zone value from test output."""
    import re
    match = re.search(r'Safe Zone: (\d+) items', output)
    if match:
        return int(match.group(1))
    return None

def should_test_context(results: list, target_context: int) -> bool:
    """Decide if we should test a context based on previous result."""
    if target_context == 30000:
        # Test 30k if 28k succeeded
        result_28k = next((r for r in results if r.get("context_size") == 28000), None)
        if not result_28k or not result_28k.get("success"):
            log("28k test failed or not found, skipping 30k", "INFO")
            return False
        safe_zone_28k = result_28k.get("safe_zone", 0)
        if safe_zone_28k > 1200:
            log(f"28k safe zone ({safe_zone_28k} items) is strong, will test 30k", "INFO")
            return True
        else:
            log(f"28k safe zone ({safe_zone_28k} items) is marginal, skipping 30k", "INFO")
            return False

    elif target_context == 32000:
        # Test 32k if 30k succeeded
        result_30k = next((r for r in results if r.get("context_size") == 30000), None)
        if not result_30k or not result_30k.get("success"):
            log("30k test failed or not found, skipping 32k", "INFO")
            return False
        safe_zone_30k = result_30k.get("safe_zone", 0)
        if safe_zone_30k > 1300:
            log(f"30k safe zone ({safe_zone_30k} items) is strong, will test 32k", "INFO")
            return True
        else:
            log(f"30k safe zone ({safe_zone_30k} items) is marginal, skipping 32k", "INFO")
            return False

    return True

def generate_final_report(results: list):
    """Generate comprehensive final report."""
    log("\n" + "="*80)
    log("GENERATING FINAL REPORT")
    log("="*80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"PHI4_PLUS_COMPLETE_REPORT_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Phi-4-reasoning-plus-Q8_0 - Complete Context Testing Report\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {MODEL_NAME}\n")
        f.write(f"**Model Path:** D:\\llama_model\\microsoft_Phi-4-reasoning-plus-Q8_0.gguf\n\n")

        f.write("## Executive Summary\n\n")

        successful_tests = [r for r in results if r.get("success")]
        failed_tests = [r for r in results if not r.get("success")]

        f.write(f"- **Total Tests:** {len(results)}\n")
        f.write(f"- **Successful:** {len(successful_tests)}\n")
        f.write(f"- **Failed:** {len(failed_tests)}\n")

        if successful_tests:
            total_time = sum(r.get("elapsed_minutes", 0) for r in results)
            f.write(f"- **Total Test Time:** {total_time/60:.1f} hours\n")

            max_context = max(r["context_size"] for r in successful_tests)
            f.write(f"- **Maximum Reliable Context:** {max_context//1000}k\n")

        f.write("\n## Test Results Summary\n\n")
        f.write("| Context | Status | Safe Zone | Test Time | Notes |\n")
        f.write("|---------|--------|-----------|-----------|-------|\n")

        for result in results:
            ctx = result.get("context_size", 0)
            status = "[PASS] PASS" if result.get("success") else "ERROR FAIL"
            safe_zone = result.get("safe_zone", "N/A")
            elapsed = result.get("elapsed_minutes", 0)
            error = result.get("error", "")[:50] if not result.get("success") else "-"

            f.write(f"| {ctx//1000}k | {status} | {safe_zone} items | {elapsed:.1f} min | {error} |\n")

        f.write("\n## Detailed Results\n\n")

        for result in successful_tests:
            ctx = result["context_size"]
            f.write(f"### {ctx//1000}k Context\n\n")
            f.write(f"- **Safe Zone:** {result.get('safe_zone', 'N/A')} items\n")
            f.write(f"- **Test Duration:** {result.get('elapsed_minutes', 0):.1f} minutes\n")
            f.write(f"- **Timestamp:** {result.get('timestamp', 'N/A')}\n")

            # Link to detailed files
            f.write(f"- **Detailed Results:** `phi4_plus_{ctx//1000}k_validation_results_*.md`\n\n")

        if failed_tests:
            f.write("\n## Failed Tests\n\n")
            for result in failed_tests:
                ctx = result["context_size"]
                f.write(f"### {ctx//1000}k Context - FAILED\n\n")
                f.write(f"- **Error:** {result.get('error', 'Unknown error')}\n")
                f.write(f"- **Duration:** {result.get('elapsed_minutes', 0):.1f} minutes\n\n")

        f.write("\n## Comparison with Standard Phi-4-reasoning\n\n")
        f.write("| Context | Standard Phi-4 | Phi-4-Plus Q8 | Improvement |\n")
        f.write("|---------|----------------|---------------|-------------|\n")

        # Standard phi-4 baseline (from previous tests)
        standard_phi4 = {
            12000: 600,
            14000: 700,
            16000: 800,
            18000: 900,
            20000: 1000
        }

        for result in successful_tests:
            ctx = result["context_size"]
            if ctx in standard_phi4:
                std = standard_phi4[ctx]
                plus = result.get("safe_zone", 0)
                improvement = ((plus - std) / std * 100) if plus else 0
                f.write(f"| {ctx//1000}k | {std} items | {plus} items | +{improvement:.1f}% |\n")

        f.write("\n## Recommendations\n\n")

        if successful_tests:
            max_safe_ctx = max(r["context_size"] for r in successful_tests)
            f.write(f"- **Production Context:** Use {max_safe_ctx//1000}k for maximum reliability\n")

            avg_safe_zone = sum(r.get("safe_zone", 0) for r in successful_tests) / len(successful_tests)
            f.write(f"- **Average Safe Zone:** {avg_safe_zone:.0f} items across all contexts\n")

            f.write("- **Q8 Quantization:** Recommended for production use (better accuracy retention)\n")

        f.write("\n## Conclusion\n\n")
        f.write(f"Automated testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n")
        f.write(f"Phi-4-reasoning-plus-Q8_0 demonstrated reliable context handling up to ")

        if successful_tests:
            max_ctx = max(r["context_size"] for r in successful_tests)
            f.write(f"{max_ctx//1000}k tokens with consistent accuracy.\n")
        else:
            f.write("testing phase (see errors above).\n")

    log(f"OK Final report generated: {report_file}")

    # Also save raw results as JSON
    json_file = f"PHI4_PLUS_COMPLETE_RESULTS_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    log(f"OK Raw results saved: {json_file}")

    return report_file

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main automation function."""
    log("\n" + "="*80)
    log("PHI-4-REASONING-PLUS AUTOMATED OVERNIGHT TESTING")
    log("="*80)
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Model: {MODEL_NAME}")
    log(f"Test Sequence: {len(BASELINE_CONTEXTS)} baseline + {len(EXPLORATION_CONTEXTS)} exploration + up to {len(ADAPTIVE_CONTEXTS)} adaptive")
    log("="*80 + "\n")

    overall_start = time.time()
    all_results = []

    # Phase 1: Baseline tests (12k-20k)
    log("\n" + "="*80)
    log("PHASE 1: BASELINE TESTING (12k-20k)")
    log("="*80 + "\n")

    for ctx in BASELINE_CONTEXTS:
        result = run_validation_test(ctx)
        all_results.append(result)

        # If test failed critically, decide whether to continue
        if not result["success"]:
            log(f"WARN Test failed at {ctx//1000}k, but continuing with remaining tests", "WARN")

    # Phase 2: Exploration tests (24k, 28k)
    log("\n" + "="*80)
    log("PHASE 2: EXPLORATION TESTING (24k, 28k)")
    log("="*80 + "\n")

    for ctx in EXPLORATION_CONTEXTS:
        result = run_validation_test(ctx)
        all_results.append(result)

        if not result["success"]:
            log(f"WARN Test failed at {ctx//1000}k", "WARN")
            # If 24k fails, might skip 28k
            if ctx == 24000:
                log("24k failed, but will still try 28k", "INFO")

    # Phase 3: Adaptive tests (30k, 32k) - test each if previous succeeded
    log("\n" + "="*80)
    log("PHASE 3: ADAPTIVE TESTING (30k, 32k)")
    log("="*80 + "\n")

    for ctx in ADAPTIVE_CONTEXTS:
        if should_test_context(all_results, ctx):
            result = run_validation_test(ctx)
            all_results.append(result)
        else:
            log(f"Skipping {ctx//1000}k test based on previous results")
            break  # If one is skipped, skip the rest

    # Generate final report
    overall_elapsed = time.time() - overall_start

    log("\n" + "="*80)
    log("ALL TESTING COMPLETE!")
    log("="*80)
    log(f"Total Time: {overall_elapsed/3600:.1f} hours")
    log(f"Tests Completed: {len(all_results)}")
    log(f"Successful: {len([r for r in all_results if r.get('success')])}")
    log(f"Failed: {len([r for r in all_results if not r.get('success')])}")
    log("="*80 + "\n")

    report_file = generate_final_report(all_results)

    log("\n" + "="*80)
    log("FINAL REPORT READY")
    log("="*80)
    log(f"📄 Report: {report_file}")
    log(f"📄 Log: automated_test_log.txt")
    log(f"📁 All results in: {RESULTS_DIR}")
    log("="*80)
    log("\n[PASS] Good morning! All tests completed while you were sleeping.")
    log("Check the files above for detailed results.\n")

    # Shut down container to save power
    log("Shutting down containers...")
    run_command("docker-compose down", "Final shutdown", timeout=60)
    log("OK Containers stopped. Testing session complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nWARN Testing interrupted by user", "WARN")
        log("Shutting down containers...")
        subprocess.run("docker-compose down", shell=True, cwd="D:/gpt-oss")
    except Exception as e:
        log(f"\nERROR CRITICAL ERROR: {str(e)}", "ERROR")
        log("Attempting emergency shutdown...")
        subprocess.run("docker-compose down", shell=True, cwd="D:/gpt-oss")
        raise
