#!/usr/bin/env python3
"""
Test Remaining Frameworks
Uses existing capture infrastructure to test and capture traffic
"""

import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"

# Frameworks to test (that have test scripts)
FRAMEWORKS = [
    ('ai21', 'ai21_test.py'),
    ('autogen', 'autogen_test.py'),
    ('haystack', 'haystack_test.py'),
    ('perplexity', 'perplexity_test.py'),
    ('replicate', 'replicate_test.py'),
    ('transformers', 'transformers_test.py'),
]

def main():
    """Test remaining frameworks"""
    print("="*60)
    print("Testing Remaining Frameworks")
    print("="*60)
    print(f"\nFrameworks to test: {len(FRAMEWORKS)}")
    for name, script in FRAMEWORKS:
        print(f"  - {name}")
    print()
    
    results = []
    
    for framework_name, test_script in FRAMEWORKS:
        test_path = TESTS_DIR / test_script
        
        if not test_path.exists():
            print(f"\n[!] Skipping {framework_name}: test script not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing: {framework_name.upper()}")
        print(f"{'='*60}")
        
        # Use existing capture script
        print(f"[+] Starting test with network capture...")
        try:
            # Import and use the capture function
            sys.path.insert(0, str(BASE_DIR))
            from capture_windows_docker import test_framework_with_capture
            
            success = test_framework_with_capture(
                framework_name,
                test_script,
                use_docker=False  # Use scapy (works better on Windows)
            )
            
            if success:
                print(f"[+] {framework_name}: SUCCESS")
                results.append((framework_name, 'success'))
            else:
                print(f"[!] {framework_name}: Completed (may have issues)")
                results.append((framework_name, 'partial'))
        
        except Exception as e:
            print(f"[-] {framework_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
            results.append((framework_name, 'error'))
        
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("Testing Summary")
    print("="*60)
    
    success_count = len([r for r in results if r[1] == 'success'])
    partial_count = len([r for r in results if r[1] == 'partial'])
    error_count = len([r for r in results if r[1] == 'error'])
    
    print(f"\n[+] Success: {success_count}")
    print(f"[!] Partial: {partial_count}")
    print(f"[-] Errors: {error_count}")
    
    # Calculate signatures
    if success_count > 0 or partial_count > 0:
        print("\n" + "="*60)
        print("Calculating Improved JA4 Signatures")
        print("="*60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "calculate_all_improved_ja4.py")],
                timeout=60
            )
            print("\n[+] Signatures calculated!")
        except Exception as e:
            print(f"\n[!] Error calculating signatures: {e}")
    
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("1. Review PCAPs: pcaps/")
    print("2. Check database: signatures/signature_database.csv")
    print("3. Validate: python validate_signatures.py")
    print("="*60)

if __name__ == "__main__":
    main()

