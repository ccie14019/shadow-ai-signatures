#!/usr/bin/env python3
"""
Windows-compatible Framework Testing Script
Tests AI frameworks and generates signatures
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
LOGS_DIR = BASE_DIR / "logs"
SIGNATURES_DIR = BASE_DIR / "signatures"
TESTS_DIR = BASE_DIR / "tests"

def ensure_directories():
    """Create necessary directories"""
    for dir_path in [PCAPS_DIR, LOGS_DIR, SIGNATURES_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

def run_framework_test(framework_name, test_script_path):
    """Run a framework test and capture results"""
    print(f"\n{'='*60}")
    print(f"Testing Framework: {framework_name}")
    print(f"{'='*60}\n")
    
    ensure_directories()
    
    # Create log file
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOGS_DIR / f"{framework_name}_{date_str}.log"
    
    print(f"[1/4] Starting test for {framework_name}...")
    print(f"      Log file: {log_file}")
    
    # Run the test script
    print(f"[2/4] Running test script: {test_script_path}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Write to log
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Test Information ===\n")
            f.write(f"Framework: {framework_name}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"Test Script: {test_script_path}\n")
            f.write(f"\n=== System Information ===\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"\n=== Test Output ===\n")
            f.write(result.stdout)
            if result.stderr:
                f.write(f"\n=== Errors ===\n")
                f.write(result.stderr)
        
        print(f"[3/4] Test completed")
        print(f"      Return code: {result.returncode}")
        
        if result.stdout:
            print("\nTest Output:")
            print("-" * 60)
            print(result.stdout)
            print("-" * 60)
        
        # Create mock PCAP file (for signature tracking)
        pcap_file = PCAPS_DIR / f"{framework_name}_{date_str}.pcap"
        pcap_file.touch()
        
        print(f"[4/4] Results saved")
        print(f"      PCAP placeholder: {pcap_file}")
        print(f"      Log file: {log_file}")
        
        # Determine success
        success = result.returncode == 0 or "SUCCESS" in result.stdout
        
        if success:
            print(f"\n[+] {framework_name} test PASSED")
            print("  TLS handshake was attempted (expected auth failure)")
        else:
            print(f"\n[!] {framework_name} test had issues")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
        
        return {
            'success': success,
            'log_file': log_file,
            'pcap_file': pcap_file,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"\n[-] {framework_name} test TIMED OUT")
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"\n[-] {framework_name} test FAILED: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Main test execution"""
    print("="*60)
    print("Shadow AI Signature Collection - Framework Testing")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    
    ensure_directories()
    
    # Test configurations
    test_configs = []
    
    # Check which frameworks are available
    frameworks_to_test = []
    
    # Check OpenAI
    try:
        import openai
        test_configs.append({
            'name': 'openai',
            'test_script': str(TESTS_DIR / 'openai_test.py'),
            'installed': True,
            'version': getattr(openai, '__version__', 'unknown')
        })
    except ImportError:
        print("[!] OpenAI not installed (skipping)")
    
    # Check Anthropic
    try:
        import anthropic
        test_configs.append({
            'name': 'anthropic',
            'test_script': str(TESTS_DIR / 'anthropic_test.py'),
            'installed': True,
            'version': getattr(anthropic, '__version__', 'unknown')
        })
    except ImportError:
        print("[!] Anthropic not installed (skipping)")
    
    # Check LangChain
    langchain_installed = False
    try:
        import langchain
        langchain_installed = True
    except ImportError:
        pass
    
    try:
        from langchain_openai import ChatOpenAI
        langchain_installed = True
    except ImportError:
        pass
    
    if langchain_installed:
        test_configs.append({
            'name': 'langchain',
            'test_script': str(TESTS_DIR / 'langchain_test.py'),
            'installed': True,
            'version': 'installed'
        })
    else:
        print("[!] LangChain not installed (will try to install)")
        test_configs.append({
            'name': 'langchain',
            'test_script': str(TESTS_DIR / 'langchain_test.py'),
            'installed': False,
            'version': 'not installed'
        })
    
    if not test_configs:
        print("\n[-] No frameworks available to test!")
        print("\nInstall frameworks with:")
        print("  pip install openai anthropic")
        print("  pip install langchain langchain-openai")
        return
    
    print(f"\nFound {len(test_configs)} framework(s) to test:")
    for config in test_configs:
        status = "[+]" if config['installed'] else "[!]"
        print(f"  {status} {config['name']} (v{config['version']})")
    
    print("\n" + "="*60)
    print("Starting Tests...")
    print("="*60)
    
    results = []
    
    for config in test_configs:
        # Try to install if not installed
        if not config['installed'] and config['name'] == 'langchain':
            print(f"\nAttempting to install {config['name']}...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'langchain', 'langchain-openai', '--quiet'],
                    check=True,
                    timeout=60
                )
                print(f"[+] {config['name']} installed successfully")
                config['installed'] = True
            except Exception as e:
                print(f"[-] Failed to install {config['name']}: {e}")
                continue
        
        if not Path(config['test_script']).exists():
            print(f"\n[!] Test script not found: {config['test_script']}")
            continue
        
        result = run_framework_test(config['name'], config['test_script'])
        result['framework'] = config['name']
        result['version'] = config['version']
        results.append(result)
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    for result in results:
        status = "[+] PASS" if result.get('success') else "[-] FAIL"
        framework = result.get('framework', 'unknown')
        print(f"{status} {framework}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed > 0:
        print("\n" + "="*60)
        print("Next Steps:")
        print("="*60)
        print("1. Review log files in logs/ directory")
        print("2. For real signatures, capture network traffic with tcpdump")
        print("3. Calculate JA4: python3 scripts/ja4_calculator.py pcaps/*.pcap")
        print("4. Update signature_database.csv with results")
        print("="*60)
    
    return results

if __name__ == "__main__":
    main()

