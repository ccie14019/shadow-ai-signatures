#!/usr/bin/env python3
"""
Install and Test Additional Frameworks
Automatically installs missing frameworks and tests them
"""

import sys
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"

# Frameworks to install and test
FRAMEWORKS = [
    ('stability', 'stability_test.py', 'stability-sdk'),
    ('gpt4all', 'gpt4all_test.py', 'gpt4all'),
    ('semantic_kernel', 'semantic_kernel_test.py', 'semantic-kernel'),
    ('langflow', 'langflow_test.py', 'langflow'),
]

def install_framework(package_name):
    """Install a framework package"""
    print(f"[+] Installing {package_name}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"    [+] {package_name} installed successfully")
            return True
        else:
            print(f"    [-] Installation failed: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    [-] Installation timed out")
        return False
    except Exception as e:
        print(f"    [-] Error: {e}")
        return False

def test_framework(framework_name, test_script):
    """Test a framework with capture"""
    print(f"\n[+] Testing {framework_name}...")
    try:
        sys.path.insert(0, str(BASE_DIR))
        from capture_windows_docker import test_framework_with_capture
        
        success = test_framework_with_capture(
            framework_name,
            test_script,
            use_docker=False
        )
        
        return success
    except Exception as e:
        print(f"    [-] Error: {e}")
        return False

def main():
    """Install and test frameworks"""
    print("="*60)
    print("Install and Test Additional Frameworks")
    print("="*60)
    print(f"\nFrameworks: {len(FRAMEWORKS)}")
    for name, script, package in FRAMEWORKS:
        print(f"  - {name} ({package})")
    print()
    
    results = []
    
    for framework_name, test_script, package_name in FRAMEWORKS:
        print(f"\n{'='*60}")
        print(f"Framework: {framework_name.upper()}")
        print(f"{'='*60}")
        
        # Check if installed
        test_file = TESTS_DIR / test_script
        if not test_file.exists():
            print(f"[-] Test script not found: {test_script}")
            results.append((framework_name, 'no_script'))
            continue
        
        # Try importing
        try:
            if framework_name == 'stability':
                import stability_sdk
            elif framework_name == 'gpt4all':
                import gpt4all
            elif framework_name == 'semantic_kernel':
                import semantic_kernel
            elif framework_name == 'langflow':
                import langflow
            print(f"[+] Already installed")
        except ImportError:
            # Install
            if not install_framework(package_name):
                results.append((framework_name, 'install_failed'))
                continue
        
        # Test
        success = test_framework(framework_name, test_script)
        if success:
            results.append((framework_name, 'success'))
        else:
            results.append((framework_name, 'test_failed'))
        
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    success = len([r for r in results if r[1] == 'success'])
    failed = len([r for r in results if r[1] in ['install_failed', 'test_failed', 'no_script']])
    
    print(f"\n[+] Successfully tested: {success}")
    print(f"[-] Failed: {failed}")
    
    # Calculate signatures
    if success > 0:
        print("\n" + "="*60)
        print("Calculating Full JA4 Signatures")
        print("="*60)
        
        try:
            import os
            wireshark_path = r"C:\Program Files\Wireshark"
            if os.path.exists(wireshark_path):
                os.environ["PATH"] = wireshark_path + os.pathsep + os.environ.get("PATH", "")
            
            subprocess.run(
                [sys.executable, str(BASE_DIR / "calculate_all_ja4_official.py")],
                timeout=120
            )
            print("\n[+] Done! Check signatures/signature_database.csv")
        except Exception as e:
            print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()

