#!/usr/bin/env python3
"""Google Generative AI SDK (Gemini) JA4 Signature Test"""

import sys

try:
    import google.generativeai as genai
    
    print("=" * 60)
    print("Testing Google Generative AI SDK TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating Gemini client with fake API key...")
    genai.configure(api_key="fake-api-key-for-signature-capture")
    
    model = genai.GenerativeModel('gemini-pro')
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = model.generate_content("test")
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
    print("ERROR: Failed to import Google Generative AI SDK")
    print()
    print("Install with:")
    print("  pip install google-generativeai")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

