#!/usr/bin/env python3
"""
Template for testing Python AI frameworks
Modify for each specific framework

This script:
1. Imports the framework
2. Makes a minimal HTTPS connection
3. Expects auth to fail (we use fake keys)
4. But TLS handshake completes (which we capture)
"""

import sys

# MODIFY: Import your framework here
try:
    # Example for LangChain:
    # from langchain_openai import ChatOpenAI
    
    # Example for OpenAI SDK:
    # from openai import OpenAI
    
    # Example for Anthropic:
    # import anthropic
    
    print("Testing FRAMEWORK_NAME TLS signature...")
    print(f"Python version: {sys.version}")
    
    # MODIFY: Create client with fake API key
    # The connection will fail auth but TLS handshake will complete
    
    # Example for LangChain:
    # llm = ChatOpenAI(
    #     api_key="sk-fake-key-for-signature-capture",
    #     max_retries=1,
    #     request_timeout=5
    # )
    
    # Example for OpenAI:
    # client = OpenAI(
    #     api_key="sk-fake-key",
    #     max_retries=1,
    #     timeout=5.0
    # )
    
    try:
        # MODIFY: Make a minimal API call
        # This will fail auth but complete TLS handshake
        
        # Example for LangChain:
        # response = llm.invoke("test")
        
        # Example for OpenAI:
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": "test"}]
        # )
        
        pass  # Remove this, add actual call above
        
    except Exception as e:
        # This is EXPECTED - auth will fail
        # But we've captured the TLS handshake
        print(f"Expected error (auth failed): {type(e).__name__}")
        print("TLS handshake captured successfully!")
        sys.exit(0)  # Success (we got the handshake)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the framework is installed")
    sys.exit(1)
    
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

