#!/usr/bin/env python3
"""
Calculate Improved JA4 for All PCAP Files
Updates database with better signatures
"""

import sys
from pathlib import Path
from collections import defaultdict
import csv
from datetime import datetime

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
SIGNATURES_DIR = BASE_DIR / "signatures"
DB_FILE = SIGNATURES_DIR / "signature_database.csv"

# Import improved calculator
sys.path.insert(0, str(BASE_DIR / "scripts"))
from ja4_improved import extract_ja4_from_pcap

def process_all_pcaps():
    """Process all PCAP files and extract signatures"""
    pcap_files = sorted([p for p in PCAPS_DIR.glob("*_20251228_*.pcap") if p.stat().st_size > 1000])
    
    framework_signatures = defaultdict(list)
    
    print("="*60)
    print("Processing All PCAP Files with Improved JA4 Calculator")
    print("="*60)
    print(f"\nFound {len(pcap_files)} PCAP file(s) to process\n")
    
    for pcap_file in pcap_files:
        framework = pcap_file.stem.split('_')[0]
        print(f"Processing: {pcap_file.name}")
        
        signatures = extract_ja4_from_pcap(pcap_file)
        
        if signatures:
            framework_signatures[framework].extend(signatures)
            print(f"  [+] Found {len(signatures)} signature(s)")
        else:
            print(f"  [-] No signatures found")
        print()
    
    # Analyze consistency
    print("="*60)
    print("Signature Analysis")
    print("="*60)
    
    results = {}
    
    for framework, sigs in framework_signatures.items():
        sig_counts = defaultdict(int)
        for sig_info in sigs:
            sig_counts[sig_info['signature']] += 1
        
        if sig_counts:
            # Get most common signature
            most_common = max(sig_counts.items(), key=lambda x: x[1])
            total = len(sigs)
            consistent = most_common[1]
            
            results[framework] = {
                'signature': most_common[0],
                'count': consistent,
                'total': total,
                'consistency': f"{consistent}/{total}",
                'unique': len(sig_counts),
                'all_signatures': list(sig_counts.keys())
            }
            
            print(f"\n{framework.title()}:")
            print(f"  Total handshakes: {total}")
            print(f"  Unique signatures: {len(sig_counts)}")
            print(f"  Most common: {most_common[0]} ({consistent}/{total})")
            
            if len(sig_counts) == 1:
                print(f"  [+] Fully consistent!")
            elif consistent / total >= 0.67:
                print(f"  [+] Mostly consistent ({consistent}/{total})")
            else:
                print(f"  [!] Low consistency - multiple signatures")
                for sig, count in sorted(sig_counts.items(), key=lambda x: -x[1])[:3]:
                    print(f"      {sig}: {count} occurrence(s)")
    
    return results

def update_database(results):
    """Update database with improved signatures"""
    print("\n" + "="*60)
    print("Updating Database")
    print("="*60)
    
    # Read existing
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
        'google': 'Google Gemini',
        'cohere': 'Cohere',
        'mistral': 'Mistral AI',
        'together': 'Together AI',
        'llamaindex': 'LlamaIndex',
        'crewai': 'CrewAI',
        'ollama': 'Ollama'
    }
    
    updated = 0
    added = 0
    
    for framework_key, sig_data in results.items():
        framework_name = name_map.get(framework_key, framework_key.title())
        
        # Find existing entry
        found = False
        for entry in existing_entries:
            if entry.get('framework_name', '').lower() == framework_name.lower():
                entry['ja4_signature'] = sig_data['signature']
                entry['verified_runs'] = sig_data['consistency']
                entry['test_date'] = datetime.now().strftime('%Y-%m-%d')
                
                if sig_data['unique'] == 1:
                    consistency_note = "Fully consistent signature"
                elif sig_data['count'] / sig_data['total'] >= 0.67:
                    consistency_note = f"Mostly consistent ({sig_data['consistency']})"
                else:
                    consistency_note = f"Multiple signatures found ({sig_data['unique']} unique)"
                
                entry['notes'] = f"Improved JA4 extraction. {sig_data['total']} handshake(s). {consistency_note}. Note: Improved parsing (not full JA4 spec, but better than simplified)."
                found = True
                updated += 1
                print(f"  [+] Updated: {framework_name}")
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
                'notes': f"Improved JA4 extraction. {sig_data['total']} handshake(s)."
            }
            existing_entries.append(new_entry)
            added += 1
            print(f"  [+] Added: {framework_name}")
    
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

def main():
    """Main function"""
    results = process_all_pcaps()
    
    if results:
        update_database(results)
        print("\n" + "="*60)
        print("Next Steps:")
        print("="*60)
        print("1. Review signatures in database")
        print("2. For full JA4, install Wireshark and use official tool")
        print("3. Or continue with improved signatures")
        print("="*60)
    else:
        print("\n[-] No signatures found in PCAPs")

if __name__ == "__main__":
    main()

