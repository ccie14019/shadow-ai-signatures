# [Framework Name] - JA4 Signature Record

## Framework Information
- **Name:** [Full framework name]
- **Version:** [x.y.z]
- **Type:** [Python/JavaScript/Go/Rust/etc]
- **Repository:** [GitHub URL]
- **Documentation:** [Official docs URL]
- **PyPI/npm:** [Package manager link]

## Test Environment
- **OS:** Ubuntu 22.04 LTS (or Windows/macOS for local testing)
- **Kernel:** [uname -r output]
- **Python Version:** [if applicable]
- **Node.js Version:** [if applicable]
- **Go Version:** [if applicable]
- **Test Date:** YYYY-MM-DD
- **Tested By:** [Your name]

## Installation Commands
```bash
[Exact installation command used]
```

**Installation Output:**
```
[Relevant output showing installed version]
```

## Dependencies Installed
```
[Output of pip list / npm list / go list]
[Only relevant packages, not entire system]
```

## Test Code
```python
[Exact test code that generated the traffic]
[Include all imports and configuration]
```

## Capture Details
- **PCAP File:** `framework_name_YYYYMMDD_HHMMSS.pcap`
- **Total Packets:** [count]
- **TLS Client Hellos:** [count]
- **Destination:** [api.example.com]
- **Destination Port:** 443
- **Capture Interface:** eth0 (or local mock)
- **Capture Duration:** ~10 seconds

## JA4 Signature

**Primary Signature:**
```
[Complete JA4 fingerprint string]
```

**Breakdown:**
- Protocol: [t13 = TLS 1.3, t12 = TLS 1.2, etc]
- SNI: [d = domain, i = IP]
- Cipher Count: [XX]
- Extension Count: [XX]
- ALPN: [h2 = HTTP/2, 00 = none]

## Verification Tests

| Run | Date | JA4 Signature | Match? |
|-----|------|---------------|--------|
| 1   | YYYY-MM-DD | [signature] | - |
| 2   | YYYY-MM-DD | [signature] | ✓/✗ |
| 3   | YYYY-MM-DD | [signature] | ✓/✗ |

**Consistency:** [3/3 = 100% | 2/3 = 67% | etc]

**Notes on Variations:**
[If signatures varied, explain why]

## TLS Handshake Details

**From tshark analysis:**
```bash
tshark -r [pcap_file] -Y 'tls.handshake.type == 1' -V
```

- **TLS Version:** [1.2 | 1.3]
- **Cipher Suites:** [Count and notable ciphers]
- **Extensions:** [Count and notable extensions]
- **ALPN Protocols:** [http/1.1, h2, etc]
- **Server Name (SNI):** [domain]

## HTTP Library Details

**Underlying HTTP library:**
- **Library:** [requests, aiohttp, httpx, urllib3, etc]
- **Version:** [x.y.z]
- **TLS Implementation:** [OpenSSL, etc]

## Zeek Detection Test

**Signature added to database:** YYYY-MM-DD

**Test Results:**
- Test traffic generated: [X] connections
- Detected by Zeek: [X]/[X]
- Detection rate: [XX]%
- False positives in benign traffic: [X]/[100]
- False positive rate: [X]%

**Zeek log sample:**
```
[Sample lines from shadow_ai.log showing detection]
```

## Version Testing

Tested multiple versions to understand signature stability:

| Version | JA4 Signature | Notes |
|---------|---------------|-------|
| [x.y.z] | [signature]   | Initial version tested |
| [x.y.z] | [signature]   | [Same/Different, why?] |

## Known Issues / Notes

[Any special observations:]
- Does signature change with different Python versions?
- Any certificate pinning that affects capture?
- Any unusual TLS behavior?
- Does it support HTTP/2, HTTP/3?

## Related Signatures

**Similar to:**
- [Other framework] - Same underlying HTTP library

**Different from:**
- [Other framework] - Different cipher preference

## File Locations

- **PCAP Files:** 
  - Run 1: `pcaps/[framework]_run1.pcap`
  - Run 2: `pcaps/[framework]_run2.pcap`
  - Run 3: `pcaps/[framework]_run3.pcap`

- **Log File:** `logs/[framework]_YYYYMMDD.log`

- **Test Script:** `tests/[framework]_test.py`

## Production Deployment Notes

[Recommendations for using this signature in production:]
- Confidence level: [High/Medium/Low]
- Recommended alert threshold: [First detection / Multiple detections]
- Known false positive sources: [None / List]

---

**Signature Validated By:** [Your name]  
**Date:** YYYY-MM-DD

