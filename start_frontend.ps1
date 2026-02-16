# PowerShell script to start the frontend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Threat Detection Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting frontend development server..." -ForegroundColor Green
npm run dev

