# Installing Wireshark for Full JA4 Calculation

## Quick Installation Guide

### Windows Installation

1. **Download Wireshark:**
   - Go to: https://www.wireshark.org/download.html
   - Download Windows installer (64-bit)
   - File: `Wireshark-win64-X.X.X.exe`

2. **Install:**
   - Run the installer
   - Accept defaults (or customize)
   - **Important:** Make sure "Install TShark" is checked
   - Complete installation

3. **Add to PATH:**
   - Wireshark usually installs to: `C:\Program Files\Wireshark\`
   - Add to Windows PATH:
     - Open: System Properties → Environment Variables
     - Edit "Path" variable
     - Add: `C:\Program Files\Wireshark`
     - Click OK

4. **Verify Installation:**
   ```powershell
   tshark --version
   ```
   Should show: `TShark (Wireshark) X.X.X`

### Alternative: Use Improved Calculator (No Installation)

If you don't want to install Wireshark right now, use the improved calculator:

```bash
python scripts/ja4_improved.py pcaps/*.pcap
```

This provides better signatures than simplified version, but still not full JA4 spec.

## After Installation

### Calculate Full JA4

Once tshark is installed:

```bash
# Calculate JA4 for all PCAPs
python scripts/ja4-official/python/ja4.py pcaps/openai_*.pcap --ja4 -J

# Or process all at once
python scripts/ja4-official/python/ja4.py pcaps/*.pcap --ja4 -J > signatures/all_ja4.json
```

### Update Database

```bash
# Extract and update
python update_database_with_ja4.py
```

## Recommendation

**Option 1: Install Wireshark (Best Quality)**
- Full JA4 signatures
- Production-ready
- Takes 10-15 minutes to install

**Option 2: Use Improved Calculator (Quick)**
- Better than simplified
- Works immediately
- Not full JA4 spec

**Option 3: Continue with Current**
- Simplified signatures work
- Can refine later
- Focus on testing more frameworks

---

**Your choice!** The system works either way.
