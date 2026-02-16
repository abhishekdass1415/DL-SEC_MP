# Diagnostic script to check server status
Write-Host "=== DL-SEC Server Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

# Check if ports are in use
Write-Host "Checking port availability..." -ForegroundColor Yellow
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
$port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

if ($port5173) {
    Write-Host "⚠️  Port 5173 (Frontend) is IN USE" -ForegroundColor Red
    Write-Host "   Process: $($port5173.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "✅ Port 5173 (Frontend) is AVAILABLE" -ForegroundColor Green
}

if ($port5000) {
    Write-Host "⚠️  Port 5000 (Backend) is IN USE" -ForegroundColor Red
    Write-Host "   Process: $($port5000.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "✅ Port 5000 (Backend) is AVAILABLE" -ForegroundColor Green
}

Write-Host ""

# Check if frontend dependencies are installed
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules\framer-motion") {
    Write-Host "✅ framer-motion installed" -ForegroundColor Green
} else {
    Write-Host "❌ framer-motion NOT installed" -ForegroundColor Red
    Write-Host "   Run: cd frontend && npm install" -ForegroundColor Yellow
}

if (Test-Path "frontend\node_modules\zustand") {
    Write-Host "✅ zustand installed" -ForegroundColor Green
} else {
    Write-Host "❌ zustand NOT installed" -ForegroundColor Red
}

if (Test-Path "frontend\node_modules\tailwindcss") {
    Write-Host "✅ tailwindcss installed" -ForegroundColor Green
} else {
    Write-Host "❌ tailwindcss NOT installed" -ForegroundColor Red
}

Write-Host ""

# Check if virtual environment exists
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment NOT found" -ForegroundColor Red
    Write-Host "   Create one with: python -m venv .venv" -ForegroundColor Yellow
}

Write-Host ""

# Check if backend dependencies are installed
Write-Host "Checking backend dependencies..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    $python = ".venv\Scripts\python.exe"
    $flaskCheck = & $python -c "import flask; print('installed')" 2>&1
    if ($flaskCheck -match "installed") {
        Write-Host "✅ Flask installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Flask NOT installed" -ForegroundColor Red
        Write-Host "   Run: .\.venv\Scripts\Activate.ps1 && pip install -r backend/requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Cannot check (virtual environment not found)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If dependencies are missing, install them" -ForegroundColor White
Write-Host "2. If ports are in use, close those applications" -ForegroundColor White
Write-Host "3. Run: npm start" -ForegroundColor White
Write-Host "4. Open: http://localhost:5173" -ForegroundColor White

