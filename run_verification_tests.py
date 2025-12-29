#!/usr/bin/env python3
"""
Run Multiple Verification Tests
Tests each framework 3 times to verify signature consistency
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"
LOGS_DIR = BASE_DIR / "logs"
PCAPS_DIR = BASE_DIR / "pcaps"

def run_single_test(framework_name, test_script, run_number):
    """Run a single test"""
    print(f"\n  Run {run_number}/3: Testing {framework_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=60  # Increased from 30 to handle slower imports like vertexai
        )
        
        success = result.returncode == 0 and "SUCCESS" in result.stdout
        
        if success:
            print(f"    [+] PASSED - TLS handshake completed")
        else:
            print(f"    [-] FAILED - Check logs")
            if result.stderr:
                print(f"    Error: {result.stderr[:100]}")
        
        return {
            'success': success,
            'output': result.stdout,
            'error': result.stderr,
            'run': run_number
        }
    except Exception as e:
        print(f"    [-] ERROR: {e}")
        return {'success': False, 'error': str(e), 'run': run_number}

def verify_framework(framework_name, test_script):
    """Run 3 verification tests for a framework"""
    print(f"\n{'='*60}")
    print(f"Verification Testing: {framework_name}")
    print(f"{'='*60}")
    
    results = []
    
    for run_num in range(1, 4):
        result = run_single_test(framework_name, test_script, run_num)
        results.append(result)
        time.sleep(2)  # Small delay between runs
    
    # Summary
    passed = sum(1 for r in results if r.get('success', False))
    print(f"\n  Verification Results: {passed}/3 passed")
    
    if passed == 3:
        print(f"  [+] CONSISTENT - All 3 runs successful")
    elif passed >= 2:
        print(f"  [!] PARTIAL - {passed}/3 runs successful")
    else:
        print(f"  [-] INCONSISTENT - Only {passed}/3 runs successful")
    
    return {
        'framework': framework_name,
        'passed': passed,
        'total': 3,
        'results': results
    }

def main():
    """Main verification runner"""
    print("="*60)
    print("Shadow AI Signature Collection - Verification Testing")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRunning 3 verification tests for each framework...")
    print("(This verifies signature consistency)")
    
    # Test configurations - automatically discover all test scripts
    print("\nDiscovering available test scripts...")
    
    frameworks = []
    for test_file in sorted(TESTS_DIR.glob("*_test.py")):
        if test_file.name.startswith("TEMPLATE"):
            continue
        framework_name = test_file.stem.replace("_test", "")
        frameworks.append((framework_name, test_file))
    
    print(f"Found {len(frameworks)} framework test scripts")
    
    # Filter to only installed frameworks
    available_frameworks = []
    for name, script in frameworks:
        if script.exists():
            available_frameworks.append((name, script))
        else:
            print(f"\n[!] Skipping {name} - test script not found")
    
    if not available_frameworks:
        print("\n[-] No frameworks available to test!")
        return
    
    print(f"\nTesting {len(available_frameworks)} framework(s)")
    
    # Run verification for each
    verification_results = []
    
    for framework_name, test_script in available_frameworks:
        result = verify_framework(framework_name, test_script)
        verification_results.append(result)
        time.sleep(1)
    
    # Final summary
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)
    
    fully_verified = sum(1 for r in verification_results if r['passed'] == 3)
    total_frameworks = len(verification_results)
    
    for result in verification_results:
        framework = result['framework']
        passed = result['passed']
        total = result['total']
        
        if passed == 3:
            status = "[+] FULLY VERIFIED"
        elif passed >= 2:
            status = "[!] PARTIALLY VERIFIED"
        else:
            status = "[-] NOT VERIFIED"
        
        print(f"{status} {framework}: {passed}/{total} runs passed")
    
    print(f"\nTotal Frameworks: {total_frameworks}")
    print(f"Fully Verified: {fully_verified}/{total_frameworks}")
    
    if fully_verified == total_frameworks:
        print("\n[+] ALL FRAMEWORKS FULLY VERIFIED!")
        print("    Ready for signature collection")
    else:
        print(f"\n[!] {total_frameworks - fully_verified} framework(s) need attention")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Capture network traffic with tcpdump/Wireshark")
    print("2. Calculate JA4 signatures from PCAPs")
    print("3. Compare signatures across 3 runs (should be identical)")
    print("4. Document in signature_database.csv")
    print("="*60)
    
    return verification_results

if __name__ == "__main__":
    main()

