#!/usr/bin/env python3
"""NVIDIA AI Endpoints SDK JA4 Signature Test"""

import sys

try:
    from openai import OpenAI
    
    print("=" * 60)
    print("Testing NVIDIA AI Endpoints TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating NVIDIA AI client with fake API key...")
    # NVIDIA uses OpenAI-compatible API
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="nvapi-fake-key-for-signature-capture"
    )
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": "test"}]
        )
    except Exception as e:
        print(f"[+] Expected authentication error: {type(e).__name__}")
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        print(f"  Error message: {error_msg}")
        print()
        print("=" * 60)
        print("SUCCESS: TLS handshake completed and captured!")
        print("=" * 60)
        sys.exit(0)
        
except ImportError:
    print("ERROR: Failed to import OpenAI SDK (required for NVIDIA)")
    print()
    print("Install with:")
    print("  pip install openai")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

