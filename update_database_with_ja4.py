#!/usr/bin/env python3
"""
Update Database with Full JA4 Signatures
Reads from JSON file created by calculate_full_ja4.py
"""

import csv
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
SIGNATURES_DIR = BASE_DIR / "signatures"
DB_FILE = SIGNATURES_DIR / "signature_database.csv"

def find_latest_ja4_json():
    """Find the most recent JA4 JSON file"""
    json_files = sorted(SIGNATURES_DIR.glob("ja4_signatures_*.json"), reverse=True)
    if json_files:
        return json_files[0]
    return None

def update_database():
    """Update database with full JA4 signatures"""
    print("="*60)
    print("Updating Database with Full JA4 Signatures")
    print("="*60)
    
    # Find JA4 JSON file
    json_file = find_latest_ja4_json()
    
    if not json_file:
        print("[-] No JA4 signature JSON file found")
        print("    Run: python calculate_full_ja4.py first")
        return
    
    print(f"[+] Loading signatures from: {json_file.name}")
    
    # Load signatures
    with open(json_file, 'r', encoding='utf-8') as f:
        framework_signatures = json.load(f)
    
    print(f"    Found signatures for {len(framework_signatures)} framework(s)")
    
    # Read existing database
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
    
    # Update entries
    print("\n[+] Updating database entries...")
    updated = 0
    
    for framework_key, sig_data in framework_signatures.items():
        framework_name = name_map.get(framework_key, framework_key.title())
        
        # Find existing entry
        for entry in existing_entries:
            if entry.get('framework_name', '').lower() == framework_name.lower():
                # Update with full JA4 signature
                entry['ja4_signature'] = sig_data['signature']
                entry['verified_runs'] = sig_data['consistency']
                entry['test_date'] = datetime.now().strftime('%Y-%m-%d')
                
                notes = f"Full JA4 signature extracted. {sig_data['total']} handshake(s) captured. {sig_data['consistency']} consistent."
                if len(sig_data['all_signatures']) > 1:
                    notes += f" {len(sig_data['all_signatures'])} unique signatures found."
                entry['notes'] = notes
                
                updated += 1
                print(f"    [+] Updated: {framework_name} -> {sig_data['signature']}")
                break
    
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
    print(f"    Updated: {updated} entries")
    print(f"    Total entries: {len(existing_entries)}")

if __name__ == "__main__":
    update_database()

