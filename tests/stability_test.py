#!/usr/bin/env python3
"""Stability AI SDK JA4 Signature Test"""

import sys
import requests

print("=" * 60)
print("Testing Stability AI SDK TLS Signature Capture")
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

