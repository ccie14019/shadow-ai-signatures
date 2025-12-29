#!/usr/bin/env python3
"""
Test Additional Frameworks
Tests new frameworks and captures traffic
"""

import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"

# Additional frameworks to test
ADDITIONAL_FRAMEWORKS = [
    ('runpod', 'runpod_test.py', 'pip install runpod'),
    ('groq', 'groq_test.py', 'pip install groq'),
    ('vertexai', 'vertexai_test.py', 'pip install google-cloud-aiplatform'),
    ('nvidia', 'nvidia_test.py', 'pip install openai'),  # Uses OpenAI SDK
]

def check_installed(framework_name, install_cmd):
    """Check if framework is installed"""
    test_script = TESTS_DIR / f"{framework_name}_test.py"
    if not test_script.exists():
        return False, "Test script not found"
    
    # Try importing
    try:
        if framework_name == 'runpod':
            import runpod
        elif framework_name == 'groq':
            import groq
        elif framework_name == 'vertexai':
            import vertexai
        elif framework_name == 'nvidia':
            from openai import OpenAI  # NVIDIA uses OpenAI SDK
        return True, "Installed"
    except ImportError:
        return False, f"Not installed. Run: {install_cmd}"

def main():
    """Test additional frameworks"""
    print("="*60)
    print("Testing Additional Frameworks")
    print("="*60)
    print(f"\nFrameworks to test: {len(ADDITIONAL_FRAMEWORKS)}")
    for name, script, install in ADDITIONAL_FRAMEWORKS:
        print(f"  - {name}")
    print()
    
    results = []
    
    for framework_name, test_script, install_cmd in ADDITIONAL_FRAMEWORKS:
        print(f"\n{'='*60}")
        print(f"Testing: {framework_name.upper()}")
        print(f"{'='*60}")
        
        # Check installation
        installed, status = check_installed(framework_name, install_cmd)
        if not installed:
            print(f"[-] {status}")
            results.append((framework_name, 'not_installed'))
            continue
        
        print(f"[+] Framework installed")
        
        # Use existing capture script
        print(f"[+] Starting test with network capture...")
        try:
            sys.path.insert(0, str(BASE_DIR))
            from capture_windows_docker import test_framework_with_capture
            
            success = test_framework_with_capture(
                framework_name,
                test_script,
                use_docker=False
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
        
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("Testing Summary")
    print("="*60)
    
    success_count = len([r for r in results if r[1] == 'success'])
    partial_count = len([r for r in results if r[1] == 'partial'])
    not_installed = len([r for r in results if r[1] == 'not_installed'])
    error_count = len([r for r in results if r[1] == 'error'])
    
    print(f"\n[+] Success: {success_count}")
    print(f"[!] Partial: {partial_count}")
    print(f"[-] Not Installed: {not_installed}")
    print(f"[-] Errors: {error_count}")
    
    if not_installed > 0:
        print("\nTo install missing frameworks:")
        for name, script, install in ADDITIONAL_FRAMEWORKS:
            if any(r[0] == name and r[1] == 'not_installed' for r in results):
                print(f"  {install}")
    
    # Calculate signatures
    if success_count > 0 or partial_count > 0:
        print("\n" + "="*60)
        print("Calculating Full JA4 Signatures")
        print("="*60)
        
        try:
            import os
            wireshark_path = r"C:\Program Files\Wireshark"
            if os.path.exists(wireshark_path):
                os.environ["PATH"] = wireshark_path + os.pathsep + os.environ.get("PATH", "")
            
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "calculate_all_ja4_official.py")],
                timeout=120
            )
            print("\n[+] Signatures calculated!")
        except Exception as e:
            print(f"\n[!] Error calculating signatures: {e}")
    
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("1. Install missing frameworks if needed")
    print("2. Review PCAPs: pcaps/")
    print("3. Check database: signatures/signature_database.csv")
    print("4. Validate: python validate_signatures.py")
    print("="*60)

if __name__ == "__main__":
    main()

