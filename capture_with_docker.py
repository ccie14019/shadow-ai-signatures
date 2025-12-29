#!/usr/bin/env python3
"""
Docker-based Network Capture for Shadow AI Testing
Captures TLS traffic while running framework tests
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
TESTS_DIR = BASE_DIR / "tests"

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[+] Docker available: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("[-] Docker not found. Install Docker Desktop for Windows")
        return False
    return False

def start_capture(framework_name):
    """Start tcpdump capture in Docker container"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pcap_file = f"{framework_name}_{timestamp}.pcap"
    pcap_path = PCAPS_DIR / pcap_file
    
    # Ensure pcaps directory exists
    PCAPS_DIR.mkdir(exist_ok=True)
    
    print(f"\n[1/4] Starting network capture...")
    print(f"      PCAP file: {pcap_file}")
    
    # Start tcpdump container
    # Using host network mode to capture all traffic
    cmd = [
        'docker', 'run', '--rm',
        '--network', 'host',
        '-v', f'{PCAPS_DIR.absolute()}:/pcaps',
        'corfr/tcpdump:latest',
        'tcpdump', '-i', 'any', 'tcp', 'port', '443',
        '-w', f'/pcaps/{pcap_file}',
        '-v'
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"      Capture started (PID: {process.pid})")
        time.sleep(3)  # Wait for tcpdump to initialize
        return process, pcap_path
    except Exception as e:
        print(f"[-] Failed to start capture: {e}")
        return None, None

def run_framework_test(framework_name, test_script):
    """Run framework test script"""
    print(f"[2/4] Running framework test: {framework_name}")
    
    test_path = TESTS_DIR / test_script
    if not test_path.exists():
        print(f"[-] Test script not found: {test_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print(f"      [+] Test completed successfully")
            return True
        else:
            print(f"      [-] Test had issues")
            return False
    except Exception as e:
        print(f"      [-] Test error: {e}")
        return False

def stop_capture(process):
    """Stop tcpdump capture"""
    print(f"[3/4] Stopping capture...")
    time.sleep(2)  # Let any remaining packets be captured
    
    try:
        process.terminate()
        process.wait(timeout=5)
        print(f"      [+] Capture stopped")
        return True
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"      [!] Capture force stopped")
        return True
    except Exception as e:
        print(f"      [-] Error stopping capture: {e}")
        return False

def verify_pcap(pcap_path):
    """Verify PCAP file was created and has data"""
    print(f"[4/4] Verifying PCAP file...")
    
    if not pcap_path.exists():
        print(f"      [-] PCAP file not found: {pcap_path}")
        return False
    
    size = pcap_path.stat().st_size
    print(f"      [+] PCAP file created: {size} bytes")
    
    if size == 0:
        print(f"      [!] WARNING: PCAP file is empty")
        print(f"      [!] This may indicate no traffic was captured")
        return False
    
    # Try to check if it has TLS packets using scapy
    try:
        from scapy.all import rdpcap
        packets = rdpcap(str(pcap_path))
        tls_count = sum(1 for p in packets if p.haslayer('TLS'))
        print(f"      [+] Found {len(packets)} total packets")
        print(f"      [+] Found {tls_count} TLS packets")
        return tls_count > 0
    except Exception as e:
        print(f"      [!] Could not analyze PCAP: {e}")
        print(f"      [+] PCAP file exists ({size} bytes)")
        return True

def test_with_capture(framework_name, test_script):
    """Complete test workflow with Docker capture"""
    print("="*60)
    print(f"Testing {framework_name} with Docker Network Capture")
    print("="*60)
    
    # Start capture
    capture_process, pcap_path = start_capture(framework_name)
    if not capture_process:
        return False
    
    try:
        # Run test
        test_success = run_framework_test(framework_name, test_script)
        
        # Stop capture
        stop_capture(capture_process)
        
        # Verify PCAP
        pcap_valid = verify_pcap(pcap_path)
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Framework: {framework_name}")
        print(f"Test: {'PASSED' if test_success else 'FAILED'}")
        print(f"PCAP: {'VALID' if pcap_valid else 'INVALID'}")
        print(f"PCAP File: {pcap_path}")
        
        if pcap_valid:
            print(f"\n[+] SUCCESS! Ready to calculate JA4:")
            print(f"    python scripts/ja4_calculator.py {pcap_path}")
        
        return test_success and pcap_valid
        
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        stop_capture(capture_process)
        return False
    except Exception as e:
        print(f"\n[-] Error during test: {e}")
        stop_capture(capture_process)
        return False

def main():
    """Main function"""
    print("="*60)
    print("Shadow AI Signature Collection - Docker Capture")
    print("="*60)
    
    # Check Docker
    if not check_docker():
        print("\n[-] Docker is required for network capture")
        print("\nInstall Docker Desktop:")
        print("  https://www.docker.com/products/docker-desktop")
        return
    
    # Check if tcpdump image exists
    print("\n[!] Checking for tcpdump Docker image...")
    result = subprocess.run(
        ['docker', 'images', 'corfr/tcpdump:latest'],
        capture_output=True,
        text=True
    )
    
    if 'corfr/tcpdump' not in result.stdout:
        print("[!] Pulling tcpdump Docker image...")
        subprocess.run(['docker', 'pull', 'corfr/tcpdump:latest'])
    
    # Test frameworks
    frameworks = [
        ('openai', 'openai_test.py'),
        ('anthropic', 'anthropic_test.py'),
        ('langchain', 'langchain_test.py'),
    ]
    
    print(f"\n[+] Ready to test {len(frameworks)} framework(s)")
    print("\nStarting tests with network capture...")
    
    results = []
    for framework_name, test_script in frameworks:
        result = test_with_capture(framework_name, test_script)
        results.append((framework_name, result))
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("Final Summary")
    print("="*60)
    
    for framework_name, success in results:
        status = "[+] PASS" if success else "[-] FAIL"
        print(f"{status} {framework_name}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed > 0:
        print("\n[+] PCAP files ready for JA4 calculation!")
        print("    Run: python scripts/ja4_calculator.py pcaps/*.pcap")

if __name__ == "__main__":
    main()

