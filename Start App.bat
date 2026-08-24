@echo off
setlocal enabledelayedexpansion
title Weather MCP Server - Launcher
cd /d "%~dp0"

echo ===================================================================
echo   Weather MCP Server - Windows Launcher (Was made by Oleh Datsyk)
echo ===================================================================
echo.

REM ---------------------------------------------------------------
REM 1. Verify Python is installed
REM ---------------------------------------------------------------
echo [1/6] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python was not found on your system, or it is not
    echo         added to your PATH.
    echo.
    echo         Please install Python 3.12 or newer from:
    echo         https://www.python.org/downloads/
    echo.
    echo         IMPORTANT: During installation, tick the box that says
    echo         "Add python.exe to PATH" before clicking Install.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo       Found Python %PY_VERSION%
echo.

REM ---------------------------------------------------------------
REM 2. Create virtual environment if it doesn't exist
REM ---------------------------------------------------------------
echo [2/6] Checking for virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo       No virtual environment found. Creating one now...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create the virtual environment.
        pause
        exit /b 1
    )
    echo       Virtual environment created.
) else (
    echo       Virtual environment already exists.
)
echo.

REM ---------------------------------------------------------------
REM 3. Activate the virtual environment
REM ---------------------------------------------------------------
echo [3/6] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate the virtual environment.
    pause
    exit /b 1
)
echo       Activated.
echo.

REM ---------------------------------------------------------------
REM 4. Install missing dependencies
REM ---------------------------------------------------------------
echo [4/6] Checking dependencies (this may take a moment on first run)...
python -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)
echo       Dependencies are up to date.
echo.

REM ---------------------------------------------------------------
REM 5. Verify the .env file
REM ---------------------------------------------------------------
echo [5/6] Checking for .env configuration file...
if not exist ".env" (
    echo.
    echo [WARNING] No .env file was found in this folder.
    echo           The server will start, but weather tools will not
    echo           work until you create a .env file with your
    echo           OpenWeatherMap API key.
    echo.
    echo           See INSTRUCTION.md, section 10, for details.
    echo.
) else (
    echo       .env file found.
)
echo.

REM ---------------------------------------------------------------
REM 6. Launch the application
REM ---------------------------------------------------------------
echo [6/6] Starting Weather MCP Server...
echo ================================================================
echo.
python server.py
set EXIT_CODE=%errorlevel%

echo.
echo ================================================================
if not "%EXIT_CODE%"=="0" (
    echo   The server exited with an error ^(code %EXIT_CODE%^).
    echo   Review the messages above for details.
) else (
    echo   The server has stopped.
)
echo ================================================================
echo.
pause
