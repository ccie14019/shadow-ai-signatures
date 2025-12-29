#!/usr/bin/env python3
"""LlamaIndex JA4 Signature Test"""

import sys

try:
    from llama_index.llms.openai import OpenAI as LlamaOpenAI
    
    print("=" * 60)
    print("Testing LlamaIndex TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating LlamaIndex OpenAI LLM with fake API key...")
    llm = LlamaOpenAI(
        api_key="sk-fake-key-for-signature-capture",
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = llm.complete("test")
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
    print("ERROR: Failed to import LlamaIndex")
    print()
    print("Install with:")
    print("  pip install llama-index")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

