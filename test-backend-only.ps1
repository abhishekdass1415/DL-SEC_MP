# Test backend server only
Write-Host "=== Testing Backend Server Only ===" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment NOT found!" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    exit 1
}

Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host "API will be at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment and start backend
& ".\.venv\Scripts\python.exe" "backend\app.py"

