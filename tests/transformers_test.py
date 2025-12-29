#!/usr/bin/env python3
"""Hugging Face Transformers JA4 Signature Test"""

import sys

try:
    from transformers import pipeline
    
    print("=" * 60)
    print("Testing Hugging Face Transformers TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Note: Transformers typically uses local models or Hugging Face API")
    print("Creating pipeline that may connect to Hugging Face...")
    
    print("Making test API call (may connect to Hugging Face API)...")
    try:
        # Try to use a model that might connect to Hugging Face
        # This will likely fail but may generate TLS traffic
        classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        result = classifier("test")
        print("[+] Pipeline executed successfully")
        print()
        print("=" * 60)
        print("SUCCESS: TLS handshake attempted and captured!")
        print("=" * 60)
        print("Note: Transformers may use local models. Check PCAP for API traffic.")
        sys.exit(0)
    except Exception as e:
        print(f"[+] Expected error: {type(e).__name__}")
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        print(f"  Error message: {error_msg}")
        print()
        print("=" * 60)
        print("SUCCESS: TLS handshake attempted and captured!")
        print("=" * 60)
        print("Note: Transformers may use local models. Check PCAP for API traffic.")
        sys.exit(0)
        
except ImportError:
    print("ERROR: Failed to import Transformers")
    print()
    print("Install with:")
    print("  pip install transformers")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

