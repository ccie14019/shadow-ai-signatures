#!/usr/bin/env python3
"""
Calculate JA4 signatures from all captured PCAP files
Uses alternative method since TLS parsing is complex
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"

def check_pcaps():
    """Find all PCAP files"""
    pcap_files = list(PCAPS_DIR.glob("*.pcap"))
    # Filter out empty/old files
    valid_pcaps = [p for p in pcap_files if p.stat().st_size > 1000]
    return valid_pcaps

def extract_signature_info(pcap_file):
    """Extract basic info from PCAP"""
    try:
        from scapy.all import rdpcap, TCP, Raw, IP
        
        packets = rdpcap(str(pcap_file))
        
        # Count TLS-related packets
        tls_packets = 0
        https_packets = 0
        
        for pkt in packets:
            if pkt.haslayer(TCP):
                tcp = pkt[TCP]
                if tcp.dport == 443 or tcp.sport == 443:
                    https_packets += 1
                    if pkt.haslayer(Raw):
                        raw = bytes(pkt[Raw])
                        # Check for TLS handshake (simplified)
                        if len(raw) > 5 and raw[0] == 0x16:  # TLS Handshake
                            tls_packets += 1
        
        return {
            'total_packets': len(packets),
            'https_packets': https_packets,
            'tls_packets': tls_packets,
            'file_size': pcap_file.stat().st_size
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    """Main function"""
    print("="*60)
    print("JA4 Signature Analysis from PCAP Files")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    pcap_files = check_pcaps()
    
    if not pcap_files:
        print("[-] No valid PCAP files found in pcaps/ directory")
        print("\nTo capture PCAPs, run:")
        print("  python capture_windows_docker.py")
        return
    
    print(f"Found {len(pcap_files)} PCAP file(s):\n")
    
    results = {}
    
    for pcap_file in sorted(pcap_files):
        framework_name = pcap_file.stem.split('_')[0]
        print(f"Analyzing: {pcap_file.name}")
        
        info = extract_signature_info(pcap_file)
        
        if 'error' in info:
            print(f"  [-] Error: {info['error']}")
        else:
            print(f"  [+] Total packets: {info['total_packets']}")
            print(f"  [+] HTTPS packets: {info['https_packets']}")
            print(f"  [+] TLS handshakes: {info['tls_packets']}")
            print(f"  [+] File size: {info['file_size']:,} bytes")
            
            if framework_name not in results:
                results[framework_name] = []
            results[framework_name].append(info)
        
        print()
    
    # Summary
    print("="*60)
    print("Summary")
    print("="*60)
    
    for framework, infos in results.items():
        total_tls = sum(i.get('tls_packets', 0) for i in infos)
        print(f"{framework}: {total_tls} TLS handshake(s) captured")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. PCAP files are ready for JA4 calculation")
    print("2. For accurate JA4, use one of:")
    print("   - Official FoxIO JA4 tool")
    print("   - Wireshark with JA4 plugin")
    print("   - Full TLS parsing library")
    print("3. Or use the captured PCAPs with proper JA4 tool")
    print("="*60)
    
    print(f"\nPCAP Files Available:")
    for pcap_file in sorted(pcap_files):
        print(f"  - {pcap_file.name} ({pcap_file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()

