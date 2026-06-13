@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo Air Quality Backend - FastAPI
echo ===============================================
echo.

set "PYTHON_CMD="
py -3.10 --version >nul 2>nul && set "PYTHON_CMD=py -3.10"
if not defined PYTHON_CMD py -3 --version >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD python --version >nul 2>nul && set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    echo ERROR: Python is not installed or not added to PATH.
    echo Install Python 3.10, then run this file again.
    pause
    exit /b 1
)

echo Using Python command: %PYTHON_CMD%

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment.
    pause
    exit /b 1
)

echo Installing backend requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Package installation failed.
    echo Check your internet connection, then run this file again.
    pause
    exit /b 1
)

echo.
echo Backend is starting at: http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs
echo Keep this window open while using the dashboard.
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
