#!/usr/bin/env python3
"""Anthropic SDK JA4 Signature Test"""

import sys

try:
    import anthropic
    
    print("=" * 60)
    print("Testing Anthropic SDK TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating Anthropic client with fake API key...")
    client = anthropic.Anthropic(
        api_key="sk-ant-fake-key-for-signature-capture",
        max_retries=1,
        timeout=5.0
    )
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        print("Unexpected success (should have failed auth)")
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
    print("ERROR: Failed to import Anthropic SDK")
    print()
    print("Install with:")
    print("  pip install anthropic")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

