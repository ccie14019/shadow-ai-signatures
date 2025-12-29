# Wireshark Installation Guide for Windows
# This script helps download and install Wireshark

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Wireshark Installation Guide" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
$wiresharkPath = "C:\Program Files\Wireshark\tshark.exe"
if (Test-Path $wiresharkPath) {
    Write-Host "[+] Wireshark is already installed!" -ForegroundColor Green
    Write-Host "    Location: $wiresharkPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Checking version..." -ForegroundColor Cyan
    & $wiresharkPath --version | Select-Object -First 1
    exit 0
}

Write-Host "[!] Wireshark not found" -ForegroundColor Yellow
Write-Host ""
Write-Host "Installation Steps:" -ForegroundColor Cyan
Write-Host "1. Download Wireshark from: https://www.wireshark.org/download.html" -ForegroundColor White
Write-Host "2. Run the installer (Wireshark-win64-X.X.X.exe)" -ForegroundColor White
Write-Host "3. During installation:" -ForegroundColor White
Write-Host "   - Accept the license" -ForegroundColor Gray
Write-Host "   - Choose installation location (default is fine)" -ForegroundColor Gray
Write-Host "   - IMPORTANT: Check 'Install TShark' option" -ForegroundColor Yellow
Write-Host "   - Choose components (default is fine)" -ForegroundColor Gray
Write-Host "   - Complete installation" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Add to PATH (if not automatically added):" -ForegroundColor White
Write-Host "   - Open: System Properties > Environment Variables" -ForegroundColor Gray
Write-Host "   - Edit 'Path' variable" -ForegroundColor Gray
Write-Host "   - Add: C:\Program Files\Wireshark" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Verify installation:" -ForegroundColor White
Write-Host "   tshark --version" -ForegroundColor Gray
Write-Host ""

# Check if we can open the download page
$openBrowser = Read-Host "Would you like to open the Wireshark download page? (Y/N)"
if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
    Start-Process "https://www.wireshark.org/download.html"
    Write-Host ""
    Write-Host "[+] Opened download page in browser" -ForegroundColor Green
}

Write-Host ""
Write-Host "After installation, run this script again to verify." -ForegroundColor Cyan
Write-Host "Or run: python verify_wireshark.py" -ForegroundColor Cyan

