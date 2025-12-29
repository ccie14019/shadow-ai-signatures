#!/usr/bin/env python3
"""
Capture network traffic for all tested frameworks
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

FRAMEWORKS = [
    ('openai', 'openai_test.py'),
    ('anthropic', 'anthropic_test.py'),
    ('langchain', 'langchain_test.py'),
    ('google_gemini', 'google_gemini_test.py'),
    ('cohere', 'cohere_test.py'),
    ('mistral', 'mistral_test.py'),
    ('together', 'together_test.py'),
    ('llamaindex', 'llamaindex_test.py'),
    ('crewai', 'crewai_test.py'),
    ('ollama', 'ollama_test.py'),
    ('ai21', 'ai21_test.py'),
    ('autogen', 'autogen_test.py'),
    ('gpt4all', 'gpt4all_test.py'),
    ('groq', 'groq_test.py'),
    ('haystack', 'haystack_test.py'),
    ('langflow', 'langflow_test.py'),
    ('nvidia', 'nvidia_test.py'),
    ('perplexity', 'perplexity_test.py'),
    ('replicate', 'replicate_test.py'),
    ('runpod', 'runpod_test.py'),
    ('semantic_kernel', 'semantic_kernel_test.py'),
    ('stability', 'stability_test.py'),
    ('transformers', 'transformers_test.py'),
    ('vertexai', 'vertexai_test.py'),
]

def capture_with_scapy(framework_name, duration=15):
    """Capture network traffic using scapy"""
    try:
        from scapy.all import sniff, wrpcap, TCP, Raw
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pcap_file = f"{framework_name}_{timestamp}.pcap"
        pcap_path = PCAPS_DIR / pcap_file
        
        packets = []
        capture_done = threading.Event()
        
        def packet_handler(pkt):
            if pkt.haslayer(TCP):
                tcp = pkt[TCP]
                if tcp.dport == 443 or tcp.sport == 443:
                    packets.append(pkt)
        
        def start_capture():
            sniff(filter="tcp port 443", prn=packet_handler, timeout=duration)
            capture_done.set()
        
        capture_thread = threading.Thread(target=start_capture)
        capture_thread.start()
        
        return capture_thread, packets, pcap_path, capture_done
        
    except ImportError:
        print("[-] Scapy not available")
        return None, None, None, None

def test_framework_with_capture(framework_name, test_script):
    """Test framework while capturing traffic"""
    print(f"\n{'='*60}")
    print(f"Capturing: {framework_name}")
    print(f"{'='*60}")
    
    # Start capture
    capture_thread, packets, pcap_path, capture_done = capture_with_scapy(framework_name, duration=15)
    
    if not capture_thread:
        return False
    
    print(f"[1/3] Capture started...")
    time.sleep(2)  # Wait for capture to initialize
    
    # Run test
    print(f"[2/3] Running test...")
    test_path = TESTS_DIR / test_script
    if test_path.exists():
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        success = result.returncode == 0 and "SUCCESS" in result.stdout
        print(f"      Test: {'PASSED' if success else 'FAILED'}")
    else:
        print(f"      [-] Test script not found")
        success = False
    
    # Wait for capture
    print(f"[3/3] Waiting for capture to finish...")
    capture_thread.join()
    
    # Save packets
    if packets:
        from scapy.all import wrpcap
        wrpcap(str(pcap_path), packets)
        print(f"      [+] Captured {len(packets)} packets")
        print(f"      [+] Saved: {pcap_path.name}")
        return True
    else:
        print(f"      [!] No packets captured")
        return False

def main():
    """Main function"""
    print("="*60)
    print("Shadow AI - Capture All Frameworks")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nCapturing traffic for {len(FRAMEWORKS)} framework(s)...")
    
    results = []
    
    for framework_name, test_script in FRAMEWORKS:
        result = test_framework_with_capture(framework_name, test_script)
        results.append((framework_name, result))
        time.sleep(2)  # Delay between tests
    
    # Summary
    print("\n" + "="*60)
    print("Capture Summary")
    print("="*60)
    
    for framework_name, success in results:
        status = "[+] SUCCESS" if success else "[-] FAILED"
        print(f"{status} {framework_name}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{len(results)} frameworks captured")
    
    if passed > 0:
        print("\n[+] PCAP files ready in pcaps/ directory")
        print("    Next: Calculate JA4 signatures")

if __name__ == "__main__":
    main()

