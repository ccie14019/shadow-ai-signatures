#!/usr/bin/env python3
"""
Test Runner for Shadow AI Signature Collection
This script simulates the testing workflow for local development
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Project directories
BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
LOGS_DIR = BASE_DIR / "logs"
SIGNATURES_DIR = BASE_DIR / "signatures"
TESTS_DIR = BASE_DIR / "tests"
SCRIPTS_DIR = BASE_DIR / "scripts"

def ensure_directories():
    """Create necessary directories"""
    for dir_path in [PCAPS_DIR, LOGS_DIR, SIGNATURES_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

def run_test_framework(framework_name, install_cmd, test_script):
    """Run a framework test using the test script"""
    print(f"\n{'='*60}")
    print(f"Testing Framework: {framework_name}")
    print(f"{'='*60}\n")
    
    # Set mock capture mode for local testing
    env = os.environ.copy()
    env['MOCK_CAPTURE'] = 'true'
    
    script_path = SCRIPTS_DIR / "test_framework.sh"
    
    if not script_path.exists():
        print(f"ERROR: Test script not found: {script_path}")
        return False
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    try:
        result = subprocess.run(
            [str(script_path), framework_name, install_cmd, test_script],
            env=env,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR running test: {e}")
        return False

def calculate_ja4_from_pcap(pcap_file):
    """Calculate JA4 signature from PCAP file"""
    if not pcap_file.exists():
        print(f"WARNING: PCAP file not found: {pcap_file}")
        return None
    
    calculator = SCRIPTS_DIR / "ja4_calculator.py"
    
    if not calculator.exists():
        print(f"ERROR: JA4 calculator not found: {calculator}")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, str(calculator), str(pcap_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"ERROR calculating JA4: {result.stderr}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    """Main test runner"""
    print("="*60)
    print("Shadow AI Signature Collection - Test Runner")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    ensure_directories()
    
    # Test configurations
    test_configs = [
        {
            "name": "langchain",
            "install": "pip install langchain langchain-openai",
            "test_script": str(TESTS_DIR / "langchain_test.py")
        },
        {
            "name": "openai",
            "install": "pip install openai",
            "test_script": str(TESTS_DIR / "openai_test.py")
        },
        {
            "name": "anthropic",
            "install": "pip install anthropic",
            "test_script": str(TESTS_DIR / "anthropic_test.py")
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n{'='*60}")
        print(f"Testing: {config['name']}")
        print(f"{'='*60}")
        
        # Run the test
        success = run_test_framework(
            config['name'],
            config['install'],
            config['test_script']
        )
        
        if success:
            # Find the generated PCAP file
            pcap_files = list(PCAPS_DIR.glob(f"{config['name']}_*.pcap"))
            
            if pcap_files:
                latest_pcap = max(pcap_files, key=lambda p: p.stat().st_mtime)
                print(f"\nFound PCAP: {latest_pcap}")
                
                # Note: In mock mode, PCAPs are empty
                # In production, you would calculate JA4 here
                print("\nNOTE: In mock mode, PCAP files are placeholders.")
                print("      In production, run:")
                print(f"      python3 scripts/ja4_calculator.py {latest_pcap}")
            
            results.append({
                "framework": config['name'],
                "status": "success",
                "pcap": str(latest_pcap) if pcap_files else None
            })
        else:
            results.append({
                "framework": config['name'],
                "status": "failed"
            })
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['framework']}: {result['status']}")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Install actual frameworks: pip install langchain openai anthropic")
    print("2. Run tests with real network capture (requires tcpdump)")
    print("3. Calculate JA4 signatures from captured PCAPs")
    print("4. Document signatures in signatures/ directory")
    print("5. Add to signature_database.csv")
    print("="*60)

if __name__ == "__main__":
    main()

