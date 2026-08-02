#!/bin/bash
# ================================================================
#   Weather MCP Server - macOS Launcher
#   Double-click this file in Finder to run it.
# ================================================================

# Always operate from the folder this script lives in.
cd "$(dirname "$0")" || exit 1

echo "================================================================"
echo "  Weather MCP Server - macOS Launcher"
echo "================================================================"
echo

# ---------------------------------------------------------------
# 1. Verify Python is installed
# ---------------------------------------------------------------
echo "[1/6] Checking for Python..."
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo
    echo "[ERROR] Python was not found on your system."
    echo
    echo "        Please install Python 3.12 or newer from:"
    echo "        https://www.python.org/downloads/"
    echo
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi

PY_VERSION="$($PYTHON_BIN --version 2>&1)"
echo "      Found $PY_VERSION"
echo

# ---------------------------------------------------------------
# 2. Create virtual environment if it doesn't exist
# ---------------------------------------------------------------
echo "[2/6] Checking for virtual environment..."
if [ ! -f ".venv/bin/python" ]; then
    echo "      No virtual environment found. Creating one now..."
    "$PYTHON_BIN" -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create the virtual environment."
        read -n 1 -s -r -p "Press any key to close this window..."
        exit 1
    fi
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists."
fi
echo

# ---------------------------------------------------------------
# 3. Activate the virtual environment
# ---------------------------------------------------------------
echo "[3/6] Activating virtual environment..."
# shellcheck disable=SC1091
source ".venv/bin/activate"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate the virtual environment."
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi
echo "      Activated."
echo

# ---------------------------------------------------------------
# 4. Install missing dependencies
# ---------------------------------------------------------------
echo "[4/6] Checking dependencies (this may take a moment on first run)..."
python -m pip install --disable-pip-version-check -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies from requirements.txt."
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
fi
echo "      Dependencies are up to date."
echo

# ---------------------------------------------------------------
# 5. Verify the .env file
# ---------------------------------------------------------------
echo "[5/6] Checking for .env configuration file..."
if [ ! -f ".env" ]; then
    echo
    echo "[WARNING] No .env file was found in this folder."
    echo "          The server will start, but weather tools will not"
    echo "          work until you create a .env file with your"
    echo "          OpenWeatherMap API key."
    echo
    echo "          See INSTRUCTION.md, section 10, for details."
    echo
else
    echo "      .env file found."
fi
echo

# ---------------------------------------------------------------
# 6. Launch the application
# ---------------------------------------------------------------
echo "[6/6] Starting Weather MCP Server..."
echo "================================================================"
echo
python server.py
EXIT_CODE=$?

echo
echo "================================================================"
if [ $EXIT_CODE -ne 0 ]; then
    echo "  The server exited with an error (code $EXIT_CODE)."
    echo "  Review the messages above for details."
else
    echo "  The server has stopped."
fi
echo "================================================================"
echo
read -n 1 -s -r -p "Press any key to close this window..."
