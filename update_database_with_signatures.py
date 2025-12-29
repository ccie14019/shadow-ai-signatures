#!/usr/bin/env python3
"""
Update signature database with extracted signatures
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
SIGNATURES_DIR = BASE_DIR / "signatures"
PCAPS_DIR = BASE_DIR / "pcaps"
DB_FILE = SIGNATURES_DIR / "signature_database.csv"

def extract_signatures_from_pcaps():
    """Extract signatures from PCAP files"""
    from extract_ja4_from_pcaps import calculate_simple_ja4
    
    pcap_files = sorted(PCAPS_DIR.glob("*_20251228_*.pcap"))
    framework_signatures = defaultdict(list)
    
    for pcap_file in pcap_files:
        if pcap_file.stat().st_size < 1000:
            continue
        
        framework = pcap_file.stem.split('_')[0]
        signatures = calculate_simple_ja4(pcap_file)
        
        if signatures:
            framework_signatures[framework].extend(signatures)
    
    # Get most common signature for each framework
    results = {}
    for framework, sigs in framework_signatures.items():
        sig_counts = defaultdict(int)
        for sig_info in sigs:
            sig_counts[sig_info['signature']] += 1
        
        if sig_counts:
            most_common = max(sig_counts.items(), key=lambda x: x[1])
            results[framework] = {
                'signature': most_common[0],
                'count': most_common[1],
                'total': len(sigs),
                'consistency': f"{most_common[1]}/{len(sigs)}"
            }
    
    return results

def update_database():
    """Update signature database"""
    print("="*60)
    print("Updating Signature Database")
    print("="*60)
    
    # Extract signatures
    print("\n[1/2] Extracting signatures from PCAPs...")
    signatures = extract_signatures_from_pcaps()
    
    if not signatures:
        print("[-] No signatures found in PCAPs")
        return
    
    print(f"    Found signatures for {len(signatures)} framework(s)")
    
    # Read existing database
    existing_entries = []
    if DB_FILE.exists():
        with open(DB_FILE, 'r', encoding='utf-8') as sys.stdin:
            reader = csv.DictReader(sys.stdin)
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
    print("\n[2/2] Updating database...")
    updated = 0
    added = 0
    
    for framework_key, sig_data in signatures.items():
        framework_name = name_map.get(framework_key, framework_key.title())
        
        # Find or create entry
        found = False
        for entry in existing_entries:
            if entry.get('framework_name', '').lower() == framework_name.lower():
                entry['ja4_signature'] = sig_data['signature']
                entry['verified_runs'] = sig_data['consistency']
                entry['test_date'] = datetime.now().strftime('%Y-%m-%d')
                entry['notes'] = f"Extracted from PCAP. {sig_data['total']} handshake(s) captured. {sig_data['consistency']} consistent."
                found = True
                updated += 1
                print(f"    [+] Updated: {framework_name}")
                break
        
        if not found:
            new_entry = {
                'framework_name': framework_name,
                'version': 'TBD',
                'language': 'Python',
                'http_library': 'TBD',
                'tls_version': '1.3',
                'ja4_signature': sig_data['signature'],
                'test_date': datetime.now().strftime('%Y-%m-%d'),
                'verified_runs': sig_data['consistency'],
                'detection_rate': 'TBD',
                'false_positive_rate': 'TBD',
                'notes': f"Extracted from PCAP. {sig_data['total']} handshake(s) captured."
            }
            existing_entries.append(new_entry)
            added += 1
            print(f"    [+] Added: {framework_name}")
    
    # Write back
    fieldnames = [
        'framework_name', 'version', 'language', 'http_library', 'tls_version',
        'ja4_signature', 'test_date', 'verified_runs', 'detection_rate',
        'false_positive_rate', 'notes'
    ]
    
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_entries)
    
    print(f"\n[+] Database updated!")
    print(f"    Total entries: {len(existing_entries)}")
    print(f"    Updated: {updated}")
    print(f"    Added: {added}")

if __name__ == "__main__":
    update_database()

