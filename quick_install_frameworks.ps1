# Quick Install Additional Frameworks
# Installs frameworks and runs tests

Write-Host "Installing frameworks..." -ForegroundColor Cyan

pip install stability-sdk
pip install gpt4all
pip install semantic-kernel
pip install langflow

Write-Host "`nInstallation complete. Run tests with:" -ForegroundColor Green
Write-Host "  python test_more_frameworks.py" -ForegroundColor Yellow

