# Shadow AI Detection: JA4 Network Fingerprinting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A production-ready system for detecting unauthorized AI agent usage in enterprise networks using JA4 TLS fingerprinting. This project provides tools, signatures, and deployment guides for identifying Shadow AI through network-layer analysis.

## 🎯 Overview

Shadow AI—unauthorized AI tools installed by employees—represents a critical security blind spot. Traditional security tools fail because:
- Traffic is encrypted (TLS 1.3)
- AI agents run locally (no cloud API calls)
- Traffic appears identical to normal HTTPS

**This project solves the problem** by fingerprinting TLS Client Hello packets using JA4 signatures. Every AI framework has a unique, unforgeable signature based on its underlying TLS library.

## ✨ Features

- **Complete JA4 Signature Database**: Tested signatures for 24+ AI frameworks
- **Production-Ready Scripts**: Automated capture, analysis, and detection tools
- **Multi-Platform Support**: Python, Zeek, Suricata, and eBPF implementations
- **Comprehensive Testing**: Test scripts for major AI frameworks (OpenAI, Anthropic, LangChain, etc.)
- **Real-World Validated**: Signatures extracted from actual packet captures

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt

# Optional: For packet capture
# - Wireshark/tshark (for PCAP analysis)
# - tcpdump (for network capture)
```

### Basic Usage

```bash
# 1. Test a framework and capture TLS handshake
python tests/openai_test.py

# 2. Extract JA4 signature from PCAP
python scripts/ja4_calculator.py pcaps/openai_*.pcap

# 3. Validate against signature database
python validate_signatures.py
```

### Automated Framework Testing

```bash
# Test all frameworks
python test_all_frameworks.py

# Capture all frameworks
python capture_all_frameworks.py

# Extract all signatures
python extract_ja4_from_pcaps.py
```

## 📁 Project Structure

```
.
├── scripts/              # Core utilities
│   ├── ja4_calculator.py      # JA4 extraction from PCAPs
│   ├── ja4-official/         # Official JA4 implementation (FoxIO)
│   └── test_framework.sh      # Framework testing automation
├── tests/                # Framework test scripts
│   ├── openai_test.py
│   ├── anthropic_test.py
│   ├── langchain_test.py
│   └── ... (24+ frameworks)
├── signatures/           # Signature database
│   ├── signature_database.csv
│   └── TEMPLATE.md
├── pcaps/               # Packet captures (gitignored)
├── logs/                # Test logs (gitignored)
└── requirements.txt     # Python dependencies
```

## 🔍 How It Works

1. **Capture**: Monitor TLS handshakes on port 443
2. **Fingerprint**: Extract JA4 signature from Client Hello packet
3. **Match**: Compare against signature database
4. **Alert**: Generate detection alerts for known AI frameworks

### Example JA4 Signature

```
t13d1516h2_7da4a31414f2_c1f7128d93bc
│ │ │ │ │  │              │
│ │ │ │ │  │              └─ JA4C (cipher suites hash)
│ │ │ │ │  └─ JA4B (extensions hash)
│ │ │ │ └─ JA4A (TLS version + SNI + ALPN)
│ │ │ └─ Supported groups
│ │ └─ Signature algorithms
│ └─ TLS version
└─ Packet direction
```

## 📊 Signature Database

The signature database (`signatures/signature_database.csv`) contains:

- Framework name and version
- JA4 fingerprint
- HTTP library used
- Verification runs (consistency checks)
- Detection rate
- False positive rate

### Current Coverage

✅ **24 Frameworks Tested:**
- OpenAI SDK
- Anthropic SDK
- LangChain
- AutoGPT
- CrewAI
- Ollama
- Haystack
- LlamaIndex
- And 16 more...

## 🛠️ Deployment Options

### Option 1: Zeek Integration

```bash
# Copy Zeek scripts
cp -r scripts/ja4-official/zeek/* /opt/zeek/share/zeek/site/

# Configure Zeek
echo '@load ja4' >> /opt/zeek/share/zeek/site/local.zeek

# Monitor and detect
zeek -i eth0 ja4
```

### Option 2: Python Scripts

```python
from scripts.ja4_calculator import extract_ja4_from_pcap

signatures = extract_ja4_from_pcap('capture.pcap')
for sig in signatures:
    if is_shadow_ai(sig):
        alert(f"Shadow AI detected: {sig}")
```

### Option 3: Suricata Rules

See `scripts/ja4-official/` for Suricata integration examples.

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)**: Get up and running in minutes
- **[Signature Database](signatures/signature_database.csv)**: Complete list of tested signatures
- **[Test Templates](tests/TEMPLATE_python.py)**: Add support for new frameworks

## 🧪 Testing

```bash
# Run all framework tests
python test_all_frameworks.py

# Run verification tests
python run_verification_tests.py

# Validate signature database
python validate_signatures.py
```

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding a New Framework

1. Create test script: `tests/[framework]_test.py`
2. Run test and capture: `python tests/[framework]_test.py`
3. Extract signature: `python scripts/ja4_calculator.py pcaps/[framework]_*.pcap`
4. Update database: Add entry to `signatures/signature_database.csv`

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

**Note**: The `scripts/ja4-official/` directory contains the official JA4 implementation by [FoxIO](https://foxio.io/), which has its own licensing terms. See `scripts/ja4-official/LICENSE` for details.

## 🙏 Acknowledgments

- **FoxIO** for the JA4 fingerprinting methodology
- **Open source community** for framework testing and validation
- **Enterprise security teams** who provided real-world testing scenarios

## 📧 Contact

For questions, issues, or contributions:
- Open an issue on GitHub
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

## 🔗 Related Resources

- [JA4+ Network Fingerprinting](https://blog.foxio.io/ja4%2B-network-fingerprinting) - Official JA4 documentation
- [JA4+ Cheat Sheet](https://x.com/4A4133/status/1887269972545839559) - Quick reference
- [Shadow AI Detection Book](https://github.com/yourusername/shadow-ai-book) - Comprehensive guide (coming soon)

---

**⚠️ Security Notice**: This tool is for authorized security testing and monitoring only. Ensure you have proper authorization before monitoring network traffic.
