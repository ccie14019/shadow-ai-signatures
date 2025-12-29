#!/usr/bin/env python3
"""
Calculate Full JA4 Signatures using Official Tool
Requires tshark to be installed
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
PCAPS_DIR = BASE_DIR / "pcaps"
SIGNATURES_DIR = BASE_DIR / "signatures"
JA4_TOOL = BASE_DIR / "scripts" / "ja4-official" / "python" / "ja4.py"

def check_tshark():
    """Check if tshark is available"""
    try:
        result = subprocess.run(
            ['tshark', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[+] tshark found: {version_line}")
            return True
    except FileNotFoundError:
        print("[-] tshark not found in PATH")
    except Exception as e:
        print(f"[-] Error checking tshark: {e}")
    
    # Check common Windows locations
    common_paths = [
        r"C:\Program Files\Wireshark\tshark.exe",
        r"C:\Program Files (x86)\Wireshark\tshark.exe",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            print(f"[+] Found tshark at: {path}")
            print("[!] Add to PATH or use full path")
            return path
    
    return False

def calculate_ja4_for_pcap(pcap_file):
    """Calculate JA4 using official tool"""
    if not JA4_TOOL.exists():
        print(f"[-] JA4 tool not found: {JA4_TOOL}")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, str(JA4_TOOL), str(pcap_file), '--ja4', '-J'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse JSON output
            signatures = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if 'JA4' in data or 'JA4.1' in data:
                            ja4 = data.get('JA4') or data.get('JA4.1')
                            if ja4:
                                signatures.append({
                                    'ja4': ja4,
                                    'src': data.get('src', ''),
                                    'dst': data.get('dst', ''),
                                    'domain': data.get('domain', ''),
                                    'stream': data.get('stream', '')
                                })
                    except json.JSONDecodeError:
                        continue
            
            return signatures
        else:
            print(f"  [-] Error: {result.stderr[:200]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"  [-] Timeout calculating JA4")
        return None
    except Exception as e:
        print(f"  [-] Error: {e}")
        return None

def main():
    """Main function"""
    print("="*60)
    print("Calculate Full JA4 Signatures")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check tshark
    print("[1/4] Checking for tshark...")
    tshark_path = check_tshark()
    
    if not tshark_path:
        print("\n[-] tshark not found!")
        print("\nTo install Wireshark:")
        print("1. Download: https://www.wireshark.org/download.html")
        print("2. Install Wireshark (includes tshark)")
        print("3. Add to PATH: C:\\Program Files\\Wireshark\\")
        print("4. Or run this script again after installation")
        return
    
    # Find PCAP files
    print("\n[2/4] Finding PCAP files...")
    pcap_files = sorted([p for p in PCAPS_DIR.glob("*_20251228_*.pcap") if p.stat().st_size > 1000])
    
    if not pcap_files:
        print("[-] No valid PCAP files found")
        return
    
    print(f"    Found {len(pcap_files)} PCAP file(s)")
    
    # Group by framework
    framework_pcaps = defaultdict(list)
    for pcap_file in pcap_files:
        framework = pcap_file.stem.split('_')[0]
        framework_pcaps[framework].append(pcap_file)
    
    print(f"    Frameworks: {len(framework_pcaps)}")
    
    # Calculate JA4 for each framework
    print("\n[3/4] Calculating JA4 signatures...")
    framework_signatures = {}
    
    for framework, pcap_list in sorted(framework_pcaps.items()):
        print(f"\n  Processing {framework}...")
        all_sigs = []
        
        for pcap_file in pcap_list:
            print(f"    Analyzing {pcap_file.name}...", end=' ', flush=True)
            sigs = calculate_ja4_for_pcap(pcap_file)
            
            if sigs:
                all_sigs.extend(sigs)
                print(f"[+] Found {len(sigs)} signature(s)")
            else:
                print("[-] No signatures")
        
        if all_sigs:
            # Get most common JA4
            sig_counts = defaultdict(int)
            for sig_info in all_sigs:
                ja4 = sig_info['ja4']
                sig_counts[ja4] += 1
            
            most_common = max(sig_counts.items(), key=lambda x: x[1])
            framework_signatures[framework] = {
                'signature': most_common[0],
                'count': most_common[1],
                'total': len(all_sigs),
                'consistency': f"{most_common[1]}/{len(all_sigs)}",
                'all_signatures': list(sig_counts.keys())
            }
            print(f"    Most common: {most_common[0]} ({most_common[1]}/{len(all_sigs)})")
    
    # Save results
    print("\n[4/4] Saving results...")
    
    if framework_signatures:
        # Save to JSON
        json_file = SIGNATURES_DIR / f"ja4_signatures_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(framework_signatures, f, indent=2)
        print(f"    [+] Saved to: {json_file}")
        
        # Update database
        print("\n" + "="*60)
        print("JA4 Signature Results")
        print("="*60)
        
        for framework, sig_data in sorted(framework_signatures.items()):
            print(f"\n{framework.title()}:")
            print(f"  Signature: {sig_data['signature']}")
            print(f"  Consistency: {sig_data['consistency']}")
            print(f"  Total handshakes: {sig_data['total']}")
            if len(sig_data['all_signatures']) > 1:
                print(f"  Other signatures: {len(sig_data['all_signatures']) - 1}")
        
        print("\n" + "="*60)
        print("Next: Update database with these signatures")
        print(f"  Run: python update_database_with_ja4.py")
        print("="*60)
    else:
        print("[-] No signatures calculated")

if __name__ == "__main__":
    main()
