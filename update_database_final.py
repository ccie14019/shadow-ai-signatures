#!/usr/bin/env python3
"""
Update Signature Database with Extracted Signatures
Fixes the issue where signatures are extracted but not saved
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
SIGNATURES_DIR = BASE_DIR / "signatures"
PCAPS_DIR = BASE_DIR / "pcaps"
DB_FILE = SIGNATURES_DIR / "signature_database.csv"

def extract_signatures_from_pcaps():
    """Extract signatures from PCAP files using simplified method"""
    try:
        from scapy.all import rdpcap, TCP, Raw, IP
        import hashlib
    except ImportError:
        print("ERROR: scapy not installed")
        return {}
    
    pcap_files = sorted([p for p in PCAPS_DIR.glob("*_20251228_*.pcap") if p.stat().st_size > 1000])
    framework_signatures = defaultdict(list)
    
    for pcap_file in pcap_files:
        framework = pcap_file.stem.split('_')[0]
        
        try:
            packets = rdpcap(str(pcap_file))
            
            seen_connections = set()
            for pkt in packets:
                if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
                    continue
                
                ip = pkt[IP]
                tcp = pkt[TCP]
                
                if tcp.dport != 443 and tcp.sport != 443:
                    continue
                
                conn_id = tuple(sorted([
                    (ip.src, tcp.sport),
                    (ip.dst, tcp.dport)
                ]))
                
                if conn_id in seen_connections:
                    continue
                
                if pkt.haslayer(Raw):
                    raw_data = bytes(pkt[Raw])
                    if len(raw_data) > 5 and raw_data[0] == 0x16:  # TLS Handshake
                        version = (raw_data[1] << 8) | raw_data[2]
                        if len(raw_data) > 5 and raw_data[5] == 0x01:  # Client Hello
                            seen_connections.add(conn_id)
                            
                            version_map = {
                                0x0301: 't10', 0x0302: 't11',
                                0x0303: 't12', 0x0304: 't13'
                            }
                            version_str = version_map.get(version, 't13')
                            data_hash = hashlib.sha256(raw_data[:100]).hexdigest()[:12]
                            sig = f"{version_str}_simplified_{data_hash}"
                            
                            framework_signatures[framework].append(sig)
        except Exception as e:
            print(f"  Error processing {pcap_file.name}: {e}")
            continue
    
    # Get most common signature for each framework
    results = {}
    for framework, sigs in framework_signatures.items():
        if sigs:
            sig_counts = defaultdict(int)
            for sig in sigs:
                sig_counts[sig] += 1
            most_common = max(sig_counts.items(), key=lambda x: x[1])
            results[framework] = {
                'signature': most_common[0],
                'count': most_common[1],
                'total': len(sigs),
                'consistency': f"{most_common[1]}/{len(sigs)}"
            }
    
    return results

def update_database():
    """Update signature database with extracted signatures"""
    print("="*60)
    print("Updating Signature Database with Extracted Signatures")
    print("="*60)
    
    # Extract signatures
    print("\n[1/2] Extracting signatures from PCAPs...")
    signatures = extract_signatures_from_pcaps()
    
    if not signatures:
        print("[-] No signatures found in PCAPs")
        print("    Run: python extract_ja4_from_pcaps.py")
        return
    
    print(f"    Found signatures for {len(signatures)} framework(s)")
    for fw, sig_data in signatures.items():
        print(f"      {fw}: {sig_data['signature']} ({sig_data['consistency']})")
    
    # Read existing database
    print("\n[2/2] Updating database...")
    existing_entries = []
    if DB_FILE.exists():
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_entries = list(reader)
    
    # Framework name mapping
    name_map = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'langchain': 'LangChain',
        'google_gemini': 'Google Gemini',
        'cohere': 'Cohere',
        'mistral': 'Mistral AI',
        'together': 'Together AI',
        'llamaindex': 'LlamaIndex',
        'crewai': 'CrewAI',
        'ollama': 'Ollama'
    }
    
    # Update entries
    updated = 0
    added = 0
    
    for framework_key, sig_data in signatures.items():
        framework_name = name_map.get(framework_key, framework_key.title())
        
        # Find existing entry
        found = False
        for entry in existing_entries:
            if entry.get('framework_name', '').lower() == framework_name.lower():
                # Update with extracted simplified signature without overwriting full JA4
                # Only fill ja4_signature if it is currently empty (no full JA4 recorded)
                if not entry.get('ja4_signature'):
                    entry['ja4_signature'] = sig_data['signature']
                # Always record the simplified signature separately
                entry['simplified_ja4'] = sig_data['signature']
                entry['verified_runs'] = sig_data['consistency']
                entry['test_date'] = datetime.now().strftime('%Y-%m-%d')
                entry['notes'] = f"Extracted from PCAP. {sig_data['total']} handshake(s) captured. {sig_data['consistency']} consistent. Note: Simplified signature (not full JA4 spec)."
                found = True
                updated += 1
                print(f"    [+] Updated: {framework_name}")
                break
        
        if not found:
            # Add new entry
            new_entry = {
                'framework_name': framework_name,
                'version': 'TBD',
                'language': 'Python',
                'http_library': 'TBD',
                'tls_version': '1.3',
                'ja4_signature': sig_data['signature'],
                'simplified_ja4': sig_data['signature'],
                'test_date': datetime.now().strftime('%Y-%m-%d'),
                'verified_runs': sig_data['consistency'],
                'detection_rate': 'TBD',
                'false_positive_rate': 'TBD',
                'notes': f"Extracted from PCAP. {sig_data['total']} handshake(s). Simplified signature."
            }
            existing_entries.append(new_entry)
            added += 1
            print(f"    [+] Added: {framework_name}")
    
    # Write back
    fieldnames = [
        'framework_name', 'version', 'language', 'http_library', 'tls_version',
        'ja4_signature', 'simplified_ja4', 'test_date', 'verified_runs', 'detection_rate',
        'false_positive_rate', 'notes'
    ]
    
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_entries)
    
    print(f"\n[+] Database updated successfully!")
    print(f"    Total entries: {len(existing_entries)}")
    print(f"    Updated: {updated}")
    print(f"    Added: {added}")
    print(f"\n    Database file: {DB_FILE}")

if __name__ == "__main__":
    update_database()

