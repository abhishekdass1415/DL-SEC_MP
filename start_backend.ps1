# PowerShell script to start the backend server from project root
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Threat Detection Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BackendDir = Join-Path $PSScriptRoot "backend"
Set-Location $BackendDir
& .\start_server.ps1

