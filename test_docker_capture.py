#!/usr/bin/env python3
"""
Quick test of Docker-based network capture
"""

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
PCAPS_DIR.mkdir(exist_ok=True)

def test_docker_capture():
    """Test if we can capture network traffic with Docker"""
    print("="*60)
    print("Testing Docker Network Capture")
    print("="*60)
    
    # Check Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"[+] Docker: {result.stdout.strip()}")
    except:
        print("[-] Docker not found")
        return False
    
    # Check if image exists
    print("\n[!] Checking for tcpdump image...")
    result = subprocess.run(
        ['docker', 'images', 'corfr/tcpdump:latest'],
        capture_output=True,
        text=True
    )
    
    if 'corfr/tcpdump' not in result.stdout:
        print("[!] Pulling tcpdump image...")
        subprocess.run(['docker', 'pull', 'corfr/tcpdump:latest'])
    
    print("\n[+] Starting test capture (5 seconds)...")
    print("    This will capture any HTTPS traffic on port 443")
    
    # Start capture in background
    pcap_file = "test_capture.pcap"
    pcap_path = PCAPS_DIR / pcap_file
    
    cmd = [
        'docker', 'run', '--rm',
        '--network', 'host',
        '-v', f'{PCAPS_DIR.absolute()}:/pcaps',
        'corfr/tcpdump:latest',
        'timeout', '5', 'tcpdump', '-i', 'any', 'tcp', 'port', '443',
        '-w', f'/pcaps/{pcap_file}',
        '-v'
    ]
    
    print(f"\nRunning: {' '.join(cmd[:6])} ...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if pcap_path.exists():
            size = pcap_path.stat().st_size
            print(f"\n[+] PCAP file created: {size} bytes")
            
            if size > 0:
                print("[+] SUCCESS! Docker capture is working!")
                print(f"    File: {pcap_path}")
                return True
            else:
                print("[!] PCAP file is empty (no traffic captured)")
                print("    This is normal if no HTTPS traffic occurred")
                return True  # Still success, just no traffic
        else:
            print("[-] PCAP file not created")
            return False
            
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def main():
    success = test_docker_capture()
    
    print("\n" + "="*60)
    if success:
        print("[+] Docker capture test PASSED")
        print("\nNext steps:")
        print("1. Run: python capture_with_docker.py")
        print("2. Or manually start capture and run tests")
    else:
        print("[-] Docker capture test FAILED")
        print("\nTroubleshooting:")
        print("1. Make sure Docker Desktop is running")
        print("2. Check Docker has network access")
    print("="*60)

if __name__ == "__main__":
    main()

