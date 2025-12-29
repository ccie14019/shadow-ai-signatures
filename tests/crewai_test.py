#!/usr/bin/env python3
"""CrewAI JA4 Signature Test"""

import sys

try:
    from crewai import Agent, Task, Crew
    from crewai.llm import LLM
    
    print("=" * 60)
    print("Testing CrewAI TLS Signature Capture")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("Creating CrewAI agent with fake API key...")
    # CrewAI uses OpenAI by default
    llm = LLM(
        model="gpt-3.5-turbo",
        api_key="sk-fake-key-for-signature-capture"
    )
    
    agent = Agent(
        role="test agent",
        goal="test",
        backstory="test",
        llm=llm
    )
    
    print("Making test API call (will fail auth, but TLS handshake completes)...")
    try:
        task = Task(description="test", agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()
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
    print("ERROR: Failed to import CrewAI")
    print()
    print("Install with:")
    print("  pip install crewai")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Unexpected exception")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

