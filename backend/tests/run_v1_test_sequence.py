"""
Automated Test Sequence Runner for 3-Phase Test v1
Runs multiple context sizes sequentially with docker-compose restarts
"""

import subprocess
import time
from datetime import datetime

# Test sequence: 12k, 15k, 18k, 21k, 24k, 27k, 30k
CONTEXT_SIZES = [12000, 15000, 18000, 21000, 24000, 27000, 30000]

# Docker container name
CONTAINER_NAME = "phi-4-reasoning-plus-v1-test"

def update_docker_compose(context_size):
    """Update docker-compose.yml with new context size."""
    docker_compose_path = "D:/gpt-oss/docker-compose.yml"

    # Read current docker-compose.yml
    with open(docker_compose_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace context size
    import re
    content = re.sub(
        r'--ctx-size \d+',
        f'--ctx-size {context_size}',
        content
    )

    # Replace container name
    content = re.sub(
        r'container_name: phi-4.*',
        f'container_name: {CONTAINER_NAME}-{context_size//1000}k',
        content
    )

    # Write updated docker-compose.yml
    with open(docker_compose_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated docker-compose.yml: {context_size//1000}k context")

def restart_llm_container():
    """Restart llama.cpp container."""
    print("Restarting llama.cpp container...")

    # Stop current container
    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'stop', 'llama'],
                   cwd='D:/gpt-oss', check=False)

    # Remove container
    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'rm', '-f', 'llama'],
                   cwd='D:/gpt-oss', check=False)

    # Start new container
    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'up', '-d', 'llama'],
                   cwd='D:/gpt-oss', check=True)

    print("✓ Container restarted")

    # Wait for warmup
    print("Waiting 180s for model warmup...")
    time.sleep(180)
    print("✓ Warmup complete")

def run_test(context_size):
    """Run 3-phase test v1 for given context size."""
    print(f"\n{'='*80}")
    print(f"STARTING TEST: {context_size//1000}k Context (v1)")
    print(f"{'='*80}")

    output_file = f"phi4_{context_size//1000}k_v1_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    cmd = [
        'python',
        'phi4_3phase_test_v1.py',
        str(context_size)
    ]

    print(f"Command: {' '.join(cmd)}")
    print(f"Output: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(
            cmd,
            cwd='D:/gpt-oss/backend/tests',
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )

        print(f"✓ Test started (PID: {process.pid})")
        print(f"  Output redirected to: {output_file}")
        print(f"  Monitoring in real-time...")

        # Wait for completion
        process.wait()

        if process.returncode == 0:
            print(f"✓ Test completed successfully")
        else:
            print(f"✗ Test failed with return code: {process.returncode}")

    return output_file

def main():
    """Run full test sequence."""
    start_time = time.time()

    print("="*80)
    print("3-PHASE TEST V1 - AUTOMATED SEQUENCE")
    print("="*80)
    print(f"Test sequence: {[f'{ctx//1000}k' for ctx in CONTEXT_SIZES]}")
    print(f"Total tests: {len(CONTEXT_SIZES)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    results = []

    for i, context_size in enumerate(CONTEXT_SIZES, 1):
        test_start = time.time()

        print(f"\n\n### TEST {i}/{len(CONTEXT_SIZES)}: {context_size//1000}k Context ###\n")

        try:
            # Update docker-compose
            update_docker_compose(context_size)

            # Restart container
            restart_llm_container()

            # Run test
            output_file = run_test(context_size)

            test_elapsed = (time.time() - test_start) / 60

            results.append({
                "context_size": context_size,
                "status": "success",
                "elapsed_minutes": test_elapsed,
                "output_file": output_file
            })

            print(f"\n✓ {context_size//1000}k test complete ({test_elapsed:.1f} min)")

        except Exception as e:
            test_elapsed = (time.time() - test_start) / 60

            results.append({
                "context_size": context_size,
                "status": "failed",
                "error": str(e),
                "elapsed_minutes": test_elapsed
            })

            print(f"\n✗ {context_size//1000}k test failed: {e}")
            print("Continuing to next test...")

    # Summary
    total_elapsed = (time.time() - start_time) / 60

    print("\n\n" + "="*80)
    print("TEST SEQUENCE COMPLETE")
    print("="*80)
    print(f"Total time: {total_elapsed:.1f} minutes ({total_elapsed/60:.1f} hours)")
    print(f"\nResults:")

    for r in results:
        status_symbol = "✓" if r["status"] == "success" else "✗"
        print(f"  {status_symbol} {r['context_size']//1000}k: {r['status']} ({r['elapsed_minutes']:.1f} min)")
        if r["status"] == "success":
            print(f"     Output: {r['output_file']}")

    print("="*80)

if __name__ == "__main__":
    main()
