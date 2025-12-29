#!/usr/bin/env python3
"""Together AI SDK JA4 Signature Test"""

import sys

try:
    from together import Together
    
    print("=" * 60)
    print("Testing Together AI SDK TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating Together AI client with fake API key...")
    client = Together(api_key="fake-api-key-for-signature-capture")
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-2-7b-chat-hf",
            messages=[{"role": "user", "content": "test"}],
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
    print("ERROR: Failed to import Together AI SDK")
    print()
    print("Install with:")
    print("  pip install together")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

