#!/usr/bin/env python3
"""
Improved JA4 Calculator - Works without tshark
Parses TLS Client Hello more accurately than simplified version
"""

import sys
import hashlib
import struct
from pathlib import Path
from collections import defaultdict

try:
    from scapy.all import rdpcap, IP, TCP, Raw
except ImportError:
    print("ERROR: scapy not installed")
    print("Install with: pip install scapy")
    sys.exit(1)

def parse_tls_client_hello(raw_data):
    """Parse TLS Client Hello packet more accurately"""
    if len(raw_data) < 5:
        return None
    
    # TLS Record Header (5 bytes)
    # Byte 0: Content Type (0x16 = Handshake)
    # Bytes 1-2: Version
    # Bytes 3-4: Length
    
    if raw_data[0] != 0x16:  # Not a TLS Handshake
        return None
    
    # Extract TLS version
    version = struct.unpack('>H', raw_data[1:3])[0]
    
    # Skip record header (5 bytes)
    if len(raw_data) < 6:
        return None
    
    # Handshake message type (byte 5)
    if raw_data[5] != 0x01:  # Not Client Hello
        return None
    
    # Parse Client Hello structure
    # Skip handshake header (4 bytes: type, length(3))
    offset = 9  # 5 (record) + 4 (handshake header)
    
    if len(raw_data) <= offset:
        return None
    
    # Client Hello structure:
    # - Version (2 bytes) - already have from record
    # - Random (32 bytes)
    # - Session ID length (1 byte) + Session ID
    # - Cipher Suites length (2 bytes) + Cipher Suites
    # - Compression methods length (1 byte) + Compression methods
    # - Extensions length (2 bytes) + Extensions
    
    try:
        # Skip random (32 bytes)
        offset += 32
        
        # Session ID
        if len(raw_data) <= offset:
            return None
        session_id_len = raw_data[offset]
        offset += 1 + session_id_len
        
        # Cipher Suites
        if len(raw_data) <= offset + 1:
            return None
        cipher_suites_len = struct.unpack('>H', raw_data[offset:offset+2])[0]
        offset += 2
        cipher_suites = []
        for i in range(0, cipher_suites_len, 2):
            if len(raw_data) <= offset + 1:
                break
            cipher = struct.unpack('>H', raw_data[offset:offset+2])[0]
            cipher_suites.append(cipher)
            offset += 2
        
        # Compression methods
        if len(raw_data) <= offset:
            return None
        compression_len = raw_data[offset]
        offset += 1 + compression_len
        
        # Extensions
        if len(raw_data) <= offset + 1:
            return None
        extensions_len = struct.unpack('>H', raw_data[offset:offset+2])[0]
        offset += 2
        extensions = []
        ext_offset = offset
        while ext_offset < offset + extensions_len and ext_offset < len(raw_data) - 3:
            ext_type = struct.unpack('>H', raw_data[ext_offset:ext_offset+2])[0]
            ext_len = struct.unpack('>H', raw_data[ext_offset+2:ext_offset+4])[0]
            extensions.append(ext_type)
            ext_offset += 4 + ext_len
        
        # Check for ALPN (extension type 16)
        alpn_present = 16 in extensions
        
        # Check SNI (extension type 0)
        sni_present = 0 in extensions
        
        return {
            'version': version,
            'cipher_suites': cipher_suites,
            'extensions': extensions,
            'alpn': alpn_present,
            'sni': sni_present,
            'valid': True
        }
    except (IndexError, struct.error):
        return None

