#!/usr/bin/env python3
"""
Extract JA4-like signatures from PCAP files
Uses packet analysis to identify TLS characteristics
"""

import sys
from pathlib import Path
from collections import defaultdict
import hashlib

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"

try:
    from scapy.all import rdpcap, TCP, Raw, IP
except ImportError:
    print("ERROR: scapy not installed")
    print("Install with: pip install scapy")
    sys.exit(1)

def analyze_tls_packet(packet):
    """Analyze TLS packet and extract characteristics"""
    if not packet.haslayer(TCP):
        return None
    
    tcp = packet[TCP]
    if tcp.dport != 443 and tcp.sport != 443:
        return None
    
    if not packet.haslayer(Raw):
        return None
    
    raw_data = bytes(packet[Raw])
    
    # Check for TLS handshake (type 0x16)
    if len(raw_data) < 5 or raw_data[0] != 0x16:
        return None
    
    # Extract TLS version
    version = (raw_data[1] << 8) | raw_data[2]
    
    # Check for Client Hello (handshake type 1)
    if len(raw_data) > 5 and raw_data[5] == 0x01:
        return {
            'type': 'client_hello',
            'version': version,
            'data': raw_data
        }
    
    return None

def calculate_simple_ja4(pcap_file):
    """Calculate simplified JA4 from PCAP"""
    try:
        packets = rdpcap(str(pcap_file))
    except Exception as e:
        print(f"Error reading {pcap_file}: {e}")
        return []
    
    signatures = []
    seen_connections = set()
    
    for pkt in packets:
        if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
            continue
        
        ip = pkt[IP]
        tcp = pkt[TCP]
        
        # Create connection identifier
        conn_id = tuple(sorted([
            (ip.src, tcp.sport),
            (ip.dst, tcp.dport)
        ]))
        
        if conn_id in seen_connections:
            continue
        
        tls_info = analyze_tls_packet(pkt)
        if tls_info and tls_info['type'] == 'client_hello':
            seen_connections.add(conn_id)
            
            # Simplified JA4 calculation
            version_map = {
                0x0301: 't10',  # TLS 1.0
                0x0302: 't11',  # TLS 1.1
                0x0303: 't12',  # TLS 1.2
                0x0304: 't13'   # TLS 1.3
            }
            
            version_str = version_map.get(tls_info['version'], 't13')
            
            # Create hash from packet characteristics
            data_hash = hashlib.sha256(tls_info['data'][:100]).hexdigest()[:12]
            
            # Simplified signature (not full JA4, but identifiable)
            sig = f"{version_str}_simplified_{data_hash}"
            
            signatures.append({
                'signature': sig,
                'version': tls_info['version'],
                'src': ip.src,
                'dst': ip.dst,
                'sport': tcp.sport,
                'dport': tcp.dport
            })
    
    return signatures

def main():
    """Main function"""
    print("="*60)
    print("Extracting Signatures from PCAP Files")
    print("="*60)
    print("\nNote: This is a simplified extraction.")
    print("For full JA4, use official tool with tshark.\n")
    
    pcap_files = sorted(PCAPS_DIR.glob("*.pcap"))
    
    # Filter to recent captures
    valid_pcaps = [p for p in pcap_files if p.stat().st_size > 1000]
    
    if not valid_pcaps:
        print("[-] No valid PCAP files found")
        return
    
    print(f"Found {len(valid_pcaps)} PCAP file(s):\n")
    
    all_signatures = {}
    
    for pcap_file in valid_pcaps:
        framework = pcap_file.stem.split('_')[0]
        print(f"Analyzing: {pcap_file.name}")
        
        signatures = calculate_simple_ja4(pcap_file)
        
        if signatures:
            print(f"  [+] Found {len(signatures)} TLS handshake(s)")
            for sig_info in signatures:
                print(f"      Signature: {sig_info['signature']}")
                print(f"      Connection: {sig_info['src']}:{sig_info['sport']} -> {sig_info['dst']}:{sig_info['dport']}")
            
            if framework not in all_signatures:
                all_signatures[framework] = []
            all_signatures[framework].extend(signatures)
        else:
            print(f"  [-] No TLS handshakes found")
        
        print()
    
    # Summary
    print("="*60)
    print("Summary")
    print("="*60)
    
    for framework, sigs in all_signatures.items():
        unique_sigs = set(s['signature'] for s in sigs)
        print(f"{framework}: {len(sigs)} handshake(s), {len(unique_sigs)} unique signature(s)")
        if len(unique_sigs) == 1:
            print(f"  [+] Consistent signature: {list(unique_sigs)[0]}")
        elif len(unique_sigs) > 1:
            print(f"  [!] Multiple signatures found")
            for sig in unique_sigs:
                count = sum(1 for s in sigs if s['signature'] == sig)
                print(f"      {sig}: {count} occurrence(s)")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Install Wireshark/tshark for full JA4 calculation")
    print("2. Use official JA4 tool: python scripts/ja4-official/python/ja4.py <pcap>")
    print("3. Or use these simplified signatures for testing")
    print("="*60)

if __name__ == "__main__":
    main()

