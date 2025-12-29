#!/usr/bin/env python3
"""
Simplified JA4 Calculator
Works with standard scapy (no TLS layer dependencies)
"""

import sys
import hashlib
from pathlib import Path
from collections import defaultdict

try:
    from scapy.all import rdpcap, Raw, IP, TCP
except ImportError:
    print("ERROR: scapy not installed")
    print("Install with: pip install scapy")
    sys.exit(1)

def parse_tls_client_hello(packet_data):
    """Parse TLS Client Hello from raw packet data"""
    # This is a simplified parser - for production use proper TLS parsing
    # Look for TLS handshake type 1 (Client Hello)
    if len(packet_data) < 5:
        return None
    
    # Check for TLS record header
    if packet_data[0] != 0x16:  # TLS Handshake
        return None
    
    # Check for TLS 1.2/1.3
    version = (packet_data[1] << 8) | packet_data[2]
    if version not in [0x0301, 0x0302, 0x0303, 0x0304]:
        return None
    
    # Find Client Hello (type 1)
    # Skip record header (5 bytes) and look for handshake
    offset = 5
    if len(packet_data) <= offset:
        return None
    
    if packet_data[offset] != 0x01:  # Client Hello
        return None
    
    # Extract basic info (simplified)
    # In production, properly parse TLS structure
    return {
        'version': version,
        'found': True
    }

def calculate_ja4_simple(pcap_file):
    """Calculate JA4 from PCAP using simplified method"""
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"Error reading PCAP: {e}")
        return []
    
    signatures = []
    
    for pkt in packets:
        # Look for HTTPS traffic (port 443)
        if pkt.haslayer(TCP):
            tcp = pkt[TCP]
            if tcp.dport == 443 or tcp.sport == 443:
                # Check if it has raw data (TLS handshake)
                if pkt.haslayer(Raw):
                    raw_data = bytes(pkt[Raw])
                    tls_info = parse_tls_client_hello(raw_data)
                    if tls_info:
                        # Simplified JA4 calculation
                        # For real implementation, parse full TLS structure
                        version_str = f"t{hex(tls_info['version'])[-1]}"
                        # This is a placeholder - real JA4 needs full parsing
                        sig = f"{version_str}_simplified_signature"
                        signatures.append(sig)
    
    return signatures

def main():
    if len(sys.argv) < 2:
        print("Usage: python ja4_simple.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    
    print(f"Analyzing {pcap_file}...")
    print("Note: This is a simplified version")
    print("For full JA4 calculation, use proper TLS parsing library")
    print("-" * 60)
    
    signatures = calculate_ja4_simple(pcap_file)
    
    if signatures:
        print(f"Found {len(signatures)} potential TLS handshake(s)")
        print("\nFor accurate JA4 signatures, use:")
        print("1. Wireshark to export TLS details")
        print("2. Official JA4 tool from FoxIO")
        print("3. Full TLS parsing library")
    else:
        print("No TLS Client Hello packets found")
        print("\nTroubleshooting:")
        print("1. Verify PCAP has HTTPS traffic")
        print("2. Check packets contain TLS handshakes")

if __name__ == "__main__":
    main()

