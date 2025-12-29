# Quick Start Guide

## Local Testing (No VMs Required)

This guide shows you how to test the signature collection system locally without setting up VMs.

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Install test frameworks
pip install langchain langchain-openai openai anthropic
```

### Step 2: Run Test Runner

```bash
# Run the automated test runner
python3 test_runner.py
```

This will:
- Test framework installations
- Create mock PCAP files
- Generate logs
- Demonstrate the workflow

### Step 3: Validate Signatures

```bash
# Check signature database status
python3 validate_signatures.py
```

### Step 4: Test Individual Framework

```bash
# Test LangChain (example)
./scripts/test_framework.sh \
  "langchain" \
  "pip install langchain langchain-openai" \
  "./tests/langchain_test.py"
```

### Step 5: Calculate JA4 (if you have real PCAPs)

```bash
# Calculate JA4 from PCAP file
python3 scripts/ja4_calculator.py pcaps/langchain_*.pcap
```

## Production Testing (With Network Capture)

For actual signature collection with real network traffic:

### Prerequisites

1. **tcpdump** installed
2. **Network interface** with internet access
3. **AI frameworks** installed

### Workflow

1. **Run test with capture:**
   ```bash
   # Without MOCK_CAPTURE, it will use tcpdump
   ./scripts/test_framework.sh \
     "langchain" \
     "pip install langchain langchain-openai" \
     "./tests/langchain_test.py"
   ```

2. **Transfer PCAP to analysis station** (if using separate VM):
   ```bash
   scp pcaps/langchain_*.pcap user@monitoring-station:/opt/shadow-ai-research/pcaps/
   ```

3. **Calculate JA4:**
   ```bash
   python3 scripts/ja4_calculator.py pcaps/langchain_*.pcap
   ```

4. **Verify consistency** (run 3 times):
   - Run test again
   - Compare JA4 signatures
   - Should be identical

5. **Document signature:**
   - Copy `signatures/TEMPLATE.md` to `signatures/langchain.md`
   - Fill in results
   - Add to `signatures/signature_database.csv`

## Adding a New Framework

1. **Create test script:**
   ```bash
   cp tests/TEMPLATE_python.py tests/myframework_test.py
   # Edit the file with your framework's imports and API calls
   ```

2. **Test it:**
   ```bash
   python3 tests/myframework_test.py
   ```

3. **Run full test:**
   ```bash
   ./scripts/test_framework.sh \
     "myframework" \
     "pip install myframework" \
     "./tests/myframework_test.py"
   ```

4. **Document:**
   - Create signature record
   - Add to database

## Troubleshooting

### "No module named 'scapy'"
```bash
pip install scapy
```

### "tcpdump: permission denied"
```bash
# On Linux/Mac, use sudo
sudo ./scripts/test_framework.sh [args]

# Or set capabilities
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
```

### "No TLS handshakes captured"
- Verify test script makes HTTPS connection
- Check network interface name: `ip addr show`
- Update `INTERFACE` variable in test script

### Mock mode not working
```bash
export MOCK_CAPTURE=true
./scripts/test_framework.sh [args]
```

## Next Steps

1. Read the complete guide: `Shadow_AI_Signature_Collection_Complete_Guide.md`
2. Set up production VMs (if needed)
3. Test 30 frameworks as outlined in the guide
4. Build signature database
5. Deploy Zeek detection rules

## Support

See the troubleshooting section in the main guide document for detailed solutions.

