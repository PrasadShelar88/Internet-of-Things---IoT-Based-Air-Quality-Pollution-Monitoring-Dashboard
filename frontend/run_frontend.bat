@echo off
setlocal
cd /d "%~dp0"
title Air Quality Frontend - http://127.0.0.1:5500

echo ============================================================
echo IoT Air Quality Frontend
echo ============================================================
echo.
echo Frontend URL: http://127.0.0.1:5500
echo Backend URL : http://127.0.0.1:8000
echo.
echo IMPORTANT:
echo 1. Start backend first in a separate PowerShell window:
echo    cd "C:\Projects\IOT\Internet of Things - IoT-Based Air Quality ^& Pollution Monitoring Dashboard\air_quality_backend"
echo    .\run_backend.bat
echo.
echo 2. Keep this frontend window open while using dashboard.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    start "" "http://127.0.0.1:5500"
    py -3 -m http.server 5500 --bind 127.0.0.1
    goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" "http://127.0.0.1:5500"
    python -m http.server 5500 --bind 127.0.0.1
    goto end
)

echo Python was not found. Install Python or enable Python in PATH.
echo You can download Python from https://www.python.org/downloads/
pause

:end
endlocal
