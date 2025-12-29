#!/usr/bin/env python3
"""
Signature Validation Script
Tests signature consistency and generates validation reports
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent
SIGNATURES_DIR = BASE_DIR / "signatures"
PCAPS_DIR = BASE_DIR / "pcaps"
LOGS_DIR = BASE_DIR / "logs"

def load_signature_database():
    """Load signature database from CSV"""
    db_file = SIGNATURES_DIR / "signature_database.csv"
    
    if not db_file.exists():
        return []
    
    signatures = []
    with open(db_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            signatures.append(row)
    
    return signatures

def analyze_signature_consistency(signatures):
    """Analyze signature consistency across frameworks"""
    results = {
        'total_frameworks': len(signatures),
        'unique_signatures': len(set(s['ja4_signature'] for s in signatures)),
        'shared_signatures': defaultdict(list),
        'verification_status': defaultdict(int)
    }
    
    # Find shared signatures (same JA4 across frameworks)
    sig_to_frameworks = defaultdict(list)
    for sig in signatures:
        ja4 = sig.get('ja4_signature', '')
        if ja4:
            sig_to_frameworks[ja4].append(sig.get('framework_name', 'Unknown'))
    
    for ja4, frameworks in sig_to_frameworks.items():
        if len(frameworks) > 1:
            results['shared_signatures'][ja4] = frameworks
    
    # Count verification status
    for sig in signatures:
        verified = sig.get('verified_runs', '0/0')
        if verified == '3/3':
            results['verification_status']['fully_verified'] += 1
        elif verified.startswith('2'):
            results['verification_status']['partially_verified'] += 1
        elif verified.startswith('1'):
            results['verification_status']['minimal_verification'] += 1
        else:
            results['verification_status']['unverified'] += 1
    
    return results

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("="*60)
    print("Shadow AI Signature Validation Report")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    signatures = load_signature_database()
    
    if not signatures:
        print("No signatures found in database.")
        print("Run tests to generate signatures first.")
        return
    
    print(f"Total Frameworks Tested: {len(signatures)}")
    print()
    
    # Analyze consistency
    analysis = analyze_signature_consistency(signatures)
    
    print("Signature Statistics:")
    print(f"  Unique JA4 Signatures: {analysis['unique_signatures']}")
    print(f"  Shared Signatures: {len(analysis['shared_signatures'])}")
    print()
    
    # Verification status
    print("Verification Status:")
    for status, count in analysis['verification_status'].items():
        print(f"  {status.replace('_', ' ').title()}: {count}")
    print()
    
    # Shared signatures warning
    if analysis['shared_signatures']:
        print("[!] WARNING: Shared Signatures Detected")
        print("  The following JA4 signatures appear in multiple frameworks:")
        print()
        for ja4, frameworks in analysis['shared_signatures'].items():
            print(f"  {ja4[:20]}...")
            print(f"    Used by: {', '.join(frameworks)}")
            print()
        print("  Note: This may indicate:")
        print("    - Same underlying HTTP library")
        print("    - Framework wrappers around same SDK")
        print("    - Need for additional fingerprinting")
        print()
    
    # Framework details
    print("Framework Details:")
    print("-" * 60)
    for sig in signatures:
        framework = sig.get('framework_name', 'Unknown')
        version = sig.get('version', 'N/A')
        ja4 = sig.get('ja4_signature', 'N/A')
        verified = sig.get('verified_runs', '0/0')
        detection = sig.get('detection_rate', 'N/A')
        
        status_icon = "[+]" if verified == "3/3" else "[!]" if verified.startswith("2") else "[-]"
        
        print(f"{status_icon} {framework} v{version}")
        print(f"   Signature: {ja4[:40]}..." if len(ja4) > 40 else f"   Signature: {ja4}")
        print(f"   Verified: {verified} | Detection: {detection}")
        print()
    
    # Recommendations
    print("="*60)
    print("Recommendations:")
    print("="*60)
    
    unverified = analysis['verification_status'].get('unverified', 0)
    if unverified > 0:
        print(f"[!] {unverified} framework(s) need verification runs")
        print("  Run each test 3 times to verify signature consistency")
        print()
    
    if analysis['shared_signatures']:
        print("[!] Some frameworks share signatures")
        print("  Consider additional fingerprinting methods:")
        print("    - HTTP/2 SETTINGS frame analysis")
        print("    - TLS extension ordering")
        print("    - User-Agent strings (if available)")
        print()
    
    fully_verified = analysis['verification_status'].get('fully_verified', 0)
    if fully_verified == len(signatures):
        print("[+] All signatures fully verified (3/3 runs)")
        print("  Ready for production deployment")
    else:
        print(f"[!] Only {fully_verified}/{len(signatures)} signatures fully verified")
        print("  Complete verification before production use")
    
    print()
    print("="*60)

def check_pcap_files():
    """Check for PCAP files and their status"""
    print("\nPCAP File Status:")
    print("-" * 60)
    
    if not PCAPS_DIR.exists():
        print("  No pcaps directory found")
        return
    
    pcap_files = list(PCAPS_DIR.glob("*.pcap"))
    
    if not pcap_files:
        print("  No PCAP files found")
        print("  Run tests to generate PCAP files")
        return
    
    print(f"  Found {len(pcap_files)} PCAP file(s)")
    
    for pcap in sorted(pcap_files):
        size = pcap.stat().st_size
        size_str = f"{size:,} bytes"
        if size == 0:
            size_str += " (empty - mock mode)"
        
        mtime = datetime.fromtimestamp(pcap.stat().st_mtime)
        print(f"    {pcap.name}")
        print(f"      Size: {size_str}")
        print(f"      Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main validation function"""
    generate_validation_report()
    check_pcap_files()
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Run framework tests: python3 test_runner.py")
    print("2. Calculate JA4 signatures from PCAPs")
    print("3. Update signature_database.csv with results")
    print("4. Re-run validation: python3 validate_signatures.py")
    print("="*60)

if __name__ == "__main__":
    main()

