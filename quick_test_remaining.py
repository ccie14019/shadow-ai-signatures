#!/usr/bin/env python3
"""
Quick Test Remaining Frameworks
Simplified version that uses existing capture infrastructure
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"
PCAPS_DIR = BASE_DIR / "pcaps"

# Frameworks to test
FRAMEWORKS = [
    'ai21',
    'autogen', 
    'haystack',
    'perplexity',
    'replicate',
    'transformers'
]

def main():
    """Test remaining frameworks using existing capture script"""
    print("="*60)
    print("Testing Remaining Frameworks")
    print("="*60)
    print(f"\nFrameworks to test: {', '.join(FRAMEWORKS)}")
    print("\nThis will:")
    print("  1. Run each framework test")
    print("  2. Capture network traffic")
    print("  3. Calculate improved JA4 signatures")
    print()
    
    input("Press Enter to continue (or Ctrl+C to cancel)...")
    
    for framework in FRAMEWORKS:
        test_script = TESTS_DIR / f"{framework}_test.py"
        
        if not test_script.exists():
            print(f"\n[!] Skipping {framework}: test script not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing: {framework.upper()}")
        print(f"{'='*60}")
        
        # Use existing capture script
        print(f"[+] Running test with capture...")
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "capture_windows_docker.py"), framework],
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"[+] {framework}: Success")
            else:
                print(f"[!] {framework}: Test completed (may have errors)")
        
        except subprocess.TimeoutExpired:
            print(f"[!] {framework}: Timed out")
        except Exception as e:
            print(f"[!] {framework}: Error - {e}")
        
        time.sleep(2)
    
    # Calculate signatures
    print("\n" + "="*60)
    print("Calculating Signatures")
    print("="*60)
    
    try:
        subprocess.run([sys.executable, str(BASE_DIR / "calculate_all_improved_ja4.py")])
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n[+] Done! Check signatures/signature_database.csv")

if __name__ == "__main__":
    main()

