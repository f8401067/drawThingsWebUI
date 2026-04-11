@echo off
echo ========================================
echo   DrawThings WebUI - Startup Script
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import flask" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies
        echo Please try: python -m pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies already installed
)
echo.

REM Check if DrawThings is running
echo [INFO] Checking DrawThings service...
curl -s http://127.0.0.1:8777 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Cannot connect to DrawThings at 127.0.0.1:8777
    echo Please make sure DrawThings is running before using this application
    echo.
) else (
    echo [OK] DrawThings service is running
)
echo.

REM Start the Flask server
echo [INFO] Starting DrawThings WebUI server...
echo [INFO] Server will be available at: http://localhost:5000
echo [INFO] Press Ctrl+C to stop the server
echo.
python src/app.py

pause
