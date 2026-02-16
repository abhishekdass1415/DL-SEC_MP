# PowerShell script to start the backend server
Write-Host "Starting Threat Detection Backend Server..." -ForegroundColor Green
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Activate virtual environment
$VenvPath = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    & $VenvPath
} else {
    Write-Host "Warning: Virtual environment not found at $VenvPath" -ForegroundColor Yellow
    Write-Host "Make sure you have created a virtual environment first." -ForegroundColor Yellow
}

# Navigate to backend directory
Set-Location $ScriptDir

# Run the server
Write-Host "Starting Flask server on http://localhost:5000" -ForegroundColor Cyan
python app.py

