@echo off
echo ========================================
echo   Threat Detection Frontend
echo ========================================
echo.

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo Starting frontend development server...
call npm run dev

pause

