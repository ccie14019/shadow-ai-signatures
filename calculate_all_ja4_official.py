#!/usr/bin/env python3
"""
Calculate Full JA4 Signatures Using Official Tool
Requires Wireshark/tshark to be installed
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import csv

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
SIGNATURES_DIR = BASE_DIR / "signatures"
DB_FILE = SIGNATURES_DIR / "signature_database.csv"
JA4_SCRIPT = BASE_DIR / "scripts" / "ja4-official" / "python" / "ja4.py"

def get_tshark_path():
    """Get tshark executable path"""
    import platform
    import os
    
    # Try PATH first
    try:
        result = subprocess.run(
            ["tshark", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return "tshark"  # Use from PATH
    except FileNotFoundError:
        pass
    except Exception:
        pass
    
    # Try common installation paths
    if platform.system() == "Windows":
        possible_paths = [
            Path("C:/Program Files/Wireshark/tshark.exe"),
            Path("C:/Program Files (x86)/Wireshark/tshark.exe"),
        ]
        
        for tshark_path in possible_paths:
            if tshark_path.exists():
                # Add to PATH for this session
                os.environ["PATH"] = str(tshark_path.parent) + os.pathsep + os.environ.get("PATH", "")
                return str(tshark_path)
    
    return None

def check_tshark():
    """Verify tshark is available"""
    tshark_cmd = get_tshark_path()
    
    if not tshark_cmd:
        print("[-] ERROR: tshark not found")
        print("    Install Wireshark and add to PATH")
        print("    Or run: powershell -File add_wireshark_to_path.ps1")
        return False
    
    try:
        result = subprocess.run(
            [tshark_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"[+] {version}")
            return True
    except Exception as e:
        print(f"[-] Error checking tshark: {e}")
        return False
    
    return False

def calculate_ja4_from_pcap(pcap_file):
    """Calculate JA4 signature from PCAP using official tool"""
    try:
        result = subprocess.run(
            [sys.executable, str(JA4_SCRIPT), str(pcap_file), "--ja4", "-J"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            signatures = []
            
            # Parse JSON output (can be multiple JSON objects, one per line)
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    # Extract JA4.1 (standard JA4 signature)
                    if 'JA4.1' in data:
                        signatures.append(data['JA4.1'])
                    elif 'JA4' in data:
                        signatures.append(data['JA4'])
                except json.JSONDecodeError:
                    # Try to extract from text format
                    if 'JA4.1' in line or 'JA4' in line:
                        # Look for pattern like 'JA4.1': 't00d1812h1_...'
                        import re
                        match = re.search(r"['\"]JA4\.?1?['\"]:\s*['\"]([^'\"]+)['\"]", line)
                        if match:
                            signatures.append(match.group(1))
                        else:
                            # Try simple pattern
                            match = re.search(r"(t\d+[id]\d+\w+_\w+_\w+)", line)
                            if match:
                                signatures.append(match.group(1))
            
            return {'signatures': signatures} if signatures else None
        else:
            if result.stderr:
                # Some errors are expected (no TLS in some PCAPs)
                if "No such file" not in result.stderr:
                    print(f"      [!] {result.stderr[:100]}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  [!] Timeout processing {pcap_file.name}")
        return None
    except Exception as e:
        print(f"  [!] Error: {e}")
        return None

def process_all_pcaps():
    """Process all PCAP files and extract full JA4 signatures"""
    print("="*60)
    print("Calculating Full JA4 Signatures (Official Tool)")
    print("="*60)
    
    # Check tshark
    print("\n[1/4] Checking tshark...")
    if not check_tshark():
        return None
    
    # Check JA4 script
    print("\n[2/4] Checking JA4 tool...")
    if not JA4_SCRIPT.exists():
        print(f"[-] JA4 tool not found: {JA4_SCRIPT}")
        print("    Make sure scripts/ja4-official is cloned")
        return None
    print(f"[+] JA4 tool found: {JA4_SCRIPT}")
    
    # Find PCAP files
    print("\n[3/4] Finding PCAP files...")
    pcap_files = sorted([p for p in PCAPS_DIR.glob("*.pcap") if p.stat().st_size > 1000])
    print(f"    Found {len(pcap_files)} PCAP file(s)")
    
    if not pcap_files:
        print("[-] No PCAP files found")
        return None
    
    # Process each PCAP
    print("\n[4/4] Processing PCAP files...")
    framework_signatures = defaultdict(list)
    
    for i, pcap_file in enumerate(pcap_files, 1):
        framework = pcap_file.stem.split('_')[0]
        print(f"\n  [{i}/{len(pcap_files)}] {pcap_file.name}")
        
        result = calculate_ja4_from_pcap(pcap_file)
        
        if result:
            if isinstance(result, dict):
                if 'signatures' in result:
                    for sig in result['signatures']:
                        framework_signatures[framework].append(sig)
                elif 'ja4' in result:
                    framework_signatures[framework].append(result['ja4'])
                else:
                    # Try to find JA4 in the data
                    for key, value in result.items():
                        if 'ja4' in key.lower() and value:
                            framework_signatures[framework].append(str(value))
            print(f"      [+] Found signature(s)")
        else:
            print(f"      [-] No signature found")
    
    # Analyze results
    print("\n" + "="*60)
    print("Signature Analysis")
    print("="*60)
    
    results = {}
    
    for framework, sigs in framework_signatures.items():
        if not sigs:
            continue
        
        sig_counts = defaultdict(int)
        for sig in sigs:
            sig_counts[sig] += 1
        
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
            print(f"  [+] Mostly consistent")
        else:
            print(f"  [!] Multiple signatures")
    
    return results

def update_database(results):
    """Update database with full JA4 signatures"""
    print("\n" + "="*60)
    print("Updating Database with Full JA4 Signatures")
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
        'ollama': 'Ollama',
        'ai21': 'Ai21',
        'haystack': 'Haystack',
        'transformers': 'Transformers',
        'autogen': 'AutoGen',
        'perplexity': 'Perplexity AI',
        'replicate': 'Replicate'
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
                    consistency_note = f"Multiple signatures ({sig_data['unique']} unique)"
                
                entry['notes'] = f"Full JA4 signature (official tool). {sig_data['total']} handshake(s). {consistency_note}."
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
                'notes': f"Full JA4 signature (official tool). {sig_data['total']} handshake(s)."
            }
            existing_entries.append(new_entry)
            added += 1
            print(f"  [+] Added: {framework_name}")
    
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
        print("[+] Complete!")
        print("="*60)
        print("Full JA4 signatures calculated and saved to database.")
        print(f"Database: {DB_FILE}")
    else:
        print("\n[-] No signatures calculated")
        print("    Check that:")
        print("    1. Wireshark/tshark is installed and in PATH")
        print("    2. PCAP files exist in pcaps/ directory")
        print("    3. JA4 tool is available at scripts/ja4-official/python/ja4.py")

if __name__ == "__main__":
    main()

