# Add Wireshark to PATH
# Run this as Administrator if needed

$wiresharkPath = "C:\Program Files\Wireshark"

if (-not (Test-Path $wiresharkPath)) {
    Write-Host "[-] Wireshark not found at: $wiresharkPath" -ForegroundColor Red
    Write-Host "    Install Wireshark first" -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Found Wireshark at: $wiresharkPath" -ForegroundColor Green
Write-Host ""

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -like "*$wiresharkPath*") {
    Write-Host "[+] Wireshark already in PATH" -ForegroundColor Green
} else {
    Write-Host "[!] Adding Wireshark to PATH..." -ForegroundColor Yellow
    
    # Add to user PATH
    $newPath = $currentPath + ";$wiresharkPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    
    Write-Host "[+] Added to user PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: You may need to restart your terminal/PowerShell" -ForegroundColor Yellow
    Write-Host "      for the changes to take effect" -ForegroundColor Yellow
}

# Test
Write-Host ""
Write-Host "Testing tshark..." -ForegroundColor Cyan
$env:Path += ";$wiresharkPath"
try {
    $version = & "$wiresharkPath\tshark.exe" --version | Select-Object -First 1
    Write-Host "[+] $version" -ForegroundColor Green
    Write-Host ""
    Write-Host "[+] Wireshark is ready to use!" -ForegroundColor Green
} catch {
    Write-Host "[-] Could not run tshark" -ForegroundColor Red
    Write-Host "    Try restarting your terminal" -ForegroundColor Yellow
}

