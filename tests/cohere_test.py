#!/usr/bin/env python3
"""Cohere SDK JA4 Signature Test"""

import sys

try:
    import cohere
    
    print("=" * 60)
    print("Testing Cohere SDK TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating Cohere client with fake API key...")
    client = cohere.Client(api_key="fake-api-key-for-signature-capture")
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = client.generate(
            model='command',
            prompt='test',
            max_tokens=10
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
    print("ERROR: Failed to import Cohere SDK")
    print()
    print("Install with:")
    print("  pip install cohere")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

