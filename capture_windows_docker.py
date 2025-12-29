#!/usr/bin/env python3
"""
Windows-compatible Docker Network Capture
Uses Docker to capture traffic from host network
"""

import subprocess
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
TESTS_DIR = BASE_DIR / "tests"
PCAPS_DIR.mkdir(exist_ok=True)

def capture_with_docker(framework_name, duration=10):
    """Capture network traffic using Docker"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pcap_file = f"{framework_name}_{timestamp}.pcap"
    pcap_path = PCAPS_DIR / pcap_file
    
    print(f"\n[1/3] Starting Docker capture...")
    print(f"      Duration: {duration} seconds")
    print(f"      Output: {pcap_file}")
    
    # On Windows, we need to use a different approach
    # Option 1: Use Docker's default bridge network
    # Option 2: Use WSL2 if available
    # Option 3: Use host.docker.internal
    
    # Try using Docker with host network (may not work on Windows)
    # Fallback to using scapy directly if Docker fails
    
    cmd = [
        'docker', 'run', '--rm',
        '--network', 'host',
        '-v', f'{PCAPS_DIR.absolute()}:/pcaps',
        'corfr/tcpdump:latest',
        'timeout', str(duration),
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
        return process, pcap_path
    except Exception as e:
        print(f"      [-] Docker capture failed: {e}")
        return None, None

def capture_with_scapy(framework_name, duration=10):
    """Alternative: Use scapy to capture directly (no Docker)"""
    print(f"\n[!] Using scapy for direct capture (no Docker needed)")
    print(f"    Duration: {duration} seconds")
    
    try:
        from scapy.all import sniff, wrpcap
        from scapy.layers.inet import IP, TCP
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pcap_file = f"{framework_name}_{timestamp}.pcap"
        pcap_path = PCAPS_DIR / pcap_file
        
        packets = []
        
        def packet_handler(pkt):
            # Capture HTTPS traffic (port 443)
            if pkt.haslayer(TCP):
                if pkt[TCP].dport == 443 or pkt[TCP].sport == 443:
                    packets.append(pkt)
        
        print(f"    Capturing on all interfaces...")
        print(f"    Run your test now!")
        
        # Start capture in thread
        def start_capture():
            sniff(filter="tcp port 443", prn=packet_handler, timeout=duration)
        
        capture_thread = threading.Thread(target=start_capture)
        capture_thread.start()
        
        return capture_thread, packets, pcap_path
        
    except ImportError:
        print("[-] Scapy not available")
        return None, None, None
    except Exception as e:
        print(f"[-] Scapy capture error: {e}")
        return None, None, None

def test_framework_with_capture(framework_name, test_script, use_docker=True):
    """Test framework while capturing network traffic"""
    print("="*60)
    print(f"Testing {framework_name} with Network Capture")
    print("="*60)
    
    if use_docker:
        # Try Docker first
        capture_process, pcap_path = capture_with_docker(framework_name, duration=15)
        
        if not capture_process:
            print("[!] Docker capture failed, trying scapy...")
            use_docker = False
    
    if not use_docker:
        # Use scapy directly
        capture_thread, packets, pcap_path = capture_with_scapy(framework_name, duration=15)
        
        if not capture_thread:
            print("[-] Both Docker and scapy capture failed")
            return False
        
        # Wait a moment for capture to start
        time.sleep(2)
        
        # Run test
        print(f"\n[2/3] Running framework test...")
        test_path = TESTS_DIR / test_script
        if test_path.exists():
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"      Test completed: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        
        # Wait for capture to finish
        capture_thread.join()
        
        # Save packets
        if packets:
            from scapy.all import wrpcap
            wrpcap(str(pcap_path), packets)
            print(f"      [+] Captured {len(packets)} packets")
        else:
            print(f"      [!] No packets captured")
            return False
    else:
        # Docker capture
        time.sleep(2)  # Wait for Docker to start
        
        # Run test
        print(f"\n[2/3] Running framework test...")
        test_path = TESTS_DIR / test_script
        if test_path.exists():
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"      Test completed: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        
        # Wait for Docker to finish
        capture_process.wait()
    
    # Verify PCAP
    print(f"\n[3/3] Verifying PCAP file...")
    if pcap_path.exists():
        size = pcap_path.stat().st_size
        print(f"      [+] PCAP file: {size} bytes")
        
        if size > 0:
            print(f"\n[+] SUCCESS! Ready to calculate JA4:")
            print(f"    python scripts/ja4_calculator.py {pcap_path}")
            return True
        else:
            print(f"      [!] PCAP file is empty")
            return False
    else:
        print(f"      [-] PCAP file not found")
        return False

def main():
    """Main function"""
    print("="*60)
    print("Shadow AI - Windows Network Capture")
    print("="*60)
    
    # Test frameworks
    if len(sys.argv) > 1:
        # If a framework name is passed as an argument, only test that one
        fw = sys.argv[1]
        frameworks = [
            (fw, f"{fw}_test.py"),
        ]
    else:
        frameworks = [
            ('openai', 'openai_test.py'),
            ('anthropic', 'anthropic_test.py'),
            ('langchain', 'langchain_test.py'),
        ]
    
    print(f"\nTesting {len(frameworks)} framework(s) with network capture")
    print("This will capture TLS traffic and create PCAP files")
    
    results = []
    for framework_name, test_script in frameworks:
        result = test_framework_with_capture(framework_name, test_script, use_docker=False)
        results.append((framework_name, result))
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    for framework_name, success in results:
        status = "[+] PASS" if success else "[-] FAIL"
        print(f"{status} {framework_name}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{len(results)} tests with valid PCAPs")

if __name__ == "__main__":
    main()

