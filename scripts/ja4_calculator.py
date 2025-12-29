#!/usr/bin/env python3
"""
JA4 Fingerprint Calculator
Simplified implementation for Shadow AI signature collection

JA4 Format:
  [Protocol][SNI][CipherCount][ExtensionCount][ALPN]_
  [Cipher_Hash]_[Extension_Hash]

Example: t13d1516h2_8daaf6152771_e5627efa2ab1
"""

import sys
import hashlib
import argparse
from pathlib import Path

try:
    from scapy.all import rdpcap
    from collections import defaultdict
    # Import TLS layers - they're in a separate module
    from scapy.layers.tls.all import TLS, TLSClientHello, TLSExtension
except ImportError:
    try:
        # Alternative import path
        from scapy.layers.tls import TLS, TLSClientHello, TLSExtension
    except ImportError:
        print("ERROR: TLS layers not available")
        print("Install with: pip install scapy[basic]")
        print("Or use: pip install scapy tls")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    print("Install with: pip install scapy")
    sys.exit(1)


def extract_client_hello(pcap_file):
    """Extract TLS Client Hello packets from PCAP"""
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"Error reading PCAP: {e}")
        return []
    
    client_hellos = []
    
    for pkt in packets:
        if pkt.haslayer(TLS):
            if pkt.haslayer(TLSClientHello):
                client_hellos.append(pkt)
    
    return client_hellos


def calculate_ja4(client_hello_pkt):
    """
    Calculate JA4 fingerprint from Client Hello packet
    Based on JA4 specification
    """
    try:
        ch = client_hello_pkt[TLSClientHello]
        
        # Protocol version
        # t=TLS, q=QUIC, d=DTLS
        version_map = {
            0x0301: 't10',  # TLS 1.0
            0x0302: 't11',  # TLS 1.1
            0x0303: 't12',  # TLS 1.2
            0x0304: 't13'   # TLS 1.3
        }
        protocol = version_map.get(ch.version, 't13')
        
        # SNI (Server Name Indication)
        # i = IP address, d = domain name
        sni = 'd'  # Default to domain (most common)
        
        # Count cipher suites (max 99)
        cipher_count = len(ch.ciphers) if hasattr(ch, 'ciphers') else 0
        cipher_count_str = f"{min(cipher_count, 99):02d}"
        
        # Count extensions (max 99)
        ext_count = len(ch.ext) if hasattr(ch, 'ext') else 0
        ext_count_str = f"{min(ext_count, 99):02d}"
        
        # ALPN (Application-Layer Protocol Negotiation)
        alpn = "00"
        if hasattr(ch, 'ext'):
            for ext in ch.ext:
                if hasattr(ext, 'type') and ext.type == 16:  # ALPN extension
                    alpn = "h2"  # HTTP/2 detected
                    break
        
        # First part: Protocol + SNI + Counts + ALPN
        part1 = f"{protocol}{sni}{cipher_count_str}{ext_count_str}{alpn}"
        
        # Second part: Hash of cipher suites
        if hasattr(ch, 'ciphers') and ch.ciphers:
            cipher_string = ','.join(str(c) for c in sorted(ch.ciphers))
        else:
            cipher_string = ''
        cipher_hash = hashlib.sha256(cipher_string.encode()).hexdigest()[:12]
        
        # Third part: Hash of extensions
        if hasattr(ch, 'ext') and ch.ext:
            ext_string = ','.join(str(e.type) for e in sorted(ch.ext, key=lambda x: x.type if hasattr(x, 'type') else 0))
        else:
            ext_string = ''
        ext_hash = hashlib.sha256(ext_string.encode()).hexdigest()[:12]
        
        # Combine all parts
        ja4 = f"{part1}_{cipher_hash}_{ext_hash}"
        
        return ja4
        
    except Exception as e:
        print(f"Error calculating JA4: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Calculate JA4 fingerprints from PCAP files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ja4_calculator.py pcaps/langchain.pcap
  python3 ja4_calculator.py pcaps/*.pcap
        """
    )
    parser.add_argument('pcap_files', nargs='+', help='PCAP file(s) to analyze')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    all_signatures = defaultdict(lambda: {'count': 0, 'files': []})
    
    for pcap_file in args.pcap_files:
        pcap_path = Path(pcap_file)
        if not pcap_path.exists():
            print(f"WARNING: File not found: {pcap_file}", file=sys.stderr)
            continue
        
        if args.verbose:
            print(f"\nAnalyzing {pcap_file}...")
            print("-" * 60)
        
        client_hellos = extract_client_hello(str(pcap_path))
        
        if not client_hellos:
            if args.verbose:
                print(f"  No TLS Client Hello packets found")
            continue
        
        if args.verbose:
            print(f"  Found {len(client_hellos)} TLS Client Hello packet(s)")
        
        # Calculate JA4 for each
        for i, pkt in enumerate(client_hellos, 1):
            ja4 = calculate_ja4(pkt)
            if ja4:
                all_signatures[ja4]['count'] += 1
                if pcap_path.name not in all_signatures[ja4]['files']:
                    all_signatures[ja4]['files'].append(pcap_path.name)
                
                if args.verbose:
                    print(f"  Packet {i:2d}: {ja4}")
    
    # Print summary
    if not all_signatures:
        print("ERROR: No JA4 signatures found in any PCAP files")
        print("\nTroubleshooting:")
        print("1. Verify PCAP has HTTPS traffic: tcpdump -r file.pcap 'port 443'")
        print("2. Check for TLS handshakes: tshark -r file.pcap -Y 'tls.handshake.type == 1'")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"JA4 Signature Summary")
    print("=" * 60)
    
    for sig, data in sorted(all_signatures.items(), key=lambda x: -x[1]['count']):
        print(f"\nSignature: {sig}")
        print(f"  Occurrences: {data['count']}")
        print(f"  Files: {', '.join(data['files'])}")
    
    print("\n" + "=" * 60)
    print(f"Total unique signatures: {len(all_signatures)}")
    
    # If only one unique signature (expected for framework testing)
    if len(all_signatures) == 1:
        print("✓ Consistent signature (good for framework fingerprinting)")
        return 0
    else:
        print("⚠ Multiple signatures detected")
        print("  This might indicate:")
        print("  - Multiple TLS versions negotiated")
        print("  - Different cipher suite preferences")
        print("  - Connection to different servers")
        return 0


if __name__ == "__main__":
    sys.exit(main())

