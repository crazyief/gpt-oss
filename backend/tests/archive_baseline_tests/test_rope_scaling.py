#!/usr/bin/env python3
"""
Test RoPE scaling and context extension parameters for llama.cpp
"""

import requests
import json

def test_rope_parameters():
    """
    Test if the model supports RoPE scaling to extend context.
    Some models can use RoPE scaling to go beyond training context.
    """

    # Test with extended context using RoPE scaling
    test_configs = [
        {
            "name": "Standard 32k",
            "params": {
                "rope_freq_base": 10000,  # Standard RoPE
                "rope_freq_scale": 1.0
            }
        },
        {
            "name": "Linear scaling to 48k",
            "params": {
                "rope_freq_base": 10000,
                "rope_freq_scale": 0.66  # 32k/48k = 0.66
            }
        },
        {
            "name": "NTK-aware scaling to 48k",
            "params": {
                "rope_freq_base": 15000,  # Increase base frequency
                "rope_freq_scale": 1.0
            }
        },
        {
            "name": "YaRN scaling",
            "params": {
                "rope_freq_base": 10000,
                "rope_freq_scale": 0.66,
                "yarn_ext_factor": 1.0,
                "yarn_attn_factor": 1.0,
                "yarn_beta_fast": 32.0,
                "yarn_beta_slow": 1.0
            }
        }
    ]

    print("Testing RoPE scaling parameters for context extension...")
    print("="*60)

    for config in test_configs:
        print(f"\n{config['name']}:")
        print(f"Parameters: {json.dumps(config['params'], indent=2)}")

        # Create a long prompt to test
        test_prompt = "index 1: value 100\n" * 1500  # About 33k tokens
        test_prompt += "\nWhat is the value at index 1?"

        try:
            # Note: These parameters would need to be set when starting llama.cpp server
            # They can't be changed per-request in most cases
            response = requests.post(
                "http://localhost:8080/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": test_prompt}],
                    "temperature": 0,
                    "max_tokens": 10,
                    **config["params"]  # These won't work in standard llama.cpp
                },
                timeout=10
            )

            if response.status_code == 200:
                print("✓ Request successful")
            elif response.status_code == 400:
                error = response.json().get("error", {})
                if "exceed_context" in error.get("type", ""):
                    print(f"✗ Context exceeded: {error.get('n_prompt_tokens')} tokens")
                else:
                    print(f"✗ Error: {error.get('message')}")
            else:
                print(f"✗ HTTP {response.status_code}")

        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")

        print("-"*40)


def check_server_capabilities():
    """Check what the llama.cpp server actually supports"""

    endpoints = [
        "/props",
        "/slots",
        "/metrics"
    ]

    print("\nChecking server capabilities...")
    print("="*60)

    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8080{endpoint}")
            if response.status_code == 200:
                print(f"\n{endpoint}:")
                data = response.json()
                # Look for context-related info
                for key, value in data.items():
                    if any(term in str(key).lower() for term in ["ctx", "rope", "yarn", "context", "window"]):
                        print(f"  {key}: {value}")
        except:
            pass


if __name__ == "__main__":
    print("ROPE SCALING AND CONTEXT EXTENSION TEST")
    print("="*60)

    # First check server capabilities
    check_server_capabilities()

    print("\n" + "="*60)
    print("IMPORTANT: RoPE scaling parameters must be set when starting")
    print("the llama.cpp server, not per-request!")
    print("="*60)

    print("\nTo enable context extension, restart llama.cpp with:")
    print("--rope-freq-base 10000   # Standard")
    print("--rope-freq-scale 0.66   # For 1.5x context (48k)")
    print("--rope-scaling yarn      # Use YaRN scaling (best)")
    print("--ctx-size 48000         # Increase context limit")

    print("\nExample docker-compose.yml modification:")
    print("""
    llama:
      command: >
        --model /models/Mistral-Small-24B-Q6_K.gguf
        --host 0.0.0.0
        --port 8080
        --n-gpu-layers -1
        --ctx-size 48000        # Extend to 48k
        --rope-scaling yarn     # Use YaRN scaling
        --rope-freq-base 10000
        --rope-freq-scale 0.66  # 32k/48k = 0.66
        --yarn-ext-factor 1.0
        --yarn-attn-factor 1.0
    """)

    # Try to test if current config supports any scaling
    # test_rope_parameters()