"""
Automated Test Sequence Runner - Continue from 21k to 30k
Monitors 18k completion and automatically runs remaining tests
"""

import time
import os
import subprocess
from datetime import datetime

# Remaining context sizes to test
CONTEXT_SIZES = [21000, 24000, 27000, 30000]

def wait_for_18k_completion():
    """Wait for 18k test to complete by monitoring output file."""
    output_file = "D:/gpt-oss/backend/tests/phi4_18k_v1_output_20251122_151429.txt"

    print("="*80)
    print("AUTOMATED TEST SEQUENCE - WAITING FOR 18K COMPLETION")
    print("="*80)
    print(f"Monitoring: {output_file}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    while True:
        try:
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "VALIDATION COMPLETE" in content:
                        print(f"\n✅ 18k test completed at {datetime.now().strftime('%H:%M:%S')}")
                        return True
        except Exception as e:
            print(f"Error reading file: {e}")

        time.sleep(30)  # Check every 30 seconds

def update_docker_compose(context_size):
    """Update docker-compose.yml with new context size."""
    docker_compose_path = "D:/gpt-oss/docker-compose.yml"

    with open(docker_compose_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    content = re.sub(r'--ctx-size \d+', f'--ctx-size {context_size}', content)
    content = re.sub(r'container_name: phi-4.*',
                     f'container_name: phi-4-reasoning-plus-v1-{context_size//1000}k',
                     content)

    with open(docker_compose_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated docker-compose.yml: {context_size//1000}k context")

def restart_llm_container():
    """Restart llama.cpp container."""
    print("Restarting llama.cpp container...")

    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'stop', 'llama'],
                   cwd='D:/gpt-oss', check=False)
    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'rm', '-f', 'llama'],
                   cwd='D:/gpt-oss', check=False)
    subprocess.run(['docker-compose', '-f', 'D:/gpt-oss/docker-compose.yml', 'up', '-d', 'llama'],
                   cwd='D:/gpt-oss', check=True)

    print("✓ Container restarted")
    print("Waiting 180s for model warmup...")
    time.sleep(180)
    print("✓ Warmup complete")

def run_test(context_size):
    """Run 3-phase test v1 for given context size."""
    print(f"\n{'='*80}")
    print(f"STARTING TEST: {context_size//1000}k Context (v1)")
    print(f"{'='*80}")

    output_file = f"phi4_{context_size//1000}k_v1_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    cmd = ['python', 'phi4_3phase_test_v1.py', str(context_size)]

    print(f"Command: {' '.join(cmd)}")
    print(f"Output: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(cmd, cwd='D:/gpt-oss/backend/tests',
                                   stdout=f, stderr=subprocess.STDOUT, text=True)
        print(f"✓ Test started (PID: {process.pid})")
        process.wait()

        if process.returncode == 0:
            print(f"✓ Test completed successfully")
        else:
            print(f"✗ Test failed with return code: {process.returncode}")

    return output_file

def main():
    """Main automation loop."""
    start_time = time.time()

    # Wait for 18k to complete
    wait_for_18k_completion()

    print(f"\n\n{'='*80}")
    print("STARTING AUTOMATED TEST SEQUENCE: 21k → 24k → 27k → 30k")
    print(f"{'='*80}\n")

    for context_size in CONTEXT_SIZES:
        test_start = time.time()

        print(f"\n### TEST: {context_size//1000}k Context ###\n")

        try:
            update_docker_compose(context_size)
            restart_llm_container()
            output_file = run_test(context_size)

            test_elapsed = (time.time() - test_start) / 60
            print(f"\n✓ {context_size//1000}k test complete ({test_elapsed:.1f} min)")

        except Exception as e:
            print(f"\n✗ {context_size//1000}k test failed: {e}")
            print("Continuing to next test...")

    total_elapsed = (time.time() - start_time) / 60
    print(f"\n\n{'='*80}")
    print("ALL TESTS COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {total_elapsed:.1f} minutes ({total_elapsed/60:.1f} hours)")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
