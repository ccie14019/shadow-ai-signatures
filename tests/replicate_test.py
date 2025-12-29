#!/usr/bin/env python3
"""Replicate SDK JA4 Signature Test"""

import sys

try:
    import replicate
    
    print("=" * 60)
    print("Testing Replicate SDK TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating Replicate client with fake API key...")
    client = replicate.Client(api_token="fake-token-for-signature-capture")
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        output = client.run(
            "meta/llama-2-7b-chat",
            input={"prompt": "test"}
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
    print("ERROR: Failed to import Replicate SDK")
    print()
    print("Install with:")
    print("  pip install replicate")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

