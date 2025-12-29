#!/usr/bin/env python3
"""
Test All Available Frameworks
Automatically detects and tests all installed frameworks
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
TESTS_DIR = BASE_DIR / "tests"

# Framework configurations
FRAMEWORKS = [
    {
        'name': 'openai',
        'test_script': 'openai_test.py',
        'install': 'pip install openai',
        'check_import': 'openai'
    },
    {
        'name': 'anthropic',
        'test_script': 'anthropic_test.py',
        'install': 'pip install anthropic',
        'check_import': 'anthropic'
    },
    {
        'name': 'langchain',
        'test_script': 'langchain_test.py',
        'install': 'pip install langchain langchain-openai',
        'check_import': 'langchain'
    },
    {
        'name': 'google_gemini',
        'test_script': 'google_gemini_test.py',
        'install': 'pip install google-generativeai',
        'check_import': 'google.generativeai'
    },
    {
        'name': 'cohere',
        'test_script': 'cohere_test.py',
        'install': 'pip install cohere',
        'check_import': 'cohere'
    },
    {
        'name': 'mistral',
        'test_script': 'mistral_test.py',
        'install': 'pip install mistralai',
        'check_import': 'mistralai'
    },
    {
        'name': 'together',
        'test_script': 'together_test.py',
        'install': 'pip install together',
        'check_import': 'together'
    },
    {
        'name': 'llamaindex',
        'test_script': 'llamaindex_test.py',
        'install': 'pip install llama-index',
        'check_import': 'llama_index'
    },
    {
        'name': 'crewai',
        'test_script': 'crewai_test.py',
        'install': 'pip install crewai',
        'check_import': 'crewai'
    },
    {
        'name': 'ollama',
        'test_script': 'ollama_test.py',
        'install': 'pip install ollama',
        'check_import': 'ollama'
    },
]

def check_framework_installed(framework):
    """Check if framework is installed"""
    try:
        if '.' in framework['check_import']:
            # Handle dotted imports like google.generativeai
            parts = framework['check_import'].split('.')
            __import__(parts[0])
        else:
            __import__(framework['check_import'])
        return True
    except ImportError:
        return False

def test_framework(framework):
    """Test a single framework"""
    test_script = TESTS_DIR / framework['test_script']
    
    if not test_script.exists():
        return {'installed': False, 'error': 'Test script not found'}
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0 and "SUCCESS" in result.stdout
        
        return {
            'installed': True,
            'success': success,
            'output': result.stdout,
            'error': result.stderr if not success else None
        }
    except Exception as e:
        return {'installed': True, 'success': False, 'error': str(e)}

def main():
    """Main test runner"""
    print("="*60)
    print("Shadow AI Signature Collection - All Frameworks Test")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check which frameworks are available
    available = []
    not_installed = []
    
    for framework in FRAMEWORKS:
        if check_framework_installed(framework):
            available.append(framework)
        else:
            not_installed.append(framework)
    
    print(f"Found {len(available)} installed framework(s):")
    for fw in available:
        print(f"  [+] {fw['name']}")
    
    if not_installed:
        print(f"\n{len(not_installed)} framework(s) not installed:")
        for fw in not_installed:
            print(f"  [-] {fw['name']} - Install: {fw['install']}")
    
    if not available:
        print("\n[-] No frameworks installed!")
        print("\nInstall frameworks with:")
        for fw in FRAMEWORKS[:5]:  # Show first 5
            print(f"  {fw['install']}")
        return
    
    print("\n" + "="*60)
    print("Testing Frameworks...")
    print("="*60)
    
    results = []
    
    for framework in available:
        print(f"\nTesting {framework['name']}...")
        result = test_framework(framework)
        result['framework'] = framework['name']
        results.append(result)
        
        if result.get('success'):
            print(f"  [+] PASSED")
        else:
            print(f"  [-] FAILED")
            if result.get('error'):
                print(f"  Error: {result['error'][:100]}")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    for result in results:
        status = "[+] PASS" if result.get('success') else "[-] FAIL"
        print(f"{status} {result['framework']}")
    
    print(f"\nTotal: {passed}/{total} frameworks passed")
    
    if passed == total:
        print("\n[+] ALL FRAMEWORKS PASSED!")
    elif passed > 0:
        print(f"\n[!] {total - passed} framework(s) need attention")
    else:
        print("\n[-] No frameworks passed - check installations")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Install missing frameworks:")
    for fw in not_installed[:5]:
        print(f"   {fw['install']}")
    print("\n2. Run verification tests:")
    print("   python run_verification_tests.py")
    print("\n3. Update signature database")
    print("="*60)

if __name__ == "__main__":
    main()

