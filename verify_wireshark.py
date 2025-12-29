#!/usr/bin/env python3
"""
Verify Wireshark/tshark Installation
"""

import subprocess
import sys
from pathlib import Path

def check_tshark():
    """Check if tshark is installed and accessible"""
    print("="*60)
    print("Verifying Wireshark/tshark Installation")
    print("="*60)
    print()
    
    # Check common installation paths
    possible_paths = [
        Path("C:/Program Files/Wireshark/tshark.exe"),
        Path("C:/Program Files (x86)/Wireshark/tshark.exe"),
    ]
    
    tshark_path = None
    for path in possible_paths:
        if path.exists():
            tshark_path = path
            print(f"[+] Found tshark at: {path}")
            break
    
    # Try to run tshark
    try:
        result = subprocess.run(
            ["tshark", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[+] tshark is accessible!")
            print(f"    {version_line}")
            print()
            
            # Check version
            if "TShark" in version_line:
                print("[+] Installation verified successfully!")
                print()
                print("You can now use the official JA4 tool:")
                print("  python scripts/ja4-official/python/ja4.py <pcap_file> --ja4")
                return True
        else:
            print(f"[-] tshark returned error code: {result.returncode}")
            print(f"    {result.stderr}")
            return False
    
    except FileNotFoundError:
        print("[-] tshark not found in PATH")
        if tshark_path:
            print(f"[!] Found at: {tshark_path}")
            print(f"    Add to PATH: {tshark_path.parent}")
        else:
            print("[!] Wireshark not installed or not in PATH")
            print()
            print("Installation steps:")
            print("1. Download from: https://www.wireshark.org/download.html")
            print("2. Install (make sure 'Install TShark' is checked)")
            print("3. Add to PATH: C:\\Program Files\\Wireshark")
        return False
    
    except subprocess.TimeoutExpired:
        print("[-] tshark command timed out")
        return False
    except Exception as e:
        print(f"[-] Error checking tshark: {e}")
        return False

def test_ja4_tool():
    """Test if JA4 tool can use tshark"""
    print("\n" + "="*60)
    print("Testing JA4 Tool Integration")
    print("="*60)
    print()
    
    ja4_script = Path(__file__).parent / "scripts" / "ja4-official" / "python" / "ja4.py"
    
    if not ja4_script.exists():
        print("[-] JA4 tool not found at expected location")
        print(f"    Expected: {ja4_script}")
        return False
    
    print(f"[+] JA4 tool found: {ja4_script}")
    
    # Check if we have any PCAP files to test
    pcaps_dir = Path(__file__).parent / "pcaps"
    pcap_files = list(pcaps_dir.glob("*.pcap"))
    
    if not pcap_files:
        print("[!] No PCAP files found to test")
        print("    Run some framework tests first to generate PCAPs")
        return False
    
    # Try with a small PCAP
    test_pcap = None
    for pcap in pcap_files:
        if pcap.stat().st_size > 1000:  # At least 1KB
            test_pcap = pcap
            break
    
    if not test_pcap:
        print("[!] No suitable PCAP files found (all too small)")
        return False
    
    print(f"[+] Testing with: {test_pcap.name}")
    print(f"    Size: {test_pcap.stat().st_size} bytes")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(ja4_script), str(test_pcap), "--ja4", "-J"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[+] JA4 tool works!")
            print()
            print("Sample output:")
            output_lines = result.stdout.split('\n')[:10]
            for line in output_lines:
                if line.strip():
                    print(f"    {line}")
            return True
        else:
            print(f"[-] JA4 tool returned error: {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr[:500])
            return False
    
    except subprocess.TimeoutExpired:
        print("[-] JA4 tool timed out")
        return False
    except Exception as e:
        print(f"[-] Error running JA4 tool: {e}")
        return False

if __name__ == "__main__":
    tshark_ok = check_tshark()
    
    if tshark_ok:
        test_ja4_tool()
    
    print("\n" + "="*60)
    if tshark_ok:
        print("[+] Wireshark is ready to use!")
        print("\nNext steps:")
        print("1. Calculate full JA4 signatures:")
        print("   python calculate_all_ja4_official.py")
        print("2. Or use directly:")
        print("   python scripts/ja4-official/python/ja4.py pcaps/*.pcap --ja4 -J")
    else:
        print("[-] Wireshark not installed or not accessible")
        print("\nInstallation:")
        print("1. Download: https://www.wireshark.org/download.html")
        print("2. Install (check 'Install TShark')")
        print("3. Add to PATH: C:\\Program Files\\Wireshark")
        print("4. Run this script again to verify")
    print("="*60)

