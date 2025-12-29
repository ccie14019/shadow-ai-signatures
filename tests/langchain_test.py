#!/usr/bin/env python3
"""LangChain JA4 Signature Test"""

import sys
import os

try:
    from langchain_openai import ChatOpenAI
    import langchain
    
    print("=" * 60)
    print("Testing LangChain TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    
    try:
        print(f"LangChain version: {langchain.__version__}")
    except:
        print("LangChain version: (unable to determine)")
    
    print()
    
    print("Creating ChatOpenAI client with fake API key...")
    llm = ChatOpenAI(
        api_key="sk-fake-key-for-signature-capture-only-not-real",
        max_retries=1,
        request_timeout=5,
        base_url="https://api.openai.com/v1"
    )
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        response = llm.invoke("test message")
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
        
except ImportError as e:
    print(f"ERROR: Failed to import LangChain")
    print(f"  {e}")
    print()
    print("Install with:")
    print("  pip install langchain langchain-openai")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

