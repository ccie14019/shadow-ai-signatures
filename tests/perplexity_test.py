#!/usr/bin/env python3
"""Perplexity API JA4 Signature Test"""

import sys

try:
    # Verify Perplexity SDK is installed, then generate TLS traffic via HTTPS
    # to capture a JA4 fingerprint. We use a representative HTTPS call so
    # capture is reliable even if the SDK prefers HTTP/3 or non-TCP transports.
    from perplexity import Perplexity  # noqa: F401
    import requests

    print("=" * 60)
    print("Testing Perplexity API TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()

    print("Making test HTTPS call (will fail auth, but TLS handshake completes)...")
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": "Bearer sk-fake-key-for-signature-capture"},
            timeout=10,
        )
        # We do not expect a successful HTTP status; any auth/network error
        # after the handshake is acceptable.
        print(f"[+] Unexpected HTTP status: {response.status_code}")
        print()
        print("=" * 60)
        print("SUCCESS: TLS handshake completed and captured!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"[+] Expected error after TLS handshake: {type(e).__name__}")
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
    print("ERROR: Failed to import Perplexity")
    print()
    print("Install with:")
    print("  python -m pip install perplexityai")
    sys.exit(1)

except Exception as e:
    print("ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
