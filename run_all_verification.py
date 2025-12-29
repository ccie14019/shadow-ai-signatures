#!/usr/bin/env python3
"""
Run Verification Tests for All Frameworks
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

# All frameworks to test
FRAMEWORKS = [
    ('openai', TESTS_DIR / 'openai_test.py'),
    ('anthropic', TESTS_DIR / 'anthropic_test.py'),
    ('langchain', TESTS_DIR / 'langchain_test.py'),
    ('google_gemini', TESTS_DIR / 'google_gemini_test.py'),
    ('cohere', TESTS_DIR / 'cohere_test.py'),
    ('mistral', TESTS_DIR / 'mistral_test.py'),
    ('together', TESTS_DIR / 'together_test.py'),
    ('llamaindex', TESTS_DIR / 'llamaindex_test.py'),
    ('crewai', TESTS_DIR / 'crewai_test.py'),
    ('ollama', TESTS_DIR / 'ollama_test.py'),
]

def run_single_test(framework_name, test_script, run_number):
    """Run a single test"""
    print(f"  Run {run_number}/3: Testing {framework_name}...", end=' ', flush=True)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0 and "SUCCESS" in result.stdout
        
        if success:
            print("[+] PASSED")
        else:
            print("[-] FAILED")
            if result.stderr:
                error_msg = result.stderr[:80].replace('\n', ' ')
                print(f"    Error: {error_msg}")
        
        return {
            'success': success,
            'output': result.stdout,
            'error': result.stderr,
            'run': run_number
        }
    except Exception as e:
        print(f"[-] ERROR: {str(e)[:50]}")
        return {'success': False, 'error': str(e), 'run': run_number}

def verify_framework(framework_name, test_script):
    """Run 3 verification tests for a framework"""
    print(f"\n{'='*60}")
    print(f"Verification Testing: {framework_name}")
    print(f"{'='*60}")
    
    if not test_script.exists():
        print(f"  [-] Test script not found: {test_script}")
        return None
    
    results = []
    
    for run_num in range(1, 4):
        result = run_single_test(framework_name, test_script, run_num)
        results.append(result)
        if run_num < 3:
            time.sleep(1)  # Small delay between runs
    
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
    print("Shadow AI Signature Collection - Full Verification Testing")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTesting {len(FRAMEWORKS)} frameworks (3 runs each)...")
    print("This verifies signature consistency across multiple runs")
    
    # Run verification for each
    verification_results = []
    
    for framework_name, test_script in FRAMEWORKS:
        result = verify_framework(framework_name, test_script)
        if result:
            verification_results.append(result)
        time.sleep(0.5)
    
    # Final summary
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)
    
    fully_verified = sum(1 for r in verification_results if r['passed'] == 3)
    total_frameworks = len(verification_results)
    total_runs = sum(r['total'] for r in verification_results)
    total_passed = sum(r['passed'] for r in verification_results)
    
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
    
    print(f"\n{'='*60}")
    print(f"Overall Statistics:")
    print(f"  Total Frameworks: {total_frameworks}")
    print(f"  Fully Verified: {fully_verified}/{total_frameworks}")
    print(f"  Total Test Runs: {total_passed}/{total_runs}")
    print(f"  Success Rate: {(total_passed/total_runs*100):.1f}%")
    print(f"{'='*60}")
    
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
    print("5. Update database: python update_signature_database.py")
    print("="*60)
    
    return verification_results

if __name__ == "__main__":
    main()

