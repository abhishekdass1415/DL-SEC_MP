# Manual server startup script
Write-Host "=== Starting DL-SEC Servers Manually ===" -ForegroundColor Cyan
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "❌ Frontend dependencies NOT installed!" -ForegroundColor Red
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Frontend dependencies found" -ForegroundColor Green
}

Write-Host ""

# Check virtual environment
Write-Host "Checking backend setup..." -ForegroundColor Yellow
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment NOT found!" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r backend/requirements.txt" -ForegroundColor White
    exit 1
} else {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Starting Servers ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting both servers..." -ForegroundColor Yellow
Write-Host "Frontend will be at: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend will be at: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start both servers
npm start