def calculate_ja4_improved(tls_data):
    """Calculate improved JA4 signature"""
    # Protocol version
    version_map = {
        0x0301: 't10',  # TLS 1.0
        0x0302: 't11',  # TLS 1.1
        0x0303: 't12',  # TLS 1.2
        0x0304: 't13'   # TLS 1.3
    }
    protocol = version_map.get(tls_data['version'], 't13')
    
    # SNI
    sni = 'd' if tls_data['sni'] else 'i'
    
    # Cipher count (max 99)
    cipher_count = min(len(tls_data['cipher_suites']), 99)
    cipher_count_str = f"{cipher_count:02d}"
    
    # Extension count (max 99)
    ext_count = min(len(tls_data['extensions']), 99)
    ext_count_str = f"{ext_count:02d}"
    
    # ALPN
    alpn = "h2" if tls_data['alpn'] else "00"
    
    # First part
    part1 = f"{protocol}{sni}{cipher_count_str}{ext_count_str}{alpn}"
    
    # Cipher hash (sorted, hex format)
    cipher_hex = [f"{c:04x}" for c in sorted(tls_data['cipher_suites'])]
    cipher_string = ','.join(cipher_hex)
    cipher_hash = hashlib.sha256(cipher_string.encode()).hexdigest()[:12]
    
    # Extension hash (sorted)
    ext_string = ','.join(f"{e:04x}" for e in sorted(tls_data['extensions']))
    ext_hash = hashlib.sha256(ext_string.encode()).hexdigest()[:12]
    
    # Final JA4
    ja4 = f"{part1}_{cipher_hash}_{ext_hash}"
    
    return ja4

def extract_ja4_from_pcap(pcap_file):
    """Extract JA4 signatures from PCAP file"""
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
        
        # Only HTTPS traffic
        if tcp.dport != 443 and tcp.sport != 443:
            continue
        
        # Connection identifier
        conn_id = tuple(sorted([
            (ip.src, tcp.sport),
            (ip.dst, tcp.dport)
        ]))
        
        if conn_id in seen_connections:
            continue
        
        # Extract TLS data
        if pkt.haslayer(Raw):
            raw_data = bytes(pkt[Raw])
            tls_data = parse_tls_client_hello(raw_data)
            
            if tls_data and tls_data.get('valid'):
                seen_connections.add(conn_id)
                ja4 = calculate_ja4_improved(tls_data)
                
                signatures.append({
                    'signature': ja4,
                    'src': ip.src,
                    'dst': ip.dst,
                    'sport': tcp.sport,
                    'dport': tcp.dport,
                    'version': tls_data['version'],
                    'ciphers': len(tls_data['cipher_suites']),
                    'extensions': len(tls_data['extensions'])
                })
    
    return signatures

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python ja4_improved.py <pcap_file> [pcap_file2 ...]")
        print("\nExample:")
        print("  python ja4_improved.py pcaps/openai_*.pcap")
        sys.exit(1)
    
    pcap_files = sys.argv[1:]
    all_signatures = defaultdict(list)
    
    for pcap_file in pcap_files:
        pcap_path = Path(pcap_file)
        if not pcap_path.exists():
            print(f"WARNING: File not found: {pcap_file}")
            continue
        
        print(f"\nAnalyzing: {pcap_path.name}")
        print("-" * 60)
        
        signatures = extract_ja4_from_pcap(pcap_path)
        
        if signatures:
            framework = pcap_path.stem.split('_')[0]
            all_signatures[framework].extend(signatures)
            
            print(f"Found {len(signatures)} TLS Client Hello packet(s):")
            for sig_info in signatures:
                print(f"  {sig_info['signature']}")
                print(f"    Connection: {sig_info['src']}:{sig_info['sport']} -> {sig_info['dst']}:{sig_info['dport']}")
                print(f"    Ciphers: {sig_info['ciphers']}, Extensions: {sig_info['extensions']}")
        else:
            print("  No TLS Client Hello packets found")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for framework, sigs in all_signatures.items():
        unique_sigs = set(s['signature'] for s in sigs)
        print(f"\n{framework}:")
        print(f"  Total handshakes: {len(sigs)}")
        print(f"  Unique signatures: {len(unique_sigs)}")
        
        if len(unique_sigs) == 1:
            print(f"  [+] Consistent: {list(unique_sigs)[0]}")
        else:
            sig_counts = defaultdict(int)
            for s in sigs:
                sig_counts[s['signature']] += 1
            print(f"  [!] Multiple signatures:")
            for sig, count in sorted(sig_counts.items(), key=lambda x: -x[1]):
                print(f"      {sig}: {count} occurrence(s)")

if __name__ == "__main__":
    main()

