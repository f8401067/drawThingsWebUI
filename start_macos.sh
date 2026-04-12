#!/bin/bash

echo "========================================"
echo "  DrawThings WebUI - macOS Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ using Homebrew:"
    echo "  brew install python3"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not installed"
    echo "Please install pip for Python 3"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "[INFO] Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        echo "Please check your network connection and try again"
        exit 1
    fi
else
    echo "[OK] Dependencies already installed"
fi
echo ""

# Check if DrawThings is running
echo "[INFO] Checking DrawThings service..."
if curl -s http://127.0.0.1:8777 >/dev/null 2>&1; then
    echo "[OK] DrawThings service is running"
else
    echo "[WARNING] Cannot connect to DrawThings at 127.0.0.1:8777"
    echo "Please make sure DrawThings is running before using this application"
    echo ""
fi
echo ""

# Start the Flask server
echo "[INFO] Starting DrawThings WebUI server..."
echo "[INFO] Server will be available at: http://localhost:5001"
echo "[INFO] Press Ctrl+C to stop the server"
echo ""

# On macOS, we can optionally open the browser automatically
echo "[INFO] Opening browser in 3 seconds... (Press Ctrl+C to cancel)"
sleep 3 && open http://localhost:5000 &

python3 src/app.py