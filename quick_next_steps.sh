#!/bin/bash
# Quick Next Steps - Automated Scripts

echo "========================================="
echo "Shadow AI - Quick Next Steps"
echo "========================================="
echo ""

echo "1. Install Wireshark for full JA4 calculation"
echo "   Download: https://www.wireshark.org/download.html"
echo ""

echo "2. Calculate JA4 signatures:"
echo "   python scripts/ja4-official/python/ja4.py pcaps/*.pcap --ja4 -J"
echo ""

echo "3. Test more frameworks:"
echo "   python test_all_frameworks.py"
echo ""

echo "4. Capture traffic:"
echo "   python capture_all_frameworks.py"
echo ""

echo "5. Update database:"
echo "   python update_database_with_signatures.py"
echo ""

echo "6. Validate results:"
echo "   python validate_signatures.py"
echo ""

echo "========================================="

