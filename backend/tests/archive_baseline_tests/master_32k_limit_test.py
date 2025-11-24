"""
Master 32k Limit Testing - 4 Models Sequential (RESUME MODE)
============================================================
Tests 4 models pushing to their 32k context limits with 2k increments

RESUME STATUS (after auto-fixes):
- Falcon 18k-24k: COMPLETED (4/8 tests done)
- File path bug: FIXED
- Timeout issue: FIXED (adaptive timeouts implemented)

Test Order (USER REQUEST: Phi-4-reasoning-plus before Mistral):
1. Falcon-H1-34B: 26k → 32k (4 contexts remaining)
2. Phi-4-reasoning-plus: 12k → 32k (11 contexts, 300s warmup) ← RUNS FIRST
3. Mistral-Small-24B: 22k → 32k (6 contexts)
4. Phi-4: 22k → 32k (6 contexts)

Total remaining: 27 context tests, estimated 12-18 hours
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_DIR = "D:/gpt-oss/backend/tests"
DOCKER_COMPOSE_PATH = "D:/gpt-oss/docker-compose.yml"

# Model configurations
# RESUME MODE: Falcon 18k-24k completed successfully, resuming from 26k
# USER REQUEST: Phi-4-reasoning-plus runs BEFORE Mistral-Small
MODELS = [
    {
        "name": "Falcon-H1-34B-Q5_K_M",
        "file": "Falcon-H1-34B-Instruct-Q5_K_M.gguf",
        "contexts": list(range(26000, 34000, 2000)),  # 26k-32k (resume after 24k success)
        "warmup": 180,
        "test_script": "falcon_h1_context_test.py"
    },
    {
        "name": "Phi-4-reasoning-plus-Q8_0",
        "file": "microsoft_Phi-4-reasoning-plus-Q8_0.gguf",
        "contexts": list(range(12000, 34000, 2000)),  # 12k-32k
        "warmup": 300,  # Longer warmup for this model
        "test_script": "phi4_plus_adaptive_validation.py"
    },
    {
        "name": "Mistral-Small-2501-24B-Q6_K",
        "file": "Mistral-Small-24B-Instruct-2501-Q6_K.gguf",
        "contexts": list(range(22000, 34000, 2000)),  # 22k-32k
        "warmup": 180,
        "test_script": "mistral_small_context_test.py"
    },
    {
        "name": "Phi-4",
        "file": "phi-4.gguf",
        "contexts": list(range(22000, 34000, 2000)),  # 22k-32k
        "warmup": 180,
        "test_script": "phi4_context_test.py"
    }
]

COOLDOWN_BETWEEN_MODELS = 60  # 1 minute between models (optimized)

# ============================================================================
# UTILITIES
# ============================================================================

def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

    with open("master_32k_test_log.txt", "a", encoding="utf-8") as f:
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

def update_docker_compose(model_file: str, context_size: int, model_name: str):
    """Update docker-compose.yml with new model and context size."""
    log(f"Updating docker-compose.yml for {model_name} @ {context_size//1000}k")

    try:
        with open(DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        import re

        # Update container name
        content = re.sub(
            r'container_name: [a-z0-9_-]+-\d+k',
            f'container_name: {model_name.lower().replace("_", "-")}-{context_size//1000}k',
            content
        )

        # Update model path
        content = re.sub(
            r'--model /models/[^\s]+',
            f'--model /models/{model_file}',
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

        log(f"OK Updated docker-compose.yml: model={model_file}, ctx={context_size}")
        return True
    except Exception as e:
        log(f"FAIL Failed to update docker-compose.yml: {e}", "ERROR")
        return False

def restart_container(warmup_time: int):
    """Restart llama container with specified warmup time."""
    log("Stopping containers...")
    success, _ = run_command("docker-compose down", "Stop containers", timeout=60)
    if not success:
        log("Warning: docker-compose down had issues, continuing anyway", "WARN")

    time.sleep(2)  # Optimized container restart delay

    log("Starting llama container with force-recreate...")
    success, output = run_command(
        "docker-compose up -d --force-recreate llama",
        "Start llama container",
        timeout=180
    )

    if not success:
        log("FAIL Failed to start container", "ERROR")
        return False

    log(f"OK Container started, warming up for {warmup_time}s...")
    time.sleep(warmup_time)

    return True

def check_model_health_with_retry(max_retries: int = 5) -> bool:
    """Check if model is responding with retry logic.

    Retries every 60s if initial 3min warmup fails.
    Args:
        max_retries: Maximum retry attempts (default 5)
    Returns:
        True if model becomes healthy, False otherwise
    """
    import requests

    for attempt in range(1, max_retries + 1):
        log(f"Health check attempt {attempt}/{max_retries}...")

        try:
            response = requests.get("http://localhost:8090/health", timeout=10)
            if response.status_code == 200:
                log(f"OK Model is healthy (attempt {attempt})")
                return True
            else:
                log(f"WARN HTTP {response.status_code} (attempt {attempt})", "WARN")
        except Exception as e:
            log(f"WARN Health check failed: {e} (attempt {attempt})", "WARN")

        if attempt < max_retries:
            log("Waiting 60s before retry...")
            time.sleep(60)

    log("FAIL Model failed to become healthy after all retries", "ERROR")
    return False

def warmup_queries() -> bool:
    """Execute 2 warmup queries with 15s delays.

    Returns:
        True if warmup succeeded, False otherwise
    """
    import requests
    import json

    log("Running warmup queries (2 queries, 15s each)...")

    warmup_prompt = "Hello, are you ready?"

    for i in range(1, 3):
        log(f"Warmup query {i}/2...")

        try:
            response = requests.post(
                "http://localhost:8090/v1/completions",
                json={
                    "prompt": warmup_prompt,
                    "max_tokens": 10,
                    "temperature": 0.1
                },
                timeout=30
            )

            if response.status_code == 200:
                log(f"OK Warmup query {i}/2 succeeded")
            else:
                log(f"WARN Warmup query {i}/2 failed: HTTP {response.status_code}", "WARN")
        except Exception as e:
            log(f"WARN Warmup query {i}/2 exception: {e}", "WARN")

        if i < 2:
            time.sleep(15)

    log("OK Warmup queries completed")
    return True

def test_model_at_context(model_config: dict, context_size: int) -> dict:
    """Test a specific model at a specific context size."""
    log(f"\n{'='*80}")
    log(f"TESTING: {model_config['name']} @ {context_size//1000}K")
    log(f"{'='*80}\n")

    start_time = time.time()

    # Update docker-compose.yml
    if not update_docker_compose(model_config['file'], context_size, model_config['name']):
        return {"success": False, "error": "Failed to update docker-compose.yml"}

    # Restart container with appropriate warmup
    if not restart_container(model_config['warmup']):
        return {"success": False, "error": "Failed to restart container"}

    # Health check with retry (3min initial + 60s retries)
    if not check_model_health_with_retry(max_retries=5):
        return {"success": False, "error": "Model failed to become healthy after retries"}

    # Warmup queries (2 queries, 15s each)
    warmup_queries()

    # Run test script with adaptive timeout based on context size
    # Larger contexts need more time (each query takes longer)
    if context_size < 20000:
        test_timeout = 3600  # 1 hour for < 20k
    elif context_size < 26000:
        test_timeout = 5400  # 1.5 hours for 20k-24k
    elif context_size < 30000:
        test_timeout = 7200  # 2 hours for 26k-28k
    else:
        test_timeout = 10800  # 3 hours for 30k-32k

    log(f"Running validation test with {test_timeout/3600:.1f}h timeout...")
    cmd = f"cd {RESULTS_DIR} && python {model_config['test_script']} {context_size}"
    success, output = run_command(
        cmd,
        f"Validation test {context_size//1000}k",
        timeout=test_timeout
    )

    elapsed = time.time() - start_time

    if success:
        log(f"OK Test completed in {elapsed/60:.1f} minutes")

        result = {
            "success": True,
            "model": model_config['name'],
            "context_size": context_size,
            "elapsed_minutes": elapsed / 60,
            "timestamp": datetime.now().isoformat()
        }
    else:
        log(f"FAIL Test failed after {elapsed/60:.1f} minutes", "ERROR")
        result = {
            "success": False,
            "model": model_config['name'],
            "context_size": context_size,
            "error": output[:500],
            "elapsed_minutes": elapsed / 60,
            "timestamp": datetime.now().isoformat()
        }

    return result

def test_model_full_range(model_config: dict) -> list:
    """Test a model across all its context sizes."""
    log(f"\n{'='*80}")
    log(f"STARTING MODEL: {model_config['name']}")
    log(f"Contexts: {[c//1000 for c in model_config['contexts']]}k")
    log(f"Total tests: {len(model_config['contexts'])}")
    log(f"{'='*80}\n")

    results = []

    for i, context in enumerate(model_config['contexts'], 1):
        log(f"\n[{i}/{len(model_config['contexts'])}] Testing {context//1000}k...")

        result = test_model_at_context(model_config, context)
        results.append(result)

        if not result['success']:
            log(f"WARN Test failed at {context//1000}k, continuing with next context", "WARN")

        # Cooldown between contexts (1 minute - optimized)
        if i < len(model_config['contexts']):
            log("Cooldown for 60s before next context...")
            time.sleep(60)

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main automation function."""
    log("\n" + "="*80)
    log("MASTER 32K LIMIT TESTING - 4 MODELS SEQUENTIAL")
    log("="*80)
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Total models: {len(MODELS)}")
    log(f"Total contexts: {sum(len(m['contexts']) for m in MODELS)}")
    log("="*80 + "\n")

    overall_start = time.time()
    all_results = {}

    for i, model_config in enumerate(MODELS, 1):
        log(f"\n{'='*80}")
        log(f"MODEL {i}/{len(MODELS)}: {model_config['name']}")
        log(f"{'='*80}\n")

        model_results = test_model_full_range(model_config)
        all_results[model_config['name']] = model_results

        # Save intermediate results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"32k_limit_test_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(all_results, f, indent=2)

        log(f"OK Saved intermediate results to {results_file}")

        # Cooldown between models (10 minutes)
        if i < len(MODELS):
            log(f"\nModel {i} complete. Cooldown for {COOLDOWN_BETWEEN_MODELS}s before next model...")
            time.sleep(COOLDOWN_BETWEEN_MODELS)

    overall_elapsed = time.time() - overall_start

    # Generate final report
    log("\n" + "="*80)
    log("ALL TESTING COMPLETE!")
    log("="*80)
    log(f"Total Time: {overall_elapsed/3600:.1f} hours")
    log(f"Models Tested: {len(MODELS)}")

    for model_name, results in all_results.items():
        successful = len([r for r in results if r.get('success')])
        log(f"  {model_name}: {successful}/{len(results)} successful")

    log("="*80 + "\n")

    # Final results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_file = f"32K_LIMIT_TEST_FINAL_RESULTS_{timestamp}.json"
    with open(final_file, "w") as f:
        json.dump(all_results, f, indent=2)

    log(f"FILE Final results: {final_file}")
    log(f"FILE Log: master_32k_test_log.txt")

    # Shut down container
    log("\nShutting down containers...")
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
