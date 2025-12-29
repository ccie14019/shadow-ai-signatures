#!/bin/bash
# Framework Testing Automation Script
# Usage: ./test_framework.sh <framework_name> <install_command> <test_script>

set -e  # Exit on any error

# Configuration
FRAMEWORK_NAME=$1
INSTALL_CMD=$2
TEST_SCRIPT=$3
CAPTURE_DIR="pcaps"
LOG_DIR="logs"
DATE=$(date +%Y%m%d_%H%M%S)

# For local testing, we'll use a mock capture method
# In production, this would use tcpdump
MOCK_CAPTURE=${MOCK_CAPTURE:-false}

# Validate inputs
if [ -z "$FRAMEWORK_NAME" ] || [ -z "$INSTALL_CMD" ] || [ -z "$TEST_SCRIPT" ]; then
    echo "Usage: $0 <framework_name> <install_command> <test_script>"
    echo ""
    echo "Example:"
    echo "  $0 langchain 'pip install langchain langchain-openai' ./tests/langchain_test.py"
    exit 1
fi

echo "========================================="
echo "Shadow AI Signature Collection"
echo "Framework: $FRAMEWORK_NAME"
echo "Date: $(date)"
echo "========================================="
echo ""

# Step 1: Clean environment
echo "[1/7] Cleaning environment..."
# Remove any previous installations (optional)
# pip uninstall -y $FRAMEWORK_NAME 2>/dev/null || true

# Step 2: Install framework
echo "[2/7] Installing $FRAMEWORK_NAME..."
eval "$INSTALL_CMD" || {
    echo "  ✗ Installation failed"
    exit 1
}
echo "  ✓ Installation complete"
echo ""

# Step 3: Record version info
echo "[3/7] Recording version information..."
LOG_FILE="$LOG_DIR/${FRAMEWORK_NAME}_${DATE}.log"
mkdir -p "$LOG_DIR"

echo "=== Test Information ===" > "$LOG_FILE"
echo "Framework: $FRAMEWORK_NAME" >> "$LOG_FILE"
echo "Date: $(date)" >> "$LOG_FILE"
echo "Test Script: $TEST_SCRIPT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "=== System Information ===" >> "$LOG_FILE"
uname -a >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "=== Python Version ===" >> "$LOG_FILE"
python3 --version >> "$LOG_FILE" 2>&1 || echo "N/A" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "=== Installed Packages ===" >> "$LOG_FILE"
if command -v pip3 &> /dev/null; then
    pip3 list >> "$LOG_FILE" 2>&1 || true
fi
if command -v npm &> /dev/null; then
    npm list -g --depth=0 >> "$LOG_FILE" 2>&1 || true
fi
echo "" >> "$LOG_FILE"

echo "  ✓ Version info logged to $LOG_FILE"
echo ""

# Step 4: Start packet capture
echo "[4/7] Starting packet capture..."
mkdir -p "$CAPTURE_DIR"
PCAP_FILE="$CAPTURE_DIR/${FRAMEWORK_NAME}_${DATE}.pcap"

if [ "$MOCK_CAPTURE" = "true" ]; then
    echo "  ℹ Using mock capture mode (for local testing)"
    echo "  ℹ In production, this would use tcpdump"
    # Create a placeholder PCAP file
    touch "$PCAP_FILE"
    echo "  ✓ Mock capture file created: $PCAP_FILE"
else
    # Check if tcpdump is available
    if command -v tcpdump &> /dev/null; then
        # Try to detect network interface
        INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
        if [ -z "$INTERFACE" ]; then
            INTERFACE="eth0"
        fi
        
        echo "  ℹ Using interface: $INTERFACE"
        echo "  ℹ Starting tcpdump capture..."
        
        # Start tcpdump in background (requires sudo in production)
        sudo tcpdump -i "$INTERFACE" 'tcp port 443' -w "$PCAP_FILE" -c 50 > /dev/null 2>&1 &
        TCPDUMP_PID=$!
        sleep 3
        echo "  ✓ Capture started (PID: $TCPDUMP_PID)"
    else
        echo "  ⚠ tcpdump not available, using mock mode"
        touch "$PCAP_FILE"
    fi
fi

echo "  ✓ Capturing to: $PCAP_FILE"
echo ""

# Step 5: Run test script
echo "[5/7] Running test script..."
echo "--- Test Output ---" >> "$LOG_FILE"

if python3 "$TEST_SCRIPT" >> "$LOG_FILE" 2>&1; then
    echo "  ✓ Test completed successfully"
else
    echo "  ⚠ Test had errors (check log file)"
fi
echo ""

# Step 6: Stop packet capture
echo "[6/7] Stopping capture..."
sleep 5  # Let any remaining packets be captured

if [ -n "$TCPDUMP_PID" ]; then
    sudo kill -TERM $TCPDUMP_PID 2>/dev/null || true
    sleep 2
fi

# Verify PCAP was created
if [ -f "$PCAP_FILE" ]; then
    if command -v tcpdump &> /dev/null && [ "$MOCK_CAPTURE" != "true" ]; then
        PACKET_COUNT=$(tcpdump -r "$PCAP_FILE" 2>/dev/null | wc -l || echo "0")
        echo "  ✓ Captured $PACKET_COUNT packets"
        
        # Check for TLS Client Hello
        if command -v tshark &> /dev/null; then
            TLS_COUNT=$(tshark -r "$PCAP_FILE" -Y 'tls.handshake.type == 1' 2>/dev/null | wc -l || echo "0")
            echo "  ✓ Found $TLS_COUNT TLS Client Hello packet(s)"
            
            if [ "$TLS_COUNT" -eq 0 ]; then
                echo "  ⚠ WARNING: No TLS handshakes captured!"
                echo "  ⚠ Test may have failed to generate HTTPS traffic"
            fi
        fi
    else
        echo "  ℹ PCAP file created (mock mode - no actual capture)"
        echo "  ℹ In production, transfer this to monitoring station for JA4 calculation"
    fi
else
    echo "  ✗ ERROR: PCAP file not created"
    exit 1
fi
echo ""

# Step 7: Summary
echo "[7/7] Test complete!"
echo ""
echo "========================================="
echo "Results"
echo "========================================="
echo "PCAP File:    $PCAP_FILE"
echo "Log File:     $LOG_FILE"
echo ""
echo "Next Steps:"
echo "1. If using mock mode, generate actual PCAP with real traffic"
echo "2. Calculate JA4 signature:"
echo "   python3 scripts/ja4_calculator.py $PCAP_FILE"
echo ""
echo "3. Run this test 2 more times to verify consistency"
echo "========================================="

