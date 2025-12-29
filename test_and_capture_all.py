#!/usr/bin/env python3
"""
Complete Testing and Capture Workflow
Tests remaining frameworks, captures traffic, calculates improved JA4
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"
PCAPS_DIR = BASE_DIR / "pcaps"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Frameworks to test (excluding already tested)
FRAMEWORKS_TO_TEST = [
    {
        'name': 'ai21',
        'test_script': 'ai21_test.py',
        'install': 'pip install ai21',
        'check_import': 'ai21'
    },
    {
        'name': 'autogen',
        'test_script': 'autogen_test.py',
        'install': 'pip install pyautogen',
        'check_import': 'autogen'
    },
    {
        'name': 'haystack',
        'test_script': 'haystack_test.py',
        'install': 'pip install haystack-ai',
        'check_import': 'haystack'
    },
    {
        'name': 'perplexity',
        'test_script': 'perplexity_test.py',
        'install': 'pip install perplexity-ai',
        'check_import': 'perplexity'
    },
    {
        'name': 'replicate',
        'test_script': 'replicate_test.py',
        'install': 'pip install replicate',
        'check_import': 'replicate'
    },
    {
        'name': 'transformers',
        'test_script': 'transformers_test.py',
        'install': 'pip install transformers',
        'check_import': 'transformers'
    },
]

def check_framework_installed(framework):
    """Check if framework is installed"""
    try:
        if '.' in framework['check_import']:
            parts = framework['check_import'].split('.')
            __import__(parts[0])
        else:
            __import__(framework['check_import'])
        return True
    except ImportError:
        return False

def test_framework_with_capture(framework):
    """Test framework and capture traffic"""
    print(f"\n{'='*60}")
    print(f"Testing: {framework['name'].upper()}")
    print(f"{'='*60}")
    
    # Check if installed
    if not check_framework_installed(framework):
        print(f"[-] Framework not installed")
        print(f"    Install with: {framework['install']}")
        return {'status': 'not_installed', 'framework': framework['name']}
    
    test_script = TESTS_DIR / framework['test_script']
    if not test_script.exists():
        print(f"[-] Test script not found: {test_script}")
        return {'status': 'no_script', 'framework': framework['name']}
    
    # Generate PCAP filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pcap_file = PCAPS_DIR / f"{framework['name']}_{timestamp}.pcap"
    
    print(f"[+] Framework installed")
    print(f"[+] Starting capture: {pcap_file.name}")
    
    # Import capture function
    sys.path.insert(0, str(BASE_DIR))
    try:
        from capture_windows_docker import capture_traffic
    except ImportError:
        print("[-] Capture module not found")
        return {'status': 'capture_error', 'framework': framework['name']}
    
    # Start capture in background
    print(f"[+] Starting network capture...")
    capture_process = None
    try:
        # Use scapy-based capture
        from scapy.all import sniff, wrpcap
        import threading
        import queue
        
        packets = []
        capture_queue = queue.Queue()
        stop_capture = threading.Event()
        
        def packet_handler(pkt):
            if pkt.haslayer('IP') and pkt.haslayer('TCP'):
                tcp = pkt['TCP']
                if tcp.dport == 443 or tcp.sport == 443:
                    packets.append(pkt)
        
        def capture_thread():
            sniff(prn=packet_handler, stop_filter=lambda x: stop_capture.is_set(), timeout=10)
            capture_queue.put(packets)
        
        capture_thread_obj = threading.Thread(target=capture_thread, daemon=True)
        capture_thread_obj.start()
        
        # Wait a moment for capture to start
        time.sleep(1)
        
        # Run test
        print(f"[+] Running test script...")
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"[+] Test completed successfully")
            else:
                print(f"[+] Test completed (expected auth error)")
            
            # Show output
            if result.stdout:
                for line in result.stdout.strip().split('\n')[-5:]:
                    if line.strip():
                        print(f"    {line}")
        
        except subprocess.TimeoutExpired:
            print(f"[!] Test timed out")
        except Exception as e:
            print(f"[!] Test error: {e}")
        
        # Stop capture
        time.sleep(2)  # Give time for final packets
        stop_capture.set()
        capture_thread_obj.join(timeout=2)
        
        # Get captured packets
        try:
            captured_packets = capture_queue.get(timeout=1)
        except queue.Empty:
            captured_packets = packets
        
        # Save PCAP
        if captured_packets:
            wrpcap(str(pcap_file), captured_packets)
            print(f"[+] Captured {len(captured_packets)} packets")
            print(f"[+] Saved to: {pcap_file.name}")
            return {
                'status': 'success',
                'framework': framework['name'],
                'pcap': pcap_file,
                'packets': len(captured_packets)
            }
        else:
            print(f"[-] No packets captured")
            return {'status': 'no_packets', 'framework': framework['name']}
    
    except Exception as e:
        print(f"[-] Capture error: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'framework': framework['name'], 'error': str(e)}

def main():
    """Main testing workflow"""
    print("="*60)
    print("Complete Framework Testing & Capture Workflow")
    print("="*60)
    print(f"\nTesting {len(FRAMEWORKS_TO_TEST)} framework(s)")
    print(f"Using improved JA4 calculator (no Wireshark required)")
    print()
    
    results = []
    
    for framework in FRAMEWORKS_TO_TEST:
        result = test_framework_with_capture(framework)
        results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("Testing Summary")
    print("="*60)
    
    success = [r for r in results if r.get('status') == 'success']
    not_installed = [r for r in results if r.get('status') == 'not_installed']
    errors = [r for r in results if r.get('status') in ['error', 'no_packets', 'capture_error']]
    
    print(f"\n[+] Successfully tested: {len(success)}")
    for r in success:
        print(f"    {r['framework']}: {r.get('packets', 0)} packets")
    
    if not_installed:
        print(f"\n[-] Not installed: {len(not_installed)}")
        for r in not_installed:
            print(f"    {r['framework']}: {FRAMEWORKS_TO_TEST[next(i for i, f in enumerate(FRAMEWORKS_TO_TEST) if f['name'] == r['framework'])]['install']}")
    
    if errors:
        print(f"\n[!] Errors: {len(errors)}")
        for r in errors:
            print(f"    {r['framework']}: {r.get('status', 'unknown')}")
    
    # Calculate signatures
    if success:
        print("\n" + "="*60)
        print("Calculating Improved JA4 Signatures")
        print("="*60)
        
        try:
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "calculate_all_improved_ja4.py")],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"Error calculating signatures: {e}")
    
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("1. Review captured PCAPs in: pcaps/")
    print("2. Check signatures in: signatures/signature_database.csv")
    print("3. Run validation: python validate_signatures.py")
    print("="*60)

if __name__ == "__main__":
    main()

