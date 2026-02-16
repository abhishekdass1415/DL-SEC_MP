# Test frontend server only
Write-Host "=== Testing Frontend Server Only ===" -ForegroundColor Cyan
Write-Host ""

# Check if dependencies are installed
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "Starting frontend server..." -ForegroundColor Yellow
Write-Host "Open: http://localhost:5173" -ForegroundColor Green
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npm run dev

