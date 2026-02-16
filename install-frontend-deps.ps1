# Install Frontend Dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location frontend
npm install
Write-Host "`nDependencies installed successfully!" -ForegroundColor Green
Set-Location ..
Write-Host "`nYou can now start the server with: npm start" -ForegroundColor Yellow

