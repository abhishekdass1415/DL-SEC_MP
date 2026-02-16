@echo off
echo Starting Threat Detection Backend Server...
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Activate virtual environment
call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"

REM Navigate to backend directory
cd /d "%SCRIPT_DIR%"

REM Run the server
python app.py

pause

